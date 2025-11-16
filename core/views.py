import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer

from core.constants import MAX_ROWS_TO_DOWNLOAD
from core.pagination import CustomPageNumberPagination
from core.permissions import IsOwnerOrStaff

logger = logging.getLogger(__name__)


class BaseMixin:
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    pagination_class = CustomPageNumberPagination


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet supporting:
    - Full CRUD
    - Optional caching for GET requests
    - CSV download support
    - Custom pagination & filtering
    - Default filter when no filters applied
    - Queryset preprocessing hook
    """

    cache_enabled = True
    cache_timeout = getattr(settings, "CACHE_TIMEOUT", 300)
    cache_key_prefix = None  # override per-viewset if desired

    renderer_classes = [JSONRenderer, CSVRenderer]

    # ---------------------------------------------------------
    #                     CACHE HELPERS
    # ---------------------------------------------------------

    def get_cache_key(self, request):
        """Builds a stable cache key independent of renderer format."""
        user_id = getattr(request.user, "id", "anonymous")

        params = request.query_params.copy()
        params.pop("format", None)  # format should NOT affect cache

        query_part = urlencode(sorted(params.items()))
        path = f"{request.path}?{query_part}" if query_part else request.path

        prefix = f"{self.cache_key_prefix}:" if self.cache_key_prefix else ""
        return f"{prefix}{self.__class__.__name__.lower()}:{user_id}:{path}"

    def get_from_cache(self, request):
        if not self.cache_enabled:
            return None
        return cache.get(self.get_cache_key(request))

    def set_to_cache(self, request, data):
        if not self.cache_enabled:
            return
        cache.set(self.get_cache_key(request), data, timeout=self.cache_timeout)

    def invalidate_cache(self, request):
        """Invalidate all cached keys for this user & viewset."""
        if not self.cache_enabled:
            return

        user_id = getattr(request.user, "id", "anonymous")
        prefix = f"{self.__class__.__name__.lower()}:{user_id}:"

        try:
            keys = cache.keys(f"*{prefix}*")
            if keys:
                cache.delete_many(keys)
        except NotImplementedError:
            logger.warning(
                "Cache backend does not support pattern key deletion. "
                "Consider switching to Redis for full cache invalidation support."
            )

    # ---------------------------------------------------------
    #                 SERIALIZER HANDLING
    # ---------------------------------------------------------

    def get_serializer_class(self):
        """Select CSV serializer only for CSV responses."""
        if (
            hasattr(self, "csv_serializer_class")
            and self.request.accepted_renderer.format == "csv"
        ):
            return self.csv_serializer_class

        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def serialize_data(self, obj, many=False, serializer_class=None):
        """Normalize serialization behavior for caching."""
        if serializer_class is None:
            serializer_class = self.serializer_class

        return serializer_class(
            obj, many=many, context=self.get_serializer_context()
        ).data

    # ---------------------------------------------------------
    #           FILTERING + QUERYSET PREPROCESSING
    # ---------------------------------------------------------

    def preprocess_queryset(self, queryset):
        """Hook for prefetch/select_related etc."""
        return queryset

    def get_default_filter(self):
        """Optional default filter if user provides no filters."""
        return

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        filter_params = self.request.query_params.dict()
        filter_fields = set()

        if hasattr(self, "filterset_class"):
            filter_fields = set(self.filterset_class.get_filters().keys())

        default_filter = self.get_default_filter()

        if default_filter and not any(param in filter_fields for param in filter_params):
            queryset = queryset.filter(**default_filter)

        return self.preprocess_queryset(queryset)

    # ---------------------------------------------------------
    #                        LIST
    # ---------------------------------------------------------

    def list(self, request, *args, **kwargs):
        # ----- CACHE CHECK -----
        cached = self.get_from_cache(request)
        if cached is not None:
            data = cached
        else:
            queryset = self.filter_queryset(self.get_queryset())
            data = self.serialize_data(queryset, many=True)
            self.set_to_cache(request, data)

        # ----- CSV MODE -----
        if request.accepted_renderer.format == "csv":
            rows = data[:MAX_ROWS_TO_DOWNLOAD]
            csv_data = self.serialize_data(
                rows,
                many=True,
                serializer_class=self.get_serializer_class(),
            )
            return Response(csv_data)

        # ----- JSON MODE WITH PAGINATION -----
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(data)

    # ---------------------------------------------------------
    #                     RETRIEVE
    # ---------------------------------------------------------

    def retrieve(self, request, *args, **kwargs):
        cached = self.get_from_cache(request)
        if cached is not None:
            return Response(cached)

        instance = self.get_object()
        data = self.serialize_data(instance)
        self.set_to_cache(request, data)
        return Response(data)

    # ---------------------------------------------------------
    #             CREATE / UPDATE / DELETE
    # ---------------------------------------------------------

    def perform_create(self, serializer):
        instance = serializer.save()
        self.invalidate_cache(self.request)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self.invalidate_cache(self.request)
        return instance

    def perform_destroy(self, instance):
        instance.delete()
        self.invalidate_cache(self.request)

    # ---------------------------------------------------------
    #                     CSV FILENAME
    # ---------------------------------------------------------

    def get_filename(self):
        prefix = getattr(self, "file_name_prefix", self.__class__.__name__.lower())
        timestamp = timezone.now().strftime("%Y-%m-%d_%H_%M_%S")
        return f"{prefix}_{timestamp}.csv"

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if request.accepted_renderer.format == "csv":
            response["Content-Disposition"] = (
                f"attachment; filename='{self.get_filename()}'"
            )

        return response
