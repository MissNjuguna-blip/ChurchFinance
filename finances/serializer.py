from rest_framework import serializers

from core.models import Contribution, ContributionType, Expense
from core.models import Member


class ContributionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributionType
        fields = "__all__"


# finances/serializer.py

from rest_framework import serializers
from core.models import Contribution


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = [
            "id",
            "member",
            "contribution_type",
            "amount",
            "contribution_date",
            "payment_method",
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
        extra_kwargs = {
            "member": {
                "required": False,
                "allow_null": True,
            },
        }


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ["recorded_by"]
