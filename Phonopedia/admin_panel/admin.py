# admin_panel/admin.py
from django.contrib import admin
from .models import Coupon,Coupon_usage
# Register your models here.

admin.site.register(Coupon)

admin.site.register(Coupon_usage)