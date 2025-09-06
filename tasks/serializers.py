from rest_framework import serializers
from .models.task import Task
from datetime import date

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_priority(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Priority must be between 1 and 5.")
        return value

    def validate_due_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
