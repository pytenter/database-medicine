from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("medicine", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                ("order_no", models.CharField(max_length=30, unique=True, verbose_name="Purchase Order No")),
                ("purchaser_name", models.CharField(max_length=50, verbose_name="Purchaser Name")),
                ("planned_date", models.DateField(blank=True, null=True, verbose_name="Planned Arrival Date")),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Total Amount")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "待采购"),
                            ("ordered", "已下单"),
                            ("received", "已入库"),
                            ("cancelled", "已取消"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Purchase Status",
                    ),
                ),
                ("item_summary", models.CharField(max_length=255, verbose_name="Item Summary")),
                ("remark", models.CharField(blank=True, max_length=255, verbose_name="Remark")),
                (
                    "manufacturer",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to="medicine.manufacturer"),
                ),
                (
                    "store",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="purchase_orders", to="inventory.store"),
                ),
            ],
            options={
                "db_table": "purchase_order",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="PurchaseOrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                ("quantity", models.IntegerField(verbose_name="Quantity")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Purchase Unit Price")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Amount")),
                (
                    "medicine",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_items", to="medicine.medicine"),
                ),
                (
                    "order",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="inventory.purchaseorder"),
                ),
            ],
            options={
                "db_table": "purchase_order_item",
                "ordering": ["id"],
            },
        ),
    ]
