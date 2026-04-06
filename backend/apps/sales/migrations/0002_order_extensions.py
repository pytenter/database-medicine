from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="saleorder",
            name="customer_phone",
            field=models.CharField(blank=True, max_length=20, verbose_name="联系电话"),
        ),
        migrations.AddField(
            model_name="saleorder",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("pending_payment", "待付款"),
                    ("ordered", "已下单"),
                    ("delivering", "配送中"),
                    ("completed", "已收货"),
                ],
                default="ordered",
                max_length=20,
                verbose_name="订单状态",
            ),
        ),
        migrations.CreateModel(
            name="OrderLogistics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                ("content", models.CharField(max_length=255, verbose_name="物流内容")),
                ("operator_name", models.CharField(blank=True, max_length=100, verbose_name="操作人")),
                (
                    "status_after",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending_payment", "待付款"),
                            ("ordered", "已下单"),
                            ("delivering", "配送中"),
                            ("completed", "已收货"),
                        ],
                        max_length=20,
                        verbose_name="更新后状态",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logistics", to="sales.saleorder"),
                ),
            ],
            options={"db_table": "order_logistics", "ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="OrderReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                ("rating", models.PositiveSmallIntegerField(default=5, verbose_name="评分")),
                ("content", models.CharField(blank=True, max_length=255, verbose_name="评价内容")),
                ("reviewer_name", models.CharField(blank=True, max_length=100, verbose_name="评价人")),
                (
                    "order",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="review", to="sales.saleorder"),
                ),
            ],
            options={"db_table": "order_review", "ordering": ["-created_at"]},
        ),
    ]