from django.urls import path, include
from rest_framework.routers import DefaultRouter

from finances.views import (
    ContributionTypeViewSet,
    ContributionViewSet,
)

router = DefaultRouter()

router.register(
    "contribution-types",
    ContributionTypeViewSet,
    basename="contribution-type"
)

router.register(
    "contributions",
    ContributionViewSet,
    basename="contribution"
)

urlpatterns = [
    path("", include(router.urls)),
]
