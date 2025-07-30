# simulator/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer

# Health
class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()

@extend_schema(
    request=None,
    responses=HealthSerializer,
    description="Simple healthcheck."
)
class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok"})

# Sim start/stop
SimStartResponse = inline_serializer(
    name="SimStartResponse",
    fields={"started": serializers.BooleanField()}
)
SimStopResponse = inline_serializer(
    name="SimStopResponse",
    fields={"stopped": serializers.BooleanField()}
)

@extend_schema(request=None, responses=SimStartResponse, description="Start simulator for workspace.")
class SimStartView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        from .services import start_sim
        return Response({"started": start_sim(pk)})

@extend_schema(request=None, responses=SimStopResponse, description="Stop simulator for workspace.")
class SimStopView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        from .services import stop_sim
        return Response({"stopped": stop_sim(pk)})
