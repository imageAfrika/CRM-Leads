from django.db import models
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone

# Create your models here.
class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('CANCELLED', 'Cancelled'),
    )
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    sale_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH'
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='PENDING'
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    include_tax = models.BooleanField(default=True, verbose_name="Include VAT")

    def __str__(self):
        return f"Sale {self.id} - {self.client.name} - ${self.total_amount}"

    def get_absolute_url(self):
        return reverse('sales:sale_detail', kwargs={'pk': self.pk})

    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        if not self.pk:  # Skip if sale is not saved yet
            return
        
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax_amount = self.subtotal * (self.tax_rate/100) if self.include_tax else Decimal('0')
        self.total_amount = self.subtotal + self.tax_amount

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if this is a new sale
        super().save(*args, **kwargs)  # Save first to get the primary key
        
        if not is_new:  # Only calculate totals for existing sales
            self.calculate_totals()
            super().save(*args, **kwargs)  # Save again with updated totals

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def get_total(self):
        """Calculate total price for this item including discount"""
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount / 100)
        return subtotal - discount_amount

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

    class Meta:
        ordering = ['id']

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.name}"
    
    def get_absolute_url(self):
        return reverse('sales:invoice_detail', kwargs={'pk': self.pk})
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.total_amount = self.subtotal + self.tax_amount - self.discount
        
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_id = int(last_invoice.invoice_number.split('-')[-1])
                self.invoice_number = f"INV-{last_id + 1:04d}"
            else:
                self.invoice_number = "INV-0001"
                
        super().save(*args, **kwargs)
        
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != 'PAID'

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def get_total(self):
        """Calculate total price for this item including discount"""
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount / 100)
        return subtotal - discount_amount
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

class Quote(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    )
    
    quote_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='quotes')
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Quote {self.quote_number} - {self.client.name}"
    
    def save(self, *args, **kwargs):
        # Generate quote number if not already set
        if not self.quote_number:
            last_quote = Quote.objects.order_by('-id').first()
            if last_quote:
                last_number = int(last_quote.quote_number.split('-')[-1])
                self.quote_number = f"QUOTE-{last_number + 1:04d}"
            else:
                self.quote_number = "QUOTE-0001"
        
        super().save(*args, **kwargs)
