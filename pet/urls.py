from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

# Customize admin site headers
admin.site.site_header = "Pet Expense Manager Admin"
admin.site.site_title = "Pet Admin"
admin.site.index_title = "Welcome to Pet Expense Manager"


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Authentication (django-allauth for Google Sign-in)
    path("accounts/", include("allauth.urls")),
    # Expense Manager API (tags + expenses)
    path("api/v1/", include("expense_manager.urls")),
    path("api/v1/", include("authentication.urls")),
    # JWT Auth (for API clients)
    # path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    # API Schema & Docs
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
