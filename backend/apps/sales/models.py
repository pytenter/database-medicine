from django.db import models

from apps.common.models import TimeStampedModel


class SaleOrderStatusChoices(models.TextChoices):
    PENDING_PAYMENT = "pending_payment", "待付款"
    ORDERED = "ordered", "已下单"
    DELIVERING = "delivering", "配送中"
    COMPLETED = "completed", "已收货"


class SaleOrder(TimeStampedModel):
    order_no = models.CharField(max_length=32, unique=True, verbose_name="订单编号")
    store = models.ForeignKey("inventory.Store", on_delete=models.PROTECT, related_name="sales")
    salesperson = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="sales")
    customer_name = models.CharField(max_length=100, blank=True, verbose_name="客户名称")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    order_status = models.CharField(
        max_length=20,
        choices=SaleOrderStatusChoices.choices,
        default=SaleOrderStatusChoices.ORDERED,
        verbose_name="订单状态",
    )
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


class OrderLogistics(TimeStampedModel):
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name="logistics")
    content = models.CharField(max_length=255, verbose_name="物流内容")
    operator_name = models.CharField(max_length=100, blank=True, verbose_name="操作人员")
    status_after = models.CharField(
        max_length=20,
        choices=SaleOrderStatusChoices.choices,
        blank=True,
        verbose_name="更新后状态",
    )

    class Meta:
        db_table = "order_logistics"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.order.order_no} - {self.content}"


class OrderReview(TimeStampedModel):
    order = models.OneToOneField(SaleOrder, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="评分")
    content = models.CharField(max_length=255, blank=True, verbose_name="评价内容")
    reviewer_name = models.CharField(max_length=100, blank=True, verbose_name="评价人")

    class Meta:
        db_table = "order_review"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_no} - {self.rating}"
