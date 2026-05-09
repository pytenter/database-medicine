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
    ]
