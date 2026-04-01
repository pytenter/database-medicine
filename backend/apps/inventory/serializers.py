from rest_framework import serializers

from apps.inventory.models import Inventory, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_code = serializers.CharField(source="medicine.code", read_only=True)
    manufacturer_name = serializers.CharField(source="medicine.manufacturer.name", read_only=True)
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
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_warning_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Warning threshold cannot be negative.")
        return value
