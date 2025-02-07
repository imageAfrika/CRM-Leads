from django.db import models
from django.urls import reverse
from clients.models import Client
from .utils import generate_quote_pdf
from django.core.files import File
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

class Document(models.Model):

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
    document_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quote = models.OneToOneField('Quote', on_delete=models.CASCADE, null=True, blank=True)

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
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)

        # Draw things on the PDF
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, f"Quote #{self.quote_number}")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 720, f"Date: {self.created_at.strftime('%Y-%m-%d')}")
        p.drawString(50, 700, f"Valid Until: {self.valid_until.strftime('%Y-%m-%d')}")
        
        # Client Information
        p.drawString(50, 670, "Client Information:")
        p.drawString(70, 650, f"Name: {self.client.name}")
        p.drawString(70, 630, f"Email: {self.client.email}")
        
        # Items
        p.drawString(50, 590, "Items:")
        y = 570
        for item in self.items.all():
            p.drawString(70, y, f"{item.description}")
            p.drawString(300, y, f"Qty: {item.quantity}")
            p.drawString(400, y, f"Price: ${item.unit_price}")
            p.drawString(500, y, f"Total: ${item.get_total()}")
            y -= 20
        
        # Totals
        p.drawString(400, 200, f"Subtotal: ${self.subtotal}")
        p.drawString(400, 180, f"Tax: ${self.tax_amount}")
        p.drawString(400, 160, f"Total: ${self.total_amount}")
        
        # Terms
        if self.terms:
            p.drawString(50, 120, "Terms and Conditions:")
            p.drawString(70, 100, self.terms)

        # Close the PDF object cleanly
        p.showPage()
        p.save()

        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()

        # Save the PDF to the model's file field
        filename = f'quote_{self.quote_number}.pdf'
        filepath = os.path.join('quotes', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, 'quotes', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(pdf)
        
        # Update the pdf_file field
        self.pdf_file.name = filepath
        self.save()
        
        return self.pdf_file

class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def get_total(self):
        return self.quantity * self.unit_price * (1 - self.discount/100)

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"