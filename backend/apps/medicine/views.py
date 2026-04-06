from django.db.models.deletion import ProtectedError
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
    queryset = Manufacturer.objects.all().order_by("id")
    serializer_class = ManufacturerSerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["name", "contact_person", "contact_phone"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "该厂商已被药品或采购单引用，无法直接删除。"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    queryset = MedicineCategory.objects.all().order_by("id")
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["name", "description"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "该分类已被药品引用，无法直接删除。"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related("manufacturer", "category").all().order_by("id")
    serializer_class = MedicineSerializer
    permission_classes = [ReadOnlyForSalesWriteForPharmacyAdmin]
    search_fields = ["code", "name", "manufacturer__name"]
    ordering_fields = ["id", "code", "name", "retail_price"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "该药品已关联库存、销售记录或其他业务数据，无法直接删除。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
