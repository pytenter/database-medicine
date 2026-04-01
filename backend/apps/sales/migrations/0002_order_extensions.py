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
            field=models.CharField(blank=True, max_length=20, verbose_name="????"),
        ),
        migrations.AddField(
            model_name="saleorder",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("pending_payment", "???"),
                    ("ordered", "???"),
                    ("delivering", "???"),
                    ("completed", "???"),
                ],
                default="ordered",
                max_length=20,
                verbose_name="????",
            ),
        ),
        migrations.CreateModel(
            name="OrderLogistics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                ("content", models.CharField(max_length=255, verbose_name="????")),
                ("operator_name", models.CharField(blank=True, max_length=100, verbose_name="????")),
                (
                    "status_after",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending_payment", "???"),
                            ("ordered", "???"),
                            ("delivering", "???"),
                            ("completed", "???"),
                        ],
                        max_length=20,
                        verbose_name="?????",
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
                ("rating", models.PositiveSmallIntegerField(default=5, verbose_name="??")),
                ("content", models.CharField(blank=True, max_length=255, verbose_name="????")),
                ("reviewer_name", models.CharField(blank=True, max_length=100, verbose_name="???")),
                (
                    "order",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="review", to="sales.saleorder"),
                ),
            ],
            options={"db_table": "order_review", "ordering": ["-created_at"]},
        ),
    ]
