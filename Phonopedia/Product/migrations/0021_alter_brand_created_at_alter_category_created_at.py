# Generated by Django 5.1 on 2024-08-21 09:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0020_alter_brand_created_at_alter_category_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 21, 14, 42, 16, 853600)),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 21, 14, 42, 16, 854600)),
        ),
    ]
