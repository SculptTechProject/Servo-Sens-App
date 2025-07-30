from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Workspace, Machine, Sensor


class Command(BaseCommand):
    help = "Seed demo workspace/machine/sensor"

    def handle(self, *args, **opts):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email="demo@example.com", defaults={"name": "Demo"}
        )
        user.set_password("demo123")
        user.save()

        ws, _ = Workspace.objects.get_or_create(owner=user, name="Hala A")
        m, _ = Machine.objects.get_or_create(
            workspace=ws, name="Silnik #1", kind="motor"
        )
        Sensor.objects.get_or_create(
            machine=m, kind="temperature", unit="°C", threshold=75
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed OK. User: demo@example.com / demo123, workspace_id={ws.id}"
            )
        )
