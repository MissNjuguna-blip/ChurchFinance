from django.urls import include, path
from rest_framework.routers import DefaultRouter
from auditlog.views import AuditLogViewSet

router = DefaultRouter()

router.register("auditlogs",AuditLogViewSet,basename="auditlogs",)

urlpatterns = [
    path("", include(router.urls)),
]
