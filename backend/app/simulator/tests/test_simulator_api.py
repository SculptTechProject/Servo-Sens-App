"""
Tests simulator API endpoints.
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Workspace, Machine, Sensor, Reading


@override_settings(
    SIMULATOR_INLINE=True,
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
class SimApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "u@example.com", "pass123", name="U"
        )
        self.client.force_authenticate(self.user)
        self.ws = Workspace.objects.create(owner=self.user, name="W1")
        m = Machine.objects.create(workspace=self.ws, name="M1", kind="motor")
        self.s = Sensor.objects.create(
            machine=m, kind="temperature", unit="°C", threshold=70
        )

    def test_start_and_stop(self):
        url = reverse("sim:start", args=[self.ws.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["started"])

        import time

        time.sleep(1.2)
        self.assertTrue(Reading.objects.filter(sensor=self.s).exists())

        url = reverse("sim:stop", args=[self.ws.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["stopped"])
