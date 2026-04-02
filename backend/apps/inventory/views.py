from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import IsSystemOrPharmacyAdmin
from apps.inventory.models import Inventory, Store
from apps.inventory.serializers import InventorySerializer, StoreSerializer


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsSystemOrPharmacyAdmin]
    search_fields = ["code", "name", "address", "manager_name"]

    def get_queryset(self):
        queryset = Store.objects.all().order_by("id")
        user = self.request.user
        if user.role == "pharmacy_admin" and user.store_id:
            queryset = queryset.filter(id=user.store_id)
        return queryset


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
            raise PermissionDenied("???????????????")

    def perform_create(self, serializer):
        self._validate_store_scope(serializer.validated_data["store"].id)
        serializer.save()

    def perform_update(self, serializer):
        self._validate_store_scope(serializer.validated_data.get("store", serializer.instance.store).id)
        serializer.save()
