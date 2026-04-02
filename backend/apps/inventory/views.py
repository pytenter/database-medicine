from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import IsPharmacyAdmin, IsSystemAdmin
from apps.inventory.models import Inventory, PurchaseOrder, Store
from apps.inventory.serializers import InventorySerializer, PurchaseOrderSerializer, StoreSerializer


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsSystemAdmin]
    search_fields = ["code", "name", "address", "manager_name"]

    def get_queryset(self):
        return Store.objects.all().order_by("id")


class InventoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in {"pharmacy_admin", "salesperson"}
        return request.user.role == "pharmacy_admin"


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [InventoryPermission]
    search_fields = ["store__name", "medicine__name", "medicine__code", "medicine__manufacturer__name"]
    ordering_fields = ["id", "quantity", "updated_at"]

    def get_queryset(self):
        queryset = Inventory.objects.select_related("store", "medicine", "medicine__manufacturer").all().order_by("id")
        user = self.request.user
        if user.role in {"pharmacy_admin", "salesperson"} and user.store_id:
            queryset = queryset.filter(store_id=user.store_id)
        return queryset

    def _validate_store_scope(self, store_id):
        user = self.request.user
        if user.role == "pharmacy_admin" and user.store_id != store_id:
            raise PermissionDenied("只能维护所属门店的库存记录。")

    def perform_create(self, serializer):
        self._validate_store_scope(serializer.validated_data["store"].id)
        serializer.save()

    def perform_update(self, serializer):
        self._validate_store_scope(serializer.validated_data.get("store", serializer.instance.store).id)
        serializer.save()


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["order_no", "manufacturer__name", "item_summary", "purchaser_name"]
    ordering_fields = ["id", "planned_date", "total_amount", "updated_at"]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related("store", "manufacturer").all().order_by("-id")
        user = self.request.user
        if user.store_id:
            queryset = queryset.filter(store_id=user.store_id)
        else:
            queryset = queryset.none()
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def _validate_store_scope(self, store_id):
        user = self.request.user
        if not user.store_id or user.store_id != store_id:
            raise PermissionDenied("只能管理所属门店的采购订单。")

    def perform_create(self, serializer):
        store = serializer.validated_data["store"]
        self._validate_store_scope(store.id)
        serializer.save()

    def perform_update(self, serializer):
        store = serializer.validated_data.get("store", serializer.instance.store)
        self._validate_store_scope(store.id)
        serializer.save()
