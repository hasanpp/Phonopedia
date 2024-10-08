# Generated by Django 5.1 on 2024-08-27 03:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0030_alter_brand_created_at_alter_category_created_at'),
        ('Users', '0018_alter_orders_order_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balence', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users.order_items')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.variants')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users.wallet')),
            ],
        ),
    ]
