# Generated by Django 5.1 on 2024-08-29 10:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0038_alter_brand_created_at_alter_category_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 29, 15, 47, 52, 930519)),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 29, 15, 47, 52, 930519)),
        ),
    ]
