from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.common.numbering import next_daily_code
from apps.common.text import CleanDisplaySerializerMixin, is_placeholder_text
from apps.inventory.models import Inventory, PurchaseOrder, PurchaseOrderItem, Store


class StoreSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class InventorySerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    manufacturer_name = serializers.CharField(source="medicine.manufacturer.name", read_only=True)
    retail_price = serializers.DecimalField(source="medicine.retail_price", max_digits=10, decimal_places=2, read_only=True)
    is_warning = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        validators = []
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

    def create(self, validated_data):
        store = validated_data["store"]
        medicine = validated_data["medicine"]
        quantity = validated_data.get("quantity", 0)
        warning_threshold = validated_data.get("warning_threshold", 10)

        with transaction.atomic():
            inventory = (
                Inventory.objects.select_for_update()
                .filter(store=store, medicine=medicine)
                .first()
            )
            if inventory:
                inventory.quantity += quantity
                inventory.warning_threshold = warning_threshold
                inventory.is_active = True
                inventory.save(update_fields=["quantity", "warning_threshold", "is_active", "updated_at"])
                return inventory

            return super().create(validated_data)


class PurchaseOrderItemWriteSerializer(serializers.Serializer):
    medicine = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class PurchaseOrderItemReadSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    specification = serializers.CharField(source="medicine.specification", read_only=True)
    unit = serializers.CharField(source="medicine.unit", read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_code",
            "specification",
            "unit",
            "quantity",
            "unit_price",
            "amount",
        ]


class PurchaseOrderSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)
    item_details = PurchaseOrderItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = PurchaseOrder
        read_only_fields = ["order_no", "total_amount", "item_summary"]
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
            "items",
            "item_details",
            "remark",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if is_placeholder_text(data.get("remark")):
            data["remark"] = "门店常规补货"
        return data

    def validate(self, attrs):
        item_details = attrs.get("item_details")
        if self.instance is None and not item_details:
            raise serializers.ValidationError({"item_details": "请至少添加一种采购药品。"})
        if item_details is not None and not item_details:
            raise serializers.ValidationError({"item_details": "请至少添加一种采购药品。"})
        return attrs

    def _build_order_items(self, order, item_details):
        from apps.medicine.models import Medicine

        total_amount = Decimal("0.00")
        summary_parts = []
        rows = []

        for item in item_details:
            medicine = Medicine.objects.filter(id=item["medicine"], is_active=True).first()
            if not medicine:
                raise serializers.ValidationError({"item_details": f"药品 ID {item['medicine']} 不存在或已停用。"})
            if medicine.manufacturer_id != order.manufacturer_id:
                raise serializers.ValidationError({"item_details": f"{medicine.name} 不属于所选厂商。"})

            quantity = item["quantity"]
            unit_price = medicine.purchase_price
            amount = unit_price * quantity
            total_amount += amount
            summary_parts.append(f"{medicine.name}{quantity}{medicine.unit}")
            rows.append(
                PurchaseOrderItem(
                    order=order,
                    medicine=medicine,
                    quantity=quantity,
                    unit_price=unit_price,
                    amount=amount,
                )
            )

        PurchaseOrderItem.objects.bulk_create(rows)
        order.total_amount = total_amount
        order.item_summary = "，".join(summary_parts)
        order.save(update_fields=["total_amount", "item_summary", "updated_at"])

    @transaction.atomic
    def create(self, validated_data):
        item_details = validated_data.pop("item_details", [])
        validated_data["order_no"] = next_daily_code(PurchaseOrder, "order_no", "PO")
        validated_data["total_amount"] = Decimal("0.00")
        validated_data["item_summary"] = ""
        order = super().create(validated_data)
        self._build_order_items(order, item_details)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        item_details = validated_data.pop("item_details", None)
        order = super().update(instance, validated_data)
        if item_details is not None:
            order.items.all().delete()
            self._build_order_items(order, item_details)
        return order
