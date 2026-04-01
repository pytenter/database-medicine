from rest_framework import serializers

from apps.medicine.models import Manufacturer, Medicine, MedicineCategory


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class MedicineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineCategory
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Medicine
        fields = [
            "id",
            "code",
            "name",
            "specification",
            "unit",
            "purchase_price",
            "retail_price",
            "manufacturer",
            "manufacturer_name",
            "category",
            "category_name",
            "approval_number",
            "production_date",
            "expiry_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        purchase_price = attrs.get("purchase_price", getattr(self.instance, "purchase_price", None))
        retail_price = attrs.get("retail_price", getattr(self.instance, "retail_price", None))
        if purchase_price is not None and purchase_price <= 0:
            raise serializers.ValidationError("Purchase price must be greater than 0.")
        if retail_price is not None and retail_price <= 0:
            raise serializers.ValidationError("Retail price must be greater than 0.")
        return attrs
