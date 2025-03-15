from django import forms
from .models import Person, Role, ContactHistory

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'phone', 
                  'telegram_username', 'address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class RoleAssignmentForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['role']
        widgets = {
            'role': forms.CheckboxSelectMultiple(),
        }

class ContactForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    
    class Meta:
        model = ContactHistory
        fields = ['contact_type', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }