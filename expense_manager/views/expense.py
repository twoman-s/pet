from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from datetime import datetime

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

    # ------- Filter by Month -------
    @action(detail=False, methods=["get"], url_path="filter_by_month")
    def filter_by_month(self, request):
        """
        Filter expenses by month and year.
        Query parameters: month (1-12), year (YYYY)
        Example: /api/v1/expenses/filter_by_month/?month=11&year=2025
        """
        try:
            month = int(request.query_params.get("month"))
            year = int(request.query_params.get("year"))
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": "month and year parameters are required and must be integers."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate month range
        if not (1 <= month <= 12):
            return Response(
                {"detail": "month must be between 1 and 12."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter expenses for the given month and year
        expenses = self.get_queryset().filter(
            date__year=year,
            date__month=month,
        )

        serializer = self.get_serializer(expenses, many=True)
        return Response(
            {
                "month": month,
                "year": year,
                "count": expenses.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------- Filter by Date Range -------
    @action(detail=False, methods=["get"], url_path="filter_by_date_range")
    def filter_by_date_range(self, request):
        """
        Filter expenses between two dates (inclusive).
        Query parameters: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
        Example: /api/v1/expenses/filter_by_date_range/?start_date=2025-01-01&end_date=2025-11-30
        """
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        # Validate parameters exist
        if not start_date_str or not end_date_str:
            return Response(
                {"detail": "start_date and end_date parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Dates must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date range
        if start_date > end_date:
            return Response(
                {"detail": "start_date must be before or equal to end_date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter expenses within the date range
        expenses = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date,
        )

        serializer = self.get_serializer(expenses, many=True)
        return Response(
            {
                "start_date": start_date_str,
                "end_date": end_date_str,
                "count": expenses.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
