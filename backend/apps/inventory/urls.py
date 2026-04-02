from rest_framework.routers import DefaultRouter

from apps.inventory.views import InventoryViewSet, PurchaseOrderViewSet, StoreViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register("", InventoryViewSet, basename="inventory")

urlpatterns = router.urls
