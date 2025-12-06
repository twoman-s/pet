from django.db import models
from django.conf import settings


class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="User",
    )
    tag_name = models.CharField(max_length=50, verbose_name="Tag Name")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["tag_name"]
        unique_together = ["user", "tag_name"]  # Unique tag name per user

    def __str__(self):
        return self.tag_name


class BankAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name="User",
    )
    name = models.CharField(max_length=255, verbose_name="Account Name")
    balance = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True, verbose_name="Balance"
    )
    ifsc_code = models.CharField(
        max_length=11, null=True, blank=True, verbose_name="IFSC Code"
    )
    account_number = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Account Number"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.account_number}"


class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="User",
    )
    name = models.CharField(max_length=255, verbose_name="Item Name")

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["name"]
        unique_together = ["user", "name"]

    def save(self, *args, **kwargs):
        # Always store name in lowercase
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="User",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Bank Account",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    date = models.DateField(verbose_name="Transaction Date")
    time = models.TimeField(verbose_name="Transaction Time")
    transaction_info = models.CharField(
        max_length=255, blank=True, verbose_name="Transaction Information"
    )
    transaction_date_time = models.DateTimeField(verbose_name="Transaction Date & Time")
    notes = models.TextField(blank=True, verbose_name="Notes")
    currency = models.CharField(max_length=10, default="INR", verbose_name="Currency")
    tags = models.ManyToManyField(
        Tag, related_name="expenses", blank=True, verbose_name="Tags"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    transaction_type = models.CharField(
        max_length=10, blank=True, verbose_name="Transaction Type"
    )

    class Meta:
        ordering = ["-transaction_date_time"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} on {self.date}"


class ExpenseItem(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="expense_items",
        verbose_name="Expense",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="expense_items",
        verbose_name="Item",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")

    class Meta:
        verbose_name = "Expense Item"
        verbose_name_plural = "Expense Items"

    def __str__(self):
        return f"{self.expense.id} - {self.item.name} - {self.amount}"
