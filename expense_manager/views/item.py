from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from expense_manager.models import Item
from expense_manager.serializers import ITEM_SERIALIZER


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ITEM_SERIALIZER.ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
