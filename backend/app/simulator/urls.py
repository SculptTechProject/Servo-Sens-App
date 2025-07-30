from django.urls import path
from .views import SimStartView, SimStopView

app_name = "simulator"

urlpatterns = [
    path("start/<int:pk>/", SimStartView.as_view(), name="start"),
    path("stop/<int:pk>/", SimStopView.as_view(), name="stop"),
]
