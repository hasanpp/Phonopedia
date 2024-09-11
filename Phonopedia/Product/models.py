from django.db import models
from django import forms 
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.text import slugify
import os

# Create your models here.

STARS =( 
    ("1", "One"), 
    ("2", "Two"), 
    ("3", "Three"), 
    ("4", "Four"), 
    ("5", "Five"), 
) 
def upload_to(instance, filename):
    return os.path.join('media/brands/', datetime.now().strftime('%Y/%m/%d/'), filename)

def upload_to_v(instance, filename):
    # You can use something like this to generate a valid path
    return f'variants/{instance.id}/{datetime.now().strftime("%Y%m%d%H%M%S")}_{slugify(filename)}'

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True)
    image = models.ImageField(upload_to =upload_to)
    created_at = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True) 
    created_at = models.DateTimeField(default=datetime.now())
    is_active = models.BooleanField(default=True)
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='prodcuts')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE , related_name='prodcuts')
    operating_system = models.CharField(max_length=25, default='Android')
    processor = models.CharField(max_length=60)
    screen_size = models.CharField(max_length=60)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    description = models.TextField()
    stars = forms.ChoiceField(choices = STARS)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Variants(models.Model):
    color = models.CharField(max_length=25 )
    image = models.ImageField(upload_to=upload_to_v, blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ram = models.IntegerField()
    rom = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class SecondaryImages(models.Model):
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, related_name='secondary_images')
    image = models.ImageField(upload_to=upload_to_v, blank=True, null=True)

