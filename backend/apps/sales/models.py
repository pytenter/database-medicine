from django.db import models

from apps.common.models import TimeStampedModel


class SaleOrder(TimeStampedModel):
    order_no = models.CharField(max_length=32, unique=True, verbose_name="订单编号")
    store = models.ForeignKey("inventory.Store", on_delete=models.PROTECT, related_name="sales")
    salesperson = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="sales")
    customer_name = models.CharField(max_length=100, blank=True, verbose_name="客户名称")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="订单金额")
    remark = models.CharField(max_length=255, blank=True, verbose_name="备注")

    class Meta:
        db_table = "sale_order"
        ordering = ["-id"]

    def __str__(self):
        return self.order_no


class SaleOrderItem(TimeStampedModel):
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey("medicine.Medicine", on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.IntegerField(verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="金额")

    class Meta:
        db_table = "sale_order_item"
        ordering = ["id"]

    def __str__(self):
        return f"{self.order.order_no} - {self.medicine.name}"


