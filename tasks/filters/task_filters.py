from django_filters import rest_framework as django_filters

from tasks.models import Task


class TaskFilterSet(django_filters.FilterSet):
    """Filter for Tasks based on request parameters."""

    min_priority = django_filters.NumberFilter(field_name="priority", lookup_expr="gte")
    max_priority = django_filters.NumberFilter(field_name="priority", lookup_expr="lte")
    due_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ["min_priority", "max_priority", "due_before", "due_after"]
