from rest_framework.routers import DefaultRouter

from apps.inventory.views import InventoryViewSet, StoreViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")
router.register("", InventoryViewSet, basename="inventory")

urlpatterns = router.urls
