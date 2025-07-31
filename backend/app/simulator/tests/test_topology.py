from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from core.models import Workspace, Machine, Sensor

User = get_user_model()


class TopologyViewTests(APITestCase):
    def setUp(self):
        # użytkownicy
        self.user = User.objects.create_user(
            email="mati@example.com", password="pass123", name="Mati"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="pass123", name="Other"
        )

        # WS-y
        self.ws = Workspace.objects.create(owner=self.user, name="WS #1")
        self.ws_empty = Workspace.objects.create(owner=self.user, name="Empty WS")
        self.ws_foreign = Workspace.objects.create(owner=self.other, name="Foreign WS")

        # dane do ws
        m1 = Machine.objects.create(
            workspace=self.ws, name="Motor A", kind="motor", x=10, y=20
        )
        m2 = Machine.objects.create(
            workspace=self.ws, name="Pump B", kind="pump", x=200, y=160
        )

        Sensor.objects.create(machine=m1, kind="temperature", unit="°C", threshold=80)
        Sensor.objects.create(machine=m1, kind="current", unit="A")
        Sensor.objects.create(machine=m2, kind="vibration", unit="mm/s", threshold=12)

    def test_topology_happy_path(self):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:workspace-topology", args=[self.ws.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        body = res.json()
        self.assertIn("workspace", body)
        self.assertIn("machines", body)
        self.assertIn("sensors", body)
        self.assertEqual(body["workspace"]["id"], self.ws.id)
        self.assertEqual(len(body["machines"]), 2)
        self.assertEqual(len(body["sensors"]), 3)

        sensor = body["sensors"][0]
        self.assertTrue(
            {"id", "name", "kind", "unit", "threshold", "machine"} <= set(sensor.keys())
        )

    def test_topology_empty_workspace(self):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:workspace-topology", args=[self.ws_empty.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["machines"], [])
        self.assertEqual(body["sensors"], [])

    def test_topology_unauthenticated(self):
        url = reverse("simulator:workspace-topology", args=[self.ws.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)

    def test_topology_not_owner_404(self):
        self.client.force_authenticate(self.user)
        url = reverse("simulator:workspace-topology", args=[self.ws_foreign.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)
