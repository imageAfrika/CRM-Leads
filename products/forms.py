from django import forms
from .models import (
    Category, 
    Product, 
    InventoryTransaction, 
    Supplier, 
    Purchase, 
    PurchaseItem
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'item_code', 'name', 'description', 'category',
            'buying_price', 'selling_price', 'current_stock',
            'reorder_level', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'item_code': forms.TextInput(attrs={'placeholder': 'Leave blank for auto-generation'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_code'].required = False

class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = [
            'product', 'transaction_type', 'quantity',
            'unit_price', 'reference_number', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs.update({'step': '0.01'})
        
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        
        if transaction_type == 'sale' and product and quantity:
            if quantity > product.current_stock:
                raise forms.ValidationError(
                    f"Not enough stock available. Current stock: {product.current_stock}"
                )
        
        return cleaned_data

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'purchase_date', 'reference_number', 'status', 'notes']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'reference_number': forms.TextInput(attrs={'placeholder': 'Leave blank for auto-generation'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference_number'].required = False

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs.update({'step': '0.01'})

# Formset for purchase items
PurchaseItemFormSet = forms.inlineformset_factory(
    Purchase, 
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True
) 