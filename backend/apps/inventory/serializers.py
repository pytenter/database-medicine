from rest_framework import serializers

from apps.inventory.models import Inventory, PurchaseOrder, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    manufacturer_name = serializers.CharField(source="medicine.manufacturer.name", read_only=True)
    retail_price = serializers.DecimalField(source="medicine.retail_price", max_digits=10, decimal_places=2, read_only=True)
    is_warning = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            "id",
            "store",
            "store_name",
            "medicine",
            "medicine_name",
            "medicine_code",
            "manufacturer_name",
            "retail_price",
            "quantity",
            "warning_threshold",
            "is_warning",
            "created_at",
            "updated_at",
        ]

    def get_is_warning(self, obj):
        return obj.quantity <= obj.warning_threshold

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("库存数量不能为负数。")
        return value

    def validate_warning_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("预警阈值不能为负数。")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_no",
            "store",
            "store_name",
            "manufacturer",
            "manufacturer_name",
            "purchaser_name",
            "planned_date",
            "total_amount",
            "status",
            "status_display",
            "item_summary",
            "remark",
            "created_at",
            "updated_at",
        ]

    def validate_total_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("采购金额不能为负数。")
        return value
