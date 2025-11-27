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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the expense with the authenticated user
        expense = serializer.save(user=request.user)

        # Adjust bank account balance
        bank_account = expense.bank_account
        amount = expense.amount
        transaction_type = expense.transaction_type

        if transaction_type == "Debit":
            bank_account.balance = (bank_account.balance or 0) - amount
        elif transaction_type == "Credit":
            bank_account.balance = (bank_account.balance or 0) + amount

        bank_account.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Store original values
        original_amount = instance.amount
        original_transaction_type = instance.transaction_type
        original_bank_account = instance.bank_account

        # Apply updates
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()

        # Get new values
        new_amount = expense.amount
        new_transaction_type = expense.transaction_type
        new_bank_account = expense.bank_account

        # Check if bank account changed
        if original_bank_account.id == new_bank_account.id:
            # Case A: Same bank account - reverse original and apply new
            bank_account = original_bank_account

            # Reverse original effect
            if original_transaction_type == "Debit":
                bank_account.balance = (bank_account.balance or 0) + original_amount
            elif original_transaction_type == "Credit":
                bank_account.balance = (bank_account.balance or 0) - original_amount

            # Apply new effect
            if new_transaction_type == "Debit":
                bank_account.balance = (bank_account.balance or 0) - new_amount
            elif new_transaction_type == "Credit":
                bank_account.balance = (bank_account.balance or 0) + new_amount

            bank_account.save()
        else:
            # Case B: Bank account changed - reverse on old, apply on new
            # Reverse on original bank account
            if original_transaction_type == "Debit":
                original_bank_account.balance = (
                    original_bank_account.balance or 0
                ) + original_amount
            elif original_transaction_type == "Credit":
                original_bank_account.balance = (
                    original_bank_account.balance or 0
                ) - original_amount
            original_bank_account.save()

            # Apply on new bank account
            if new_transaction_type == "Debit":
                new_bank_account.balance = (new_bank_account.balance or 0) - new_amount
            elif new_transaction_type == "Credit":
                new_bank_account.balance = (new_bank_account.balance or 0) + new_amount
            new_bank_account.save()

        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Store values before deletion
        bank_account = instance.bank_account
        amount = instance.amount
        transaction_type = instance.transaction_type

        # Reverse the transaction effect on balance
        if transaction_type == "Debit":
            bank_account.balance = (bank_account.balance or 0) + amount
        elif transaction_type == "Credit":
            bank_account.balance = (bank_account.balance or 0) - amount

        bank_account.save()

        # Delete the expense
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        # This method is no longer used since we override create()
        # Keeping it for backward compatibility if needed
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
    @action(detail=False, methods=["get"], url_path="filter_by_date_range_and_tags")
    def filter_by_date_range_and_tags(self, request):
        """
        Filter expenses by date range, tags, and/or bank account.
        Query parameters:
            - start_date (YYYY-MM-DD) - If provided, end_date is mandatory
            - end_date (YYYY-MM-DD) - If provided, start_date is mandatory
            - tags (comma-separated tag IDs) - Optional, can be used independently or with dates
            - bank_account (integer) - Optional, bank account ID to filter by
        Logic:
            - If start_date or end_date is provided, BOTH are required
            - If only tags are provided, filter by tags (date range optional)
            - If bank_account is provided, filter by that bank account
            - At least one filter must be provided
        Examples:
            - By tags only: /api/v1/expenses/filter_by_date_range_and_tags/?tags=1,2,3
            - By date range only: /api/v1/expenses/filter_by_date_range_and_tags/?start_date=2025-01-01&end_date=2025-11-30
            - By bank account only: /api/v1/expenses/filter_by_date_range_and_tags/?bank_account=5
            - All combined: /api/v1/expenses/filter_by_date_range_and_tags/?start_date=2025-01-01&end_date=2025-11-30&tags=1,2,3&bank_account=5
        """
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")
        tags_param = request.query_params.get("tags")
        bank_account_param = request.query_params.get("bank_account")

        # Check if any filter is provided
        date_provided = bool(start_date_str or end_date_str)

        # If any date is provided, both dates are required
        if date_provided and not (start_date_str and end_date_str):
            return Response(
                {"detail": "If start_date or end_date is provided, both are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # At least one filter must be provided
        if not date_provided and not tags_param and not bank_account_param:
            return Response(
                {
                    "detail": "At least one filter is required: date range (start_date and end_date), tags, or bank_account."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expenses = self.get_queryset()

        # Parse and validate dates if provided
        if start_date_str and end_date_str:
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

            # Apply date filter
            expenses = expenses.filter(
                date__gte=start_date,
                date__lte=end_date,
            )

        # Parse and validate tags if provided
        tag_ids = []
        if tags_param:
            try:
                tag_ids = [
                    int(tag_id.strip())
                    for tag_id in tags_param.split(",")
                    if tag_id.strip()
                ]
            except ValueError:
                return Response(
                    {"detail": "tags must be comma-separated integers."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate at least one tag ID
            if not tag_ids:
                return Response(
                    {"detail": "At least one tag ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply tag filter
            expenses = expenses.filter(tags__id__in=tag_ids)

        # Parse and validate bank account if provided
        bank_account_id = None
        if bank_account_param:
            try:
                bank_account_id = int(bank_account_param)
            except ValueError:
                return Response(
                    {"detail": "bank_account must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply bank account filter
            expenses = expenses.filter(bank_account_id=bank_account_id)

        # Remove duplicates if both filters are applied
        expenses = expenses.distinct()

        serializer = self.get_serializer(expenses, many=True)

        response_data = {
            "count": expenses.count(),
            "results": serializer.data,
        }

        # Include applied filters in response
        if start_date_str and end_date_str:
            response_data["start_date"] = start_date_str
            response_data["end_date"] = end_date_str
        if tags_param:
            response_data["tags"] = tag_ids
        if bank_account_param:
            response_data["bank_account"] = bank_account_id

        return Response(response_data, status=status.HTTP_200_OK)

    # ------- Filter by Tags -------
    @action(detail=False, methods=["get"], url_path="filter_by_tags")
    def filter_by_tags(self, request):
        """
        Filter expenses by tag IDs.
        Query parameters: tags (comma-separated tag IDs)
        Example: /api/v1/expenses/filter_by_tags/?tags=1,2,3
        """
        tags_param = request.query_params.get("tags")

        # Validate parameter exists
        if not tags_param:
            return Response(
                {"detail": "tags parameter is required (comma-separated tag IDs)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse tag IDs
        try:
            tag_ids = [
                int(tag_id.strip())
                for tag_id in tags_param.split(",")
                if tag_id.strip()
            ]
        except ValueError:
            return Response(
                {"detail": "tags must be comma-separated integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate at least one tag ID
        if not tag_ids:
            return Response(
                {"detail": "At least one tag ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter expenses that have any of the specified tags
        expenses = self.get_queryset().filter(tags__id__in=tag_ids).distinct()

        serializer = self.get_serializer(expenses, many=True)
        return Response(
            {
                "tags": tag_ids,
                "count": expenses.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
