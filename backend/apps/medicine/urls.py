from rest_framework.routers import DefaultRouter

from apps.medicine.views import ManufacturerViewSet, MedicineCategoryViewSet, MedicineViewSet

router = DefaultRouter()
router.register("manufacturers", ManufacturerViewSet, basename="manufacturer")
router.register("categories", MedicineCategoryViewSet, basename="category")
router.register("", MedicineViewSet, basename="medicine")

urlpatterns = router.urls
