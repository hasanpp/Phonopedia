# Generated by Django 5.1 on 2024-09-11 08:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0061_alter_brand_created_at_alter_category_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 11, 14, 2, 53, 334510)),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 11, 14, 2, 53, 334510)),
        ),
    ]
