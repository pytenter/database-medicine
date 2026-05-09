from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.accounts.permissions import IsPharmacyAdmin, IsSystemAdmin
from apps.common.numbering import next_daily_code, next_prefixed_sequence_code
from apps.inventory.models import Inventory, PurchaseOrder, Store
from apps.inventory.serializers import InventorySerializer, PurchaseOrderSerializer, StoreSerializer


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsSystemAdmin]
    search_fields = ["code", "name", "address", "manager_name"]

    def get_queryset(self):
        return Store.objects.all().order_by("id")

    @action(detail=False, methods=["get"], url_path="next-code")
    def next_code(self, request):
        return Response({"code": next_prefixed_sequence_code(Store, "code", "ST")})


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
        queryset = (
            Inventory.objects.select_related("store", "medicine", "medicine__manufacturer")
            .filter(is_active=True, medicine__is_active=True)
            .order_by("id")
        )
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

    def destroy(self, request, *args, **kwargs):
        inventory = self.get_object()
        self._validate_store_scope(inventory.store_id)
        inventory.is_active = False
        inventory.save(update_fields=["is_active", "updated_at"])
        return Response(
            {"detail": "库存记录已从当前列表隐藏，历史订单信息保留不受影响。"},
            status=status.HTTP_200_OK,
        )


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["order_no", "manufacturer__name", "item_summary", "purchaser_name"]
    ordering_fields = ["id", "planned_date", "total_amount", "updated_at"]

    def get_queryset(self):
        queryset = (
            PurchaseOrder.objects.select_related("store", "manufacturer")
            .prefetch_related("items", "items__medicine")
            .all()
            .order_by("-id")
        )
        user = self.request.user
        if user.store_id:
            queryset = queryset.filter(store_id=user.store_id)
        else:
            queryset = queryset.none()
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    @action(detail=False, methods=["get"], url_path="next-code")
    def next_code(self, request):
        return Response({"order_no": next_daily_code(PurchaseOrder, "order_no", "PO")})

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
