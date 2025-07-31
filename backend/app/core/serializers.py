from rest_framework import serializers
from .models import Workspace, Machine, Sensor, Event, Reading


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("id", "name")


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ("id", "name", "kind", "x", "y", "workspace")


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ("id", "kind", "unit", "threshold", "machine")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("machine"):
            raise serializers.ValidationError(
                {"machine": "Sensor musi być przypisany do maszyny."}
            )
        return super().validate(attrs)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "ts", "level", "message", "sensor", "workspace")


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = ("id", "ts", "value", "sensor")
