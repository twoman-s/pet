from django.db import models
from django.conf import settings


class Tag(models.Model):
    tag_name = models.CharField(max_length=50, unique=True, verbose_name="Tag Name")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["tag_name"]

    def __str__(self):
        return self.tag_name


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="User",
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

    class Meta:
        ordering = ["-transaction_date_time"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} on {self.date}"
