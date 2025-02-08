from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Client Name'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Person'}),

            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Client Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Client Phone'}),
        }

