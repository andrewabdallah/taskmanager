from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer

from core.decorators.cache_decorator import cache_api_call
from core.views import BaseMixin, BaseModelViewSet
from tasks.filters.task_filters import TasksRequestFilter
from tasks.models.task import Task
from tasks.serializers.task_serializer import TaskCSVSerializer, TaskSerializer


class TaskViewSet(BaseMixin, BaseModelViewSet):
    """
    ViewSet for managing Tasks with full CRUD, filtering, ordering, CSV export, and caching.
    """

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    renderer_classes = [JSONRenderer, CSVRenderer]
    serializer_class = TaskSerializer
    csv_serializer_class = TaskCSVSerializer
    filterset_class = TasksRequestFilter
    ordering_fields = ["created_at", "due_date", "priority"]
    ordering = ["-created_at"]
    cache_enabled = False
    cache_key_prefix = "task"
    file_name_prefix = "tasks"

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    @cache_api_call("user_id")
    def recent(self, request):
        """Cached endpoint for recent tasks"""
        queryset = self.get_queryset().order_by("-created_at")[
            : settings.RECENT_TASKS_COUNT
        ]
        data = TaskSerializer(queryset, many=True).data
        return Response(data)
