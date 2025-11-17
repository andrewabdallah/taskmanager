from datetime import date

from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_priority(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Priority must be between 1 and 5.")
        return value

    def validate_due_date(self, value):
        if value is None:
            raise serializers.ValidationError("Due date cannot be null.")
        if value and value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class TaskCSVSerializer(serializers.ModelSerializer):
    """
    Readonly serializer for exporting Task data in CSV format. including owner username
    """

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "due_date",
            "status",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
