from django.db import models
from django.contrib.auth.models import AbstractUser
from Product.models import Variants
import random
import string

# Create your models here.



class Custom_User(AbstractUser):
    phone = models.CharField(null= True, max_length=20)
    email = models.EmailField(max_length = 50,unique=True)
    profile_pic = models.ImageField(upload_to='profile_pic/% Y/% m/% d/')
    
class Address(models.Model):
    Region = models.CharField(max_length=40,default='India')
    state = models.CharField(max_length=40)
    district = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    place = models.CharField(max_length=40)
    pin = models.IntegerField()
    house_name = models.CharField(max_length=40)
    landmark = models.CharField(max_length=40)
    road = models.CharField(max_length=40)
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Wishlist(models.Model):
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Cart(models.Model):
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class DeliveryAddress(models.Model):
    Region = models.CharField(max_length=40,default='India')
    state = models.CharField(max_length=40)
    district = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    place = models.CharField(max_length=40)
    pin = models.IntegerField()
    house_name = models.CharField(max_length=40)
    landmark = models.CharField(max_length=40)
    road = models.CharField(max_length=40)
    name = models.CharField(max_length=50)
    phone = models.CharField(null= True, max_length=20)
    
class Orders(models.Model):
    pyment_method = models.CharField(max_length=20)
    pyment_status = models.CharField(max_length=20)
    invoice_no = models.CharField(max_length=20, blank=True, null=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)
    delivery_charge = models.IntegerField(default=50)
    delivery_date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    

class Order_items(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, related_name='order_items')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50)
    
class Wallet(models.Model):
    user = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    balence = models.DecimalField(max_digits=10, decimal_places=2)
    
class Transactions(models.Model):
    order_item = models.ForeignKey(Order_items, on_delete=models.CASCADE,  null=True, blank=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=50,default='credit')
    
class Profile(models.Model):
    user = models.OneToOneField(Custom_User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = 'PH' +''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)