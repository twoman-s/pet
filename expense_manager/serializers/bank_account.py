from expense_manager.models import BankAccount
from utils.common_serializer import DynamicFieldsModelSerializer


class BankAccountSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "user",
            "name",
            "balance",
            "ifsc_code",
            "account_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
