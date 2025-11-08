import uuid

from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.PositiveSmallIntegerField(default=3)  # 1=High, 5=Low
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"
        db_table = "task"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["updated_at"], name="tsk_updated_at"),
        ]

    def __str__(self):
        return self.title
