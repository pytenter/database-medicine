from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import IsPharmacyAdmin
from apps.medicine.models import Manufacturer, Medicine, MedicineCategory
from apps.medicine.serializers import ManufacturerSerializer, MedicineCategorySerializer, MedicineSerializer


class ReadOnlyForSalesWriteForPharmacyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in {"pharmacy_admin", "salesperson"}
        return request.user.role == "pharmacy_admin"


class ManufacturerViewSet(viewsets.ModelViewSet):
    serializer_class = ManufacturerSerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["name", "contact_person", "contact_phone"]

    def get_queryset(self):
        return Manufacturer.objects.filter(is_active=True).order_by("id")

    def destroy(self, request, *args, **kwargs):
        manufacturer = self.get_object()
        manufacturer.is_active = False
        manufacturer.save(update_fields=["is_active", "updated_at"])
        return Response(
            {"detail": "厂商已从当前列表隐藏，历史采购和药品数据保留。"},
            status=status.HTTP_200_OK,
        )


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    queryset = MedicineCategory.objects.all().order_by("id")
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["name", "description"]


class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [ReadOnlyForSalesWriteForPharmacyAdmin]
    search_fields = ["code", "name", "manufacturer__name"]
    ordering_fields = ["id", "code", "name", "retail_price"]

    def get_queryset(self):
        return (
            Medicine.objects.select_related("manufacturer", "category")
            .filter(is_active=True)
            .order_by("id")
        )

    def destroy(self, request, *args, **kwargs):
        medicine = self.get_object()
        medicine.is_active = False
        medicine.save(update_fields=["is_active", "updated_at"])
        medicine.inventories.update(is_active=False)
        return Response(
            {"detail": "药品已从当前列表隐藏，历史订单信息保留不受影响。"},
            status=status.HTTP_200_OK,
        )
