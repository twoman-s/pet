from rest_framework import serializers
from expense_manager.models import Expense, Tag
from utils.common_serializer import DynamicFieldsModelSerializer


class ExpenseSerializer(DynamicFieldsModelSerializer):
    # READ: show tags as list of tag names
    tags = serializers.SerializerMethodField(read_only=True)

    # WRITE: accept list of tag names (["Food","Travel"])
    write_tags = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, write_only=True
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "date",
            "time",
            "transaction_info",
            "transaction_date_time",
            "notes",
            "currency",
            "tags",  # read-only
            "write_tags",  # write-only
            "created_at",
            "updated_at",
            "transaction_type",
            "bank_account",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # ---------- helpers ----------
    def _get_or_create_tags(self, tag_names):
        if not tag_names:
            return []
        norm = []
        seen = set()
        for name in tag_names:
            n = name.strip()
            if n and n not in seen:
                seen.add(n)
                norm.append(n)
        existing = {t.tag_name: t for t in Tag.objects.filter(tag_name__in=norm)}
        return [existing.get(n) or Tag.objects.create(tag_name=n) for n in norm]

    # ---------- representation ----------
    def get_tags(self, obj):
        # ensure we iterate a queryset, not the manager
        return list(obj.tags.all().values_list("id", flat=True))

    # ---------- create / update ----------
    def create(self, validated_data):
        tag_names = validated_data.pop("write_tags", [])
        expense = Expense.objects.create(**validated_data)
        if tag_names:
            expense.tags.set(self._get_or_create_tags(tag_names))
        return expense

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("write_tags", None)  # None => not provided
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if tag_names is not None:
            instance.tags.set(self._get_or_create_tags(tag_names))
        return instance
