from rest_framework.routers import DefaultRouter
from member.views import MemberViewSet

router = DefaultRouter()

router.register(
    "members",
    MemberViewSet,
    basename="members"
)

urlpatterns = router.urls
