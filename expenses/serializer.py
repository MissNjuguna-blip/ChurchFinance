# expenses/serializer.py

from rest_framework import serializers

from core.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense

        fields = [
            "id",
            "description",
            "amount",
            "expense_date",
            "payment_method",
            "reference",
            "status",
            "recorded_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
