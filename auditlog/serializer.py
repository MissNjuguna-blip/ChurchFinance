from rest_framework import serializers
from core.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_display = serializers.StringRelatedField(
        source="user",
        read_only=True
    )

    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_full_name",
            "user_display",
            "action",
            "model_name",
            "object_id",
            "description",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "user_full_name",
            "user_display",
            "created_at",
            "updated_at",
        ]

    def get_user_full_name(self, obj):
        user = obj.user

        full_name = f"{user.first_name} {user.last_name}".strip()

        return full_name or user.username or "Unknown user"
