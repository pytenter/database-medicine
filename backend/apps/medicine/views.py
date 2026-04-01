from rest_framework import permissions, viewsets

from apps.accounts.permissions import IsSystemOrPharmacyAdmin
from apps.medicine.models import Manufacturer, Medicine, MedicineCategory
from apps.medicine.serializers import ManufacturerSerializer, MedicineCategorySerializer, MedicineSerializer


class ReadOnlyForSalesWriteForAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in {"system_admin", "pharmacy_admin", "salesperson"}
        return request.user.role in {"system_admin", "pharmacy_admin"}


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all().order_by("id")
    serializer_class = ManufacturerSerializer
    permission_classes = [IsSystemOrPharmacyAdmin]
    search_fields = ["name", "contact_person", "contact_phone"]


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    queryset = MedicineCategory.objects.all().order_by("id")
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsSystemOrPharmacyAdmin]
    search_fields = ["name", "description"]


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related("manufacturer", "category").all().order_by("id")
    serializer_class = MedicineSerializer
    permission_classes = [ReadOnlyForSalesWriteForAdmin]
    search_fields = ["code", "name", "manufacturer__name"]
    ordering_fields = ["id", "code", "name", "retail_price"]
