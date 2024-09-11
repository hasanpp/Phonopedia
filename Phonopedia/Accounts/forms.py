#### forms.py
from django import forms


class varification(forms.Form):
    email = forms.EmailField()