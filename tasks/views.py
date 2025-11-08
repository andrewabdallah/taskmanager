from rest_framework import viewsets, permissions
from .models.task import Task
from .serializers import TaskSerializer
from core.permissions import IsOwner
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from core.decorators.cache_decorator import cache_api_call

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    @cache_api_call("user_id")
    def recent(self, request):
        """Cached endpoint for recent tasks"""
        queryset = self.get_queryset().order_by("-created_at")[:settings.RECENT_TASKS_COUNT]
        data = TaskSerializer(queryset, many=True).data
        return Response(data)