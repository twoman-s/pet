from rest_framework.routers import DefaultRouter
from expense_manager.views import EXPENSE_VIEW, TAG_VIEW, BANK_ACCOUNT_VIEW, ITEM_VIEW

router = DefaultRouter()
router.register(r"tags", TAG_VIEW.TagViewSet, basename="tag")
router.register(r"expenses", EXPENSE_VIEW.ExpenseViewSet, basename="expense")
router.register(
    r"bank_accounts", BANK_ACCOUNT_VIEW.BankAccountViewSet, basename="bank_account"
)
router.register(r"items", ITEM_VIEW.ItemViewSet, basename="item")

urlpatterns = router.urls
