from rest_framework import serializers
from core.models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    machines_count = serializers.IntegerField(read_only=True)
    sensors_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workspace
        fields = ["id", "name", "machines_count", "sensors_count"]
        read_only_fields = ["id", "machines_count", "sensors_count"]
