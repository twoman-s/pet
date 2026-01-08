from django.contrib import admin
from unfold.admin import ModelAdmin

from expense_manager.models import (
    Tag,
    Expense,
    BankAccount,
    Item,
    ExpenseItem,
)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["id", "tag_name", "user"]
    search_fields = ["tag_name", "user__username"]


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ["id", "amount", "date", "transaction_type", "user", "bank_account"]
    list_filter = ["transaction_type", "date", "bank_account"]
    search_fields = ["transaction_info", "notes", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "date"
    filter_horizontal = ["tags"]


@admin.register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ["id", "name", "account_number", "balance", "user"]
    search_fields = ["name", "account_number", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Item)
class ItemAdmin(ModelAdmin):
    list_display = ["id", "name", "user"]
    search_fields = ["name", "user__username"]


@admin.register(ExpenseItem)
class ExpenseItemAdmin(ModelAdmin):
    list_display = ["id", "expense", "item", "amount"]
    search_fields = ["expense__transaction_info", "item__name"]
    list_filter = ["item"]
    readonly_fields = []
