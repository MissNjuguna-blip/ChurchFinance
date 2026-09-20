# finances/serializer.py

from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Contribution, ContributionType


class ContributionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContributionType
        fields = "__all__"


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

    def validate(self, attrs):

        member = attrs.get("member")
        contribution_type = attrs.get("contribution_type")
        contribution_date = attrs.get("contribution_date")

        if not contribution_type or not contribution_date:
            return attrs

        # Sunday = first day of the reporting week

        days_since_sunday = (
            contribution_date.weekday() + 1
        ) % 7

        start_of_week = (
            contribution_date
            - timedelta(days=days_since_sunday)
        )

        end_of_week = (
            start_of_week
            + timedelta(days=6)
        )

        duplicate_query = Contribution.objects.filter(
            contribution_type=contribution_type,
            contribution_date__range=[
                start_of_week,
                end_of_week
            ]
        )

        if member:
            duplicate_query = duplicate_query.filter(
                member=member
            )
        else:
            duplicate_query = duplicate_query.filter(
                member__isnull=True
            )

        if self.instance:

            duplicate_query = (
                duplicate_query
                .exclude(id=self.instance.id)
            )

        if duplicate_query.exists():

            raise ValidationError({
                "contribution_date": (
                    f"A contribution of type "
                    f"'{contribution_type}' has already "
                    f"been recorded for this member "
                    f"for the week starting "
                    f"{start_of_week.strftime('%Y-%m-%d')}."
                )
            })

        return attrs
