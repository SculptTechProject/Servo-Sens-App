from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from core.models import Workspace, Reading, Sensor
from .serializers import WorkspaceTopologySerializer, LatestReadingSerializer
from django.db.models import OuterRef, Subquery

# ---------------- Health ----------------


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


@extend_schema(
    request=None, responses=HealthSerializer, description="Simple healthcheck."
)
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


# ---------------- Sim start/stop ----------------

SimStartResponse = inline_serializer(
    name="SimStartResponse", fields={"started": serializers.BooleanField()}
)
SimStopResponse = inline_serializer(
    name="SimStopResponse", fields={"stopped": serializers.BooleanField()}
)


@extend_schema(
    request=None,
    responses=SimStartResponse,
    description="Start simulator for workspace.",
)
class SimStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        # pilnuj właściciela zanim odpalisz symulator
        get_object_or_404(Workspace, pk=pk, owner=request.user)
        from .services import start_sim

        return Response({"started": start_sim(pk)})


@extend_schema(
    request=None,
    responses=SimStopResponse,
    description="Stop simulator for workspace.",
)
class SimStopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        get_object_or_404(Workspace, pk=pk, owner=request.user)
        from .services import stop_sim

        return Response({"stopped": stop_sim(pk)})


# ---------------- Topology ----------------


@extend_schema(
    request=None,
    responses=WorkspaceTopologySerializer,
    description="Return machines + sensors topology for a workspace.",
    examples=[
        OpenApiExample(
            "Sample",
            value={
                "workspace": {"id": 2, "name": "Workspace #2"},
                "machines": [
                    {
                        "id": 7,
                        "name": "Motor A",
                        "kind": "motor",
                        "x": 120,
                        "y": 80,
                        "sensors": [
                            {
                                "id": 12,
                                "name": "Temperature #12",
                                "kind": "temperature",
                                "unit": "°C",
                                "threshold": 80.0,
                                "machine": {
                                    "id": 7,
                                    "name": "Motor A",
                                    "kind": "motor",
                                    "x": 120,
                                    "y": 80,
                                },
                            }
                        ],
                    }
                ],
                "sensors": [
                    {
                        "id": 12,
                        "name": "Temperature #12",
                        "kind": "temperature",
                        "unit": "°C",
                        "threshold": 80.0,
                        "machine": {
                            "id": 7,
                            "name": "Motor A",
                            "kind": "motor",
                            "x": 120,
                            "y": 80,
                        },
                    }
                ],
            },
        )
    ],
)
class WorkspaceTopologyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        ws = get_object_or_404(Workspace, pk=pk, owner=request.user)
        data = WorkspaceTopologySerializer(ws).data
        return Response(data, status=status.HTTP_200_OK)


class LatestReadingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        ws = get_object_or_404(Workspace, pk=pk, owner=request.user)

        latest = Reading.objects.filter(sensor=OuterRef("pk")).order_by("-ts")
        qs = (
            Sensor.objects.filter(machine__workspace=ws)
            .select_related("machine")
            .annotate(
                last_value=Subquery(latest.values("value")[:1]),
                last_ts=Subquery(latest.values("ts")[:1]),
            )
        )

        payload = []
        for s in qs:
            payload.append(
                {
                    "sensor_id": s.id,
                    "value": s.last_value,
                    "unit": s.unit,
                    "ts": s.last_ts,
                    "name": f"{s.kind.title()} #{s.id}",
                    "machine": s.machine.name if s.machine else None,
                    "threshold": s.threshold,
                }
            )

        return Response(LatestReadingSerializer(payload, many=True).data)
