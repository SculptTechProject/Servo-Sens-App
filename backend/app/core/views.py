from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Count
from core.models import Workspace
from .serializers import WorkspaceSerializer

class WorkspaceViewSet(ReadOnlyModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Workspace.objects
                .filter(owner=self.request.user)
                .annotate(machines_count=Count("machines")))
