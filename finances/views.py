from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Contribution, ContributionType,AuditLog
from core.audit import create_audit_log

from finances.serializer import (
    ContributionSerializer,
    ContributionTypeSerializer,
)


class ContributionTypeViewSet(viewsets.ModelViewSet):

    queryset = ContributionType.objects.all()
    serializer_class = ContributionTypeSerializer
    permission_classes = [IsAuthenticated]


class ContributionViewSet(viewsets.ModelViewSet):

    queryset = Contribution.objects.select_related(
        "member",
        "contribution_type",
        "recorded_by",
    ).all()

    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        contribution = serializer.save(
            recorded_by=self.request.user
        )

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            instance=contribution,
            description=(
                f"Recorded contribution of "
                f"{contribution.amount}"
            )
        )

    def perform_update(self, serializer):

        contribution = serializer.save()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=contribution,
            description=(
                f"Updated contribution #{contribution.id}"
            )
        )

    def perform_destroy(self, instance):

        contribution_id = instance.id
        amount = instance.amount

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            instance=instance,
            description=(
                f"Deleted contribution #{contribution_id} "
                f"of {amount}"
            )
        )

        instance.delete()
