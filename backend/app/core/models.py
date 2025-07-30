"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings


class UserManager(BaseUserManager):
    """Manager for user"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email adress.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Workspace(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)


class Machine(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="machines"
    )
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=50, default="motor")  # typ: motor/pump/etc.
    x = models.IntegerField(default=100)  # pozycja na canvasie
    y = models.IntegerField(default=100)


class Sensor(models.Model):
    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, related_name="sensors", null=True, blank=True
    )
    SENSOR_KIND = (
        ("temperature", "temperature"),
        ("vibration", "vibration"),
        ("current", "current"),
    )
    kind = models.CharField(max_length=50, choices=SENSOR_KIND, default="temperature")
    unit = models.CharField(max_length=20, default="°C")
    threshold = models.FloatField(null=True, blank=True)


class Event(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="events"
    )
    ts = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, default="WARN")  # INFO/WARN/CRIT
    sensor = models.ForeignKey(Sensor, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.CharField(max_length=200)


class Reading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    ts = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
