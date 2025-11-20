from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from expense_manager.models import Tag
from expense_manager.serializers import TAG_SERIALIZER


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("tag_name")
    serializer_class = TAG_SERIALIZER.TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable pagination for this viewset

    def list(self, request, *args, **kwargs):
        # Override list to return all tags without pagination
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": queryset.count(),
                "next": null,
                "previous": null,
                "results": serializer.data,
            }
        )
