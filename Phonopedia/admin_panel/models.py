# admin_panel/models.py
from django.db import models
from Product.models import Product,Category,Brand
from Users.models import Custom_User as User,Orders
import random
import string


    
class Product_offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Brand_offer(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    percentage = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Coupon(models.Model):
    code = models.CharField(max_length=20)
    percentage = models.CharField(max_length=3)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.1)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000000)
    description = models.TextField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    expiry = models.DateField()
    
    def save(self, *args, **kwargs):
        if not self.code:
            percentage = self.percentage
            if len(self.percentage) == 1:
                percentage = '0' + self.percentage
            self.code = 'PH' +''.join(random.choices(string.ascii_uppercase + string.digits, k=6))+percentage
        super().save(*args, **kwargs)
    
class Coupon_usage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True, related_name='coupon_usage')
    used_at = models.DateField(auto_now_add=True)