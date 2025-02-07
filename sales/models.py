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
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale {self.id} - {self.client.name} - ${self.total_amount}"

    def get_absolute_url(self):
        return reverse('sales:sale_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        # Always calculate total_amount before saving
        self.total_amount = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def get_total(self):
        return self.quantity * self.unit_price * (1 - self.discount/100)

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

    class Meta:
        ordering = ['id']


