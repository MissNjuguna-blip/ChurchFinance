from rest_framework import serializers
from core.models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "id",
            "first_name",
            "last_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "first_name": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "last_name": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }
