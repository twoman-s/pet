from rest_framework import serializers
from expense_manager.models import Expense, Tag, Item, ExpenseItem
from utils.common_serializer import DynamicFieldsModelSerializer


class ExpenseSerializer(DynamicFieldsModelSerializer):
    # READ: show tags as list of tag IDs
    tags = serializers.SerializerMethodField(read_only=True)

    # WRITE: accept list of tag names (["Food","Travel"])
    write_tags = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, write_only=True
    )

    # READ: show items as list of {item_id, name, amount}
    items = serializers.SerializerMethodField(read_only=True)

    # WRITE: accept list of {name, amount} dicts
    write_items = serializers.ListField(
        child=serializers.DictField(), required=False, write_only=True
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
            "items",  # read-only
            "write_items",  # write-only
            "created_at",
            "updated_at",
            "transaction_type",
            "bank_account",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # ---------- helpers ----------
    def _get_or_create_tags(self, tag_names, user):
        if not tag_names:
            return []
        norm = []
        seen = set()
        for name in tag_names:
            n = name.strip()
            if n and n not in seen:
                seen.add(n)
                norm.append(n)
        existing = {
            t.tag_name: t for t in Tag.objects.filter(tag_name__in=norm, user=user)
        }
        return [
            existing.get(n) or Tag.objects.create(tag_name=n, user=user) for n in norm
        ]

    def _get_or_create_items(self, items_data, user):
        """
        items_data: list of {name, amount} dicts
        Returns list of (Item, amount) tuples
        """
        if not items_data:
            return []

        result = []
        for item_dict in items_data:
            name = item_dict.get("name", "").strip().lower()
            amount = item_dict.get("amount")

            if not name or amount is None:
                continue

            item, _ = Item.objects.get_or_create(user=user, name=name)
            result.append((item, amount))

        return result

    # ---------- representation ----------
    def get_tags(self, obj):
        # ensure we iterate a queryset, not the manager
        return list(obj.tags.all().values_list("id", flat=True))

    def get_items(self, obj):
        # Return list of {item_id, name, amount} for all ExpenseItems
        expense_items = obj.expense_items.select_related("item").all()
        return [
            {"item_id": ei.item.id, "name": ei.item.name, "amount": str(ei.amount)}
            for ei in expense_items
        ]

    # ---------- create / update ----------
    def create(self, validated_data):
        tag_names = validated_data.pop("write_tags", [])
        items_data = validated_data.pop("write_items", [])

        expense = Expense.objects.create(**validated_data)

        # Handle tags
        if tag_names:
            user = expense.user
            expense.tags.set(self._get_or_create_tags(tag_names, user))

        # Handle items
        if items_data:
            user = expense.user
            item_tuples = self._get_or_create_items(items_data, user)
            for item, amount in item_tuples:
                ExpenseItem.objects.create(expense=expense, item=item, amount=amount)

        return expense

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("write_tags", None)  # None => not provided
        items_data = validated_data.pop("write_items", None)

        # Update expense fields
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        # Handle tags
        if tag_names is not None:
            user = instance.user
            instance.tags.set(self._get_or_create_tags(tag_names, user))

        # Handle items
        if items_data is not None:
            user = instance.user
            # Delete all existing ExpenseItems
            instance.expense_items.all().delete()

            # Create new ExpenseItems
            item_tuples = self._get_or_create_items(items_data, user)
            for item, amount in item_tuples:
                ExpenseItem.objects.create(expense=instance, item=item, amount=amount)

        return instance
