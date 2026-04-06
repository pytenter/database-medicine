from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from rest_framework import serializers

from apps.common.text import CleanDisplaySerializerMixin, is_placeholder_text, repair_text
from apps.inventory.models import Inventory
from apps.sales.models import (
    OrderLogistics,
    OrderReview,
    SaleOrder,
    SaleOrderItem,
    SaleOrderStatusChoices,
)


_STANDARD_LOGISTICS_CONTENT = {
    SaleOrderStatusChoices.ORDERED: "等待配送",
    SaleOrderStatusChoices.DELIVERING: "配送员正在配送",
    SaleOrderStatusChoices.COMPLETED: "订单已送达",
}

_LEGACY_LOGISTICS_CONTENT = {
    "订单已创建，等待门店备货。": _STANDARD_LOGISTICS_CONTENT[SaleOrderStatusChoices.ORDERED],
    "药店已完成拣货，配送员正在派送。": _STANDARD_LOGISTICS_CONTENT[SaleOrderStatusChoices.DELIVERING],
    "订单已完成签收，客户已收货。": _STANDARD_LOGISTICS_CONTENT[SaleOrderStatusChoices.COMPLETED],
    "正在配送": _STANDARD_LOGISTICS_CONTENT[SaleOrderStatusChoices.DELIVERING],
}


def normalize_logistics_content(content, status_after=""):
    cleaned = repair_text(content or "")
    cleaned = _LEGACY_LOGISTICS_CONTENT.get(cleaned, cleaned)
    if is_placeholder_text(cleaned):
        return _STANDARD_LOGISTICS_CONTENT.get(status_after, "物流状态已更新")
    return cleaned


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


class OrderLogisticsSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    status_after_label = serializers.CharField(source="get_status_after_display", read_only=True)

    class Meta:
        model = OrderLogistics
        fields = [
            "id",
            "content",
            "operator_name",
            "status_after",
            "status_after_label",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["content"] = normalize_logistics_content(data.get("content"), data.get("status_after", ""))
        return data


class OrderReviewSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = OrderReview
        fields = ["id", "rating", "content", "reviewer_name", "created_at", "updated_at"]


class SaleOrderSerializer(CleanDisplaySerializerMixin, serializers.ModelSerializer):
    items = SaleOrderItemReadSerializer(many=True, read_only=True)
    logistics = OrderLogisticsSerializer(many=True, read_only=True)
    review = OrderReviewSerializer(read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    store_address = serializers.CharField(source="store.address", read_only=True)
    store_phone = serializers.CharField(source="store.phone", read_only=True)
    salesperson_name = serializers.CharField(source="salesperson.full_name", read_only=True)
    order_status_label = serializers.CharField(source="get_order_status_display", read_only=True)
    latest_logistics = serializers.SerializerMethodField()

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
            "order_status",
            "order_status_label",
            "total_amount",
            "remark",
            "items",
            "logistics",
            "latest_logistics",
            "review",
            "created_at",
        ]

    def get_latest_logistics(self, obj):
        latest = obj.logistics.order_by("-created_at", "-id").first()
        return OrderLogisticsSerializer(latest).data if latest else None


class SaleCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True)
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
            order_no=f"SO{uuid4().hex[:12].upper()}",
            store_id=user.store_id,
            salesperson=user,
            customer_name=validated_data.get("customer_name", ""),
            customer_phone=validated_data.get("customer_phone", ""),
            order_status=SaleOrderStatusChoices.ORDERED,
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
        OrderLogistics.objects.create(
            order=order,
            content=_STANDARD_LOGISTICS_CONTENT[SaleOrderStatusChoices.ORDERED],
            operator_name=user.full_name or user.username,
            status_after=SaleOrderStatusChoices.ORDERED,
        )
        return order


class LogisticsUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=255)
    status_after = serializers.ChoiceField(
        choices=SaleOrderStatusChoices.choices,
        required=False,
        allow_blank=False,
    )

    @transaction.atomic
    def create(self, validated_data):
        order = self.context["order"]
        user = self.context["request"].user
        status_after = validated_data.get("status_after", "")
        content = normalize_logistics_content(validated_data.get("content"), status_after)
        if status_after in _STANDARD_LOGISTICS_CONTENT and not content:
            content = _STANDARD_LOGISTICS_CONTENT[status_after]

        logistics = OrderLogistics.objects.create(
            order=order,
            content=content,
            operator_name=user.full_name or user.username,
            status_after=status_after,
        )
        if validated_data.get("status_after"):
            order.order_status = validated_data["status_after"]
            order.save(update_fields=["order_status", "updated_at"])
        return logistics


class ReviewSubmitSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(max_length=255, required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data):
        order = self.context["order"]
        user = self.context["request"].user
        review, _created = OrderReview.objects.update_or_create(
            order=order,
            defaults={
                "rating": validated_data["rating"],
                "content": validated_data.get("content", ""),
                "reviewer_name": user.full_name or user.username,
            },
        )
        return review