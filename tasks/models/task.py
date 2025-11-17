from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel


class Task(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.PositiveSmallIntegerField(default=3)  # 1=High, 5=Low
    due_date = models.DateField()

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"
        db_table = "task"

    def __str__(self):
        return self.title
