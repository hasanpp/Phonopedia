from django import forms
from .models import Brand
from .models import Variants
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'image']


class VariantForm(forms.ModelForm):
    
    class Meta:
        model = Variants
        fields = ['color', 'image', 'quantity', 'price', 'ram', 'rom']

    