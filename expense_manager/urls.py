from rest_framework.routers import DefaultRouter
from expense_manager.views import EXPENSE_VIEW, TAG_VIEW

router = DefaultRouter()
router.register(r"tags", TAG_VIEW.TagViewSet, basename="tag")
router.register(r"expenses", EXPENSE_VIEW.ExpenseViewSet, basename="expense")

urlpatterns = router.urls
