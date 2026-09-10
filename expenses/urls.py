from django.urls import path, include
from rest_framework.routers import DefaultRouter
from finances.views import ContributionViewSet
from expenses.views import (ExpenseViewSet)

router = DefaultRouter()
router.register(
    "contributions",
    ContributionViewSet,
    basename="contribution"
)

router.register("expenses",ExpenseViewSet,basename="expense")

urlpatterns = [
    path("", include(router.urls)),
]