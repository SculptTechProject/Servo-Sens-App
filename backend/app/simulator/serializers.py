from rest_framework import serializers
from core.models import Workspace, Machine, Sensor


class MachineMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ("id", "name", "kind", "x", "y")


class SensorTopoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    machine = MachineMiniSerializer(allow_null=True)

    def get_name(self, obj: Sensor) -> str:
        return f"{obj.kind.title()} #{obj.id}"

    class Meta:
        model = Sensor
        fields = ("id", "name", "kind", "unit", "threshold", "machine")


class MachineWithSensorsSerializer(serializers.ModelSerializer):
    sensors = SensorTopoSerializer(many=True)

    class Meta:
        model = Machine
        fields = ("id", "name", "kind", "x", "y", "sensors")


class WorkspaceTopologySerializer(serializers.Serializer):
    """
    Zwraca całą topologię workspace'u: maszyny + sensory.
    """

    def to_representation(self, ws: Workspace):
        machines = Machine.objects.filter(workspace=ws).prefetch_related("sensors")
        sensors = Sensor.objects.filter(machine__workspace=ws).select_related("machine")
        return {
            "workspace": {"id": ws.id, "name": ws.name},
            "machines": MachineWithSensorsSerializer(machines, many=True).data,
            "sensors": SensorTopoSerializer(sensors, many=True).data,
        }


class LatestReadingSerializer(serializers.Serializer):
    sensor_id = serializers.IntegerField()
    value = serializers.FloatField(allow_null=True)
    unit = serializers.CharField()
    ts = serializers.DateTimeField(allow_null=True)
    name = serializers.CharField()
    machine = serializers.CharField(allow_null=True)
    threshold = serializers.FloatField(allow_null=True)
