from django.db.models import Count
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Workspace, Machine, Sensor
from .serializers import WorkspaceSerializer


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
        # jeżeli WS nie ma żadnego sensora -> twórz demo
        if not Sensor.objects.filter(machine__workspace=ws).exists():
            m = ws.machines.first() or Machine.objects.create(
                workspace=ws, name="Silnik #1", kind="motor"
            )
            Sensor.objects.create(
                machine=m, kind="temperature", unit="°C", threshold=75
            )
            Sensor.objects.create(machine=m, kind="vibration", unit="mm/s", threshold=6)
            Sensor.objects.create(machine=m, kind="current", unit="A", threshold=12)

    # ---- /api/workspaces/{id}/seed/ ----
    @action(detail=True, methods=["post"])
    def seed(self, request, pk=None):
        ws = self.get_object()
        self._seed_ws(ws)
        # zwróć zaktualizowane liczniki
        data = self.get_queryset().get(pk=ws.pk)
        ser = self.get_serializer(data)
        return Response({"ok": True, **ser.data})

    # ---- /api/workspaces/quickstart/ ----
    @action(detail=False, methods=["post"])
    def quickstart(self, request):
        # jeśli user ma już jakiś WS, użyj pierwszego; inaczej utwórz
        ws = self.get_queryset().first() or Workspace.objects.create(
            owner=request.user, name="MójWorkspace"
        )
        self._seed_ws(ws)
        data = self.get_queryset().get(pk=ws.pk)
        ser = self.get_serializer(data)
        return Response({"ok": True, **ser.data})
