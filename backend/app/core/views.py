from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Workspace, Machine, Sensor
from .serializers import WorkspaceSerializer, MachineSerializer, SensorSerializer


class WorkspaceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(owner=self.request.user).annotate(
            machines_count=Count("machines", distinct=True),
            sensors_count=Count("machines__sensors", distinct=True),
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # ---- helpers ----
    def _seed_ws(self, ws: Workspace) -> None:
        if not Sensor.objects.filter(machine__workspace=ws).exists():
            m = ws.machines.first() or Machine.objects.create(
                workspace=ws, name="Silnik #1", kind="motor", x=100, y=100
            )
            Sensor.objects.create(
                machine=m, kind="temperature", unit="°C", threshold=75
            )
            Sensor.objects.create(machine=m, kind="vibration", unit="mm/s", threshold=6)
            Sensor.objects.create(machine=m, kind="current", unit="A", threshold=12)

    @action(detail=True, methods=["post"])
    def seed(self, request, pk=None):
        ws = self.get_object()
        self._seed_ws(ws)
        data = self.get_queryset().get(pk=ws.pk)
        ser = self.get_serializer(data)
        return Response({"ok": True, **ser.data})

    @action(detail=False, methods=["post"])
    def quickstart(self, request):
        ws = self.get_queryset().first() or Workspace.objects.create(
            owner=request.user, name="MójWorkspace"
        )
        self._seed_ws(ws)
        data = self.get_queryset().get(pk=ws.pk)
        ser = self.get_serializer(data)
        return Response({"ok": True, **ser.data})


# ===== CRUD dla maszyn =====
class MachineViewSet(viewsets.ModelViewSet):
    """
    /api/core/machines/      GET, POST
    /api/core/machines/<id>/ GET, PATCH, PUT, DELETE
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get_queryset(self):
        # tylko maszyny należące do workspace'ów użytkownika
        return Machine.objects.filter(workspace__owner=self.request.user)

    def perform_create(self, serializer):
        ws_id = self.request.data.get("workspace")
        ws = get_object_or_404(Workspace, pk=ws_id, owner=self.request.user)
        serializer.save(workspace=ws)


# ===== CRUD dla sensorów =====
class SensorViewSet(viewsets.ModelViewSet):
    """
    /api/core/sensors/       GET, POST
    /api/core/sensors/<id>/  GET, PATCH, PUT, DELETE

    Uwaga: ponieważ Sensor ma FK tylko do Machine, dopuszczamy wyłącznie te,
    które należą do maszyn użytkownika. Tworzenie wymaga `machine`.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SensorSerializer

    def get_queryset(self):
        return Sensor.objects.filter(machine__workspace__owner=self.request.user)

    def perform_create(self, serializer):
        machine_id = self.request.data.get("machine")
        machine = get_object_or_404(
            Machine, pk=machine_id, workspace__owner=self.request.user
        )
        serializer.save(machine=machine)
