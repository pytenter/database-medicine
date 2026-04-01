from rest_framework.routers import DefaultRouter

from apps.sales.views import SaleOrderViewSet

router = DefaultRouter()
router.register("", SaleOrderViewSet, basename="sale-order")

urlpatterns = router.urls
