# Generated by Django 5.1 on 2024-08-26 07:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0015_alter_orders_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 26, 7, 13, 43, 822037, tzinfo=datetime.timezone.utc)),
        ),
    ]
