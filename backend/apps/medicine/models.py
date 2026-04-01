from django.db import models

from apps.common.models import TimeStampedModel


class Manufacturer(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Manufacturer Name")
    contact_person = models.CharField(max_length=50, blank=True, verbose_name="Contact Person")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Contact Phone")

    class Meta:
        db_table = "manufacturer"
        ordering = ["id"]

    def __str__(self):
        return self.name


class MedicineCategory(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Category Name")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")

    class Meta:
        db_table = "medicine_category"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Medicine(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Medicine Code")
    name = models.CharField(max_length=100, db_index=True, verbose_name="Medicine Name")
    specification = models.CharField(max_length=100, verbose_name="Specification")
    unit = models.CharField(max_length=20, default="box", verbose_name="Unit")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Purchase Price")
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Retail Price")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name="medicines")
    category = models.ForeignKey(MedicineCategory, on_delete=models.PROTECT, related_name="medicines")
    approval_number = models.CharField(max_length=60, blank=True, verbose_name="Approval Number")
    production_date = models.DateField(null=True, blank=True, verbose_name="Production Date")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Expiry Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        db_table = "medicine"
        ordering = ["id"]

    def __str__(self):
        return f"{self.code} - {self.name}"
