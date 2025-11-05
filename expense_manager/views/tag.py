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
