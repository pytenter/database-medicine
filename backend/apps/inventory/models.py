from django.db import models

from apps.common.models import TimeStampedModel


class Store(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Store Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Store Name")
    address = models.CharField(max_length=255, verbose_name="Address")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    manager_name = models.CharField(max_length=50, blank=True, verbose_name="Manager Name")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "store"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Inventory(TimeStampedModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="inventories")
    medicine = models.ForeignKey("medicine.Medicine", on_delete=models.CASCADE, related_name="inventories")
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    warning_threshold = models.IntegerField(default=10, verbose_name="Warning Threshold")

    class Meta:
        db_table = "inventory"
        unique_together = ("store", "medicine")
        ordering = ["id"]

    def __str__(self):
        return f"{self.store.name} - {self.medicine.name}"


class PurchaseOrderStatusChoices(models.TextChoices):
    PENDING = "pending", "待采购"
    ORDERED = "ordered", "已下单"
    RECEIVED = "received", "已入库"
    CANCELLED = "cancelled", "已取消"


class PurchaseOrder(TimeStampedModel):
    order_no = models.CharField(max_length=30, unique=True, verbose_name="Purchase Order No")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="purchase_orders")
    manufacturer = models.ForeignKey("medicine.Manufacturer", on_delete=models.PROTECT, related_name="purchase_orders")
    purchaser_name = models.CharField(max_length=50, verbose_name="Purchaser Name")
    planned_date = models.DateField(null=True, blank=True, verbose_name="Planned Arrival Date")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total Amount")
    status = models.CharField(
        max_length=20,
        choices=PurchaseOrderStatusChoices.choices,
        default=PurchaseOrderStatusChoices.PENDING,
        verbose_name="Purchase Status",
    )
    item_summary = models.CharField(max_length=255, verbose_name="Item Summary")
    remark = models.CharField(max_length=255, blank=True, verbose_name="Remark")

    class Meta:
        db_table = "purchase_order"
        ordering = ["-id"]

    def __str__(self):
        return self.order_no
