from expense_manager.models import Item
from utils.common_serializer import DynamicFieldsModelSerializer


class ItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "user", "name"]
        read_only_fields = ["id", "user"]

    def validate_name(self, value):
        # Ensure name is lowercase
        return value.lower()
