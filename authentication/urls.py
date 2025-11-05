from django.urls import path
from authentication.views import EMAIL_LOGIN_VIEW

urlpatterns = [
    path("auth/login/", EMAIL_LOGIN_VIEW.EmailLoginView.as_view(), name="email_login"),
]
