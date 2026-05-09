from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.common.numbering import next_daily_code
from apps.common.text import CleanDisplaySerializerMixin
from apps.inventory.models import Inventory
from apps.sales.models import (
    SaleOrder,
    SaleOrderItem,
)


class SaleOrderItemWriteSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class SaleOrderItemReadSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    manufacturer_name = serializers.CharField(source="medicine.manufacturer.name", read_only=True)

    class Meta:
        model = SaleOrderItem
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_code",
            "manufacturer_name",
            "quantity",
            "unit_price",
            "amount",
        ]


class SaleOrderSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    items = SaleOrderItemReadSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    store_address = serializers.CharField(source="store.address", read_only=True)
    store_phone = serializers.CharField(source="store.phone", read_only=True)
    salesperson_name = serializers.CharField(source="salesperson.full_name", read_only=True)

    class Meta:
        model = SaleOrder
        fields = [
            "id",
            "order_no",
            "store",
            "store_name",
            "store_address",
            "store_phone",
            "salesperson",
            "salesperson_name",
            "customer_name",
            "customer_phone",
            "total_amount",
            "remark",
            "items",
            "created_at",
        ]


class SaleCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"required": "请填写客户名称。", "blank": "请填写客户名称。"},
    )
    customer_phone = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"required": "请填写联系电话。", "blank": "请填写联系电话。"},
    )
    remark = serializers.CharField(required=False, allow_blank=True)
    items = SaleOrderItemWriteSerializer(many=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.store_id:
            raise serializers.ValidationError("当前账号未关联门店，无法创建销售单。")
        if not attrs["items"]:
            raise serializers.ValidationError("请至少选择一种药品。")

        insufficient_items = []
        for item in attrs["items"]:
            inventory = Inventory.objects.select_related("medicine").filter(
                store_id=user.store_id,
                medicine_id=item["medicine_id"],
            ).first()
            if not inventory:
                insufficient_items.append(f"药品 ID {item['medicine_id']} 在当前门店无库存记录。")
                continue
            if inventory.quantity < item["quantity"]:
                insufficient_items.append(f"{inventory.medicine.name} 库存不足，当前仅剩 {inventory.quantity} 件。")

        if insufficient_items:
            raise serializers.ValidationError({"items": insufficient_items})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        order = SaleOrder.objects.create(
            order_no=next_daily_code(SaleOrder, "order_no", "SO"),
            store_id=user.store_id,
            salesperson=user,
            customer_name=validated_data.get("customer_name", ""),
            customer_phone=validated_data.get("customer_phone", ""),
            remark=validated_data.get("remark", ""),
            total_amount=Decimal("0.00"),
        )

        total_amount = Decimal("0.00")
        for item in validated_data["items"]:
            inventory = Inventory.objects.select_related("medicine").get(
                store_id=user.store_id,
                medicine_id=item["medicine_id"],
            )
            unit_price = inventory.medicine.retail_price
            amount = unit_price * item["quantity"]
            SaleOrderItem.objects.create(
                order=order,
                medicine_id=item["medicine_id"],
                quantity=item["quantity"],
                unit_price=unit_price,
                amount=amount,
            )
            inventory.quantity -= item["quantity"]
            inventory.save(update_fields=["quantity", "updated_at"])
            total_amount += amount

        order.total_amount = total_amount
        order.save(update_fields=["total_amount", "updated_at"])
        return order
