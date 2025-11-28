from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from expense_manager.models import Tag
from expense_manager.serializers import TAG_SERIALIZER


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TAG_SERIALIZER.TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable pagination for this viewset

    def get_queryset(self):
        # Return only tags belonging to the authenticated user
        return Tag.objects.filter(user=self.request.user).order_by("tag_name")

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Override list to return all tags without pagination
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            data={
                "count": queryset.count(),
                "next": None,
                "previous": None,
                "results": serializer.data,
            }
        )
