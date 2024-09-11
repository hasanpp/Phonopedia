from django.contrib import admin
from .models import Product,Variants,Brand,Category
# Register your models here.
admin.site.register(Product)
admin.site.register(Variants)
admin.site.register(Brand)
admin.site.register(Category)