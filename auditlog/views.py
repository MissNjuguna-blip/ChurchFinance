from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import AuditLog
from auditlog.serializer import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AuditLog.objects.select_related("user").all().order_by("-created_at")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
