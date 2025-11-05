from django.contrib import admin

from expense_manager.models import Tag, Expense

# Register your models here.
admin.site.register(Tag)
admin.site.register(Expense)
