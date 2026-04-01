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
