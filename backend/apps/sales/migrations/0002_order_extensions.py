from django.db import migrations, models


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
                    ("delivering", "处理中"),
                    ("completed", "已完成"),
                ],
                default="ordered",
                max_length=20,
                verbose_name="订单状态",
            ),
        ),
    ]
