# Generated by Django 5.1 on 2024-08-15 07:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0009_alter_brand_created_at_alter_category_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 15, 13, 15, 31, 341133)),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 15, 13, 15, 31, 342134)),
        ),
    ]
