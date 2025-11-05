from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EmailPasswordLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        # Try to resolve user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.MultipleObjectsReturned:
            raise AuthenticationFailed(
                "Multiple accounts use this email. Contact support."
            )
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")

        # Authenticate by username, since default backend uses username
        user = authenticate(username=user.get_username(), password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("This account is disabled.")

        # Issue tokens
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.get_username(),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
