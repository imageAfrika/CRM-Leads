from django.db import models
from django.urls import reverse
from clients.models import Client
from .utils import generate_quote_pdf

class Document(models.Model):
    """
    Model representing various types of business documents like quotes, invoices, etc.
    """
    DOCUMENT_TYPES = [
        ('QUOTE', 'Quote'),
        ('INVOICE', 'Invoice'),
        ('DELIVERY_NOTE', 'Delivery Note'),
        ('PROFORMA_INVOICE', 'Proforma Invoice'),
        ('PAYMENT_RECEIPT', 'Payment Receipt'),
    ]

    # Client relationship
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # Document details
    title = models.CharField(max_length=200)
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES
    )
    description = models.TextField(blank=True)
    
    # Financial information
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )

    # File handling
    file = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        help_text='Upload document file'
    )

    # Dates
    document_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f"{self.client.name} - {self.get_document_type_display()} - {self.title}"

    def get_absolute_url(self):
        return reverse('documents:document_detail', kwargs={'pk': self.pk})

class Quote(models.Model):
    # Client relationship
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='quotes'
    )

    # Quote details
    quote_number = models.CharField(
        max_length=50,
        unique=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Financial information
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Status
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    # Validity
    valid_until = models.DateField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # PDF handling
    pdf_file = models.FileField(upload_to='quotes/', blank=True, null=True)

    # Terms and conditions
    terms = models.TextField(blank=True, help_text="Terms and conditions for the quote")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'

    def __str__(self):
        return f"Quote #{self.quote_number} - {self.client.name}"

    def get_absolute_url(self):
        return reverse('documents:quote_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Calculate tax amount and total if not set
        if self.tax_rate and self.subtotal:
            self.tax_amount = self.subtotal * (self.tax_rate / 100)
            self.total_amount = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)

    def generate_pdf(self):
        if not self.pdf_file:
            pdf_path = generate_quote_pdf(self)
            self.pdf_file = pdf_path
            self.save()
        return self.pdf_file

class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"