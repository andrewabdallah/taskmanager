from django.contrib import admin
from .models.task import Task
# Register your models here.



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "priority", "due_date", "created_at", "updated_at")
    list_filter = ("status", "priority", "due_date", "created_at", "updated_at")
    search_fields = ("title", "description", "owner__username")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")