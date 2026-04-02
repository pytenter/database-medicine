from rest_framework.routers import DefaultRouter

from apps.accounts.views import ShiftScheduleViewSet, UserViewSet

router = DefaultRouter()
router.register("shifts", ShiftScheduleViewSet, basename="shift-schedule")
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls
