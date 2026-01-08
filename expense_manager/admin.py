from django.contrib import admin
from unfold.admin import ModelAdmin

from expense_manager.models import (
    Tag,
    Expense,
    BankAccount,
    Item,
    Currency,
    ExpenseItem,
)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["id", "tag_name", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["tag_name", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


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
    list_display = ["id", "account_name", "account_number", "balance", "user"]
    search_fields = ["account_name", "account_number", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Item)
class ItemAdmin(ModelAdmin):
    list_display = ["id", "name", "user", "created_at"]
    search_fields = ["name", "user__username"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ["id", "code", "name", "symbol"]
    search_fields = ["code", "name"]


@admin.register(ExpenseItem)
class ExpenseItemAdmin(ModelAdmin):
    list_display = ["id", "expense", "item", "amount"]
    search_fields = ["expense__transaction_info", "item__name"]
    list_filter = ["item"]
    readonly_fields = []
