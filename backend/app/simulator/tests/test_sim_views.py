from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch
from core.models import Workspace

User = get_user_model()


class SimViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="mati@example.com", password="pass123", name="Mati"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="pass123", name="Other"
        )
        self.ws = Workspace.objects.create(owner=self.user, name="WS #1")
        self.ws_foreign = Workspace.objects.create(owner=self.other, name="Foreign WS")

    @patch("simulator.services.start_sim", return_value=True)
    def test_sim_start_success(self, start_mock):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:sim-start", args=[self.ws.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"started": True})
        start_mock.assert_called_once_with(self.ws.id)

    @patch("simulator.services.stop_sim", return_value=True)
    def test_sim_stop_success(self, stop_mock):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:sim-stop", args=[self.ws.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"stopped": True})
        stop_mock.assert_called_once_with(self.ws.id)

    def test_sim_start_requires_auth(self):
        url = reverse("simulator:sim-start", args=[self.ws.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 401)

    @patch("simulator.services.start_sim", return_value=True)
    def test_sim_start_other_owner_404(self, _):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:sim-start", args=[self.ws_foreign.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)

    @patch("simulator.services.stop_sim", return_value=True)
    def test_sim_stop_other_owner_404(self, _):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:sim-stop", args=[self.ws_foreign.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)
