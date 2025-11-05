from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import EMAIL_LOGIN_SERIALIZER


class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EMAIL_LOGIN_SERIALIZER.EmailPasswordLoginSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
