from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "paging": {
                    "page": self.page.number,
                    "size": self.get_page_size(self.request),
                    "total_pages": self.page.paginator.num_pages,
                    "total_elements": self.page.paginator.count,
                },
                "items": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "paging": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "example": 1,
                        },
                        "size": {
                            "type": "integer",
                            "example": 10,
                        },
                        "total_pages": {
                            "type": "integer",
                            "example": 3,
                        },
                        "total_elements": {
                            "type": "integer",
                            "example": 23,
                        },
                    },
                },
                "items": schema,
            },
        }


class CustomPageNumberDisabledPagination(CustomPageNumberPagination):
    """
    A pagination class that disables pagination, but returns the same structure
    as the TasksApplicationPagination to avoid breaking the API contract.
    """

    def paginate_queryset(self, queryset, request, view=None):
        return queryset

    def get_paginated_response(self, data):
        return Response(
            {
                "paging": {"page": 1, "total_pages": 1, "total_elements": len(data)},
                "items": data,
            }
        )
