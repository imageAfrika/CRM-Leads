from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            'client',
            'quote_number',
            'title',
            'description',
            'subtotal',
            'tax_rate',
            'valid_until',
            'status'
        ]
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        subtotal = cleaned_data.get('subtotal')
        tax_rate = cleaned_data.get('tax_rate')

        if subtotal and tax_rate:
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            cleaned_data['tax_amount'] = tax_amount
            cleaned_data['total_amount'] = total_amount

        return cleaned_data 