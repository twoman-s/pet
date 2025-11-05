from expense_manager.models import Tag
from utils.common_serializer import DynamicFieldsModelSerializer


class TagSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "tag_name"]
