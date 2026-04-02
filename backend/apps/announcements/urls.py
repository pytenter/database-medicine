from rest_framework.routers import DefaultRouter

from apps.announcements.views import AnnouncementViewSet

router = DefaultRouter()
router.register("", AnnouncementViewSet, basename="announcement")

urlpatterns = router.urls
