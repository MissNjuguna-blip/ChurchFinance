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
