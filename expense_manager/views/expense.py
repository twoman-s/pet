from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from expense_manager.models import Expense
from expense_manager.serializers import EXPENSE_SERIALIZER


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allow owners to access their own Expense objects
        return isinstance(obj, Expense) and obj.user_id == request.user.id


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = EXPENSE_SERIALIZER.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the expense is attributed to the logged-in user
        serializer.save(user=self.request.user)

    # ------- Bulk Create -------
    @action(detail=False, methods=["post"], url_path="bulk_create")
    def bulk_create(self, request):
        many = isinstance(request.data, list)
        if not many:
            return Response(
                {"detail": "Expected a list of items."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        created_instances = []
        # Can't use bulk_create due to M2M; create one-by-one safely
        with transaction.atomic():
            for item in serializer.validated_data:
                tag_names = item.pop("tags", [])
                exp = Expense.objects.create(user=request.user, **item)
                if tag_names:
                    tags = serializer._get_or_create_tags(tag_names)
                    exp.tags.set(tags)
                created_instances.append(exp)

        out = self.get_serializer(created_instances, many=True)
        return Response(out.data, status=status.HTTP_201_CREATED)

    # ------- Bulk Update -------
    @action(detail=False, methods=["put", "patch"], url_path="bulk_update")
    def bulk_update(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Expected a list of items."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Map by id; fetch only the user's items
        ids = [item.get("id") for item in request.data if item.get("id") is not None]
        if not ids:
            return Response(
                {"detail": "Each item must include an 'id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self.get_queryset().filter(id__in=ids)
        existing_by_id = {obj.id: obj for obj in qs}

        updated = []
        partial = request.method.lower() == "patch"
        with transaction.atomic():
            for payload in request.data:
                obj_id = payload.get("id")
                instance = existing_by_id.get(obj_id)
                if not instance:
                    # ignore or report? Here we choose to report missing id
                    return Response(
                        {"detail": f"Expense id {obj_id} not found or not yours."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                serializer = self.get_serializer(
                    instance, data=payload, partial=partial
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()  # tags handled in serializer.update
                updated.append(instance)

        out = self.get_serializer(updated, many=True)
        return Response(out.data, status=status.HTTP_200_OK)
