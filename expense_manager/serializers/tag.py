from expense_manager.models import Tag
from utils.common_serializer import DynamicFieldsModelSerializer


class TagSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "user", "tag_name"]
        read_only_fields = ["id", "user"]
