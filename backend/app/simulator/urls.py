from django.urls import path
from .views import (
    HealthCheckView,
    SimStartView,
    SimStopView,
    WorkspaceTopologyView,
    LatestReadingsView,
)

app_name = "simulator"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("sim/start/<int:pk>/", SimStartView.as_view(), name="sim-start"),
    path("sim/stop/<int:pk>/", SimStopView.as_view(), name="sim-stop"),
    # **aliasy pod namespace: sim** -> /api/sim/start/<pk>/ i /api/sim/stop/<pk>/
    path("start/<int:pk>/", SimStartView.as_view(), name="start"),
    path("stop/<int:pk>/", SimStopView.as_view(), name="stop"),
    path(
        "workspaces/<int:pk>/topology/",
        WorkspaceTopologyView.as_view(),
        name="workspace-topology",
    ),
    path(
        "workspaces/<int:pk>/latest-readings/",
        LatestReadingsView.as_view(),
        name="latest-readings",
    ),
]
