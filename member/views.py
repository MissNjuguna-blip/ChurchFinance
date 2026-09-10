from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.audit import create_audit_log
from core.models import Member, AuditLog
from member.serializer import MemberSerializer
from core.audit import create_audit_log

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().order_by("-created_at")
    serializer_class = MemberSerializer
    permission_classes = [
        IsAuthenticated
    ]
    def perform_create(self, serializer):

        member = serializer.save()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            instance=member,
            description=(
                f"Created member "
                f"{member.first_name} {member.last_name}"
            )
        )

    def perform_update(self, serializer):

        member = serializer.save()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=member,
            description=(
                f"Updated member "
                f"{member.first_name} {member.last_name}"
            )
        )

    def perform_destroy(self, instance):

        member_id = instance.id
        member_name = (
            f"{instance.first_name} {instance.last_name}"
        ).strip()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            instance=instance,
            description=(
                f"Deleted member #{member_id}: "
                f"{member_name}"
            )
        )

        instance.delete()