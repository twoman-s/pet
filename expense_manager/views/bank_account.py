from rest_framework import viewsets, permissions

from expense_manager.models import BankAccount
from expense_manager.serializers import BANK_ACCOUNT_SERIALIZER


class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BANK_ACCOUNT_SERIALIZER.BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only bank accounts belonging to the authenticated user
        return BankAccount.objects.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)
