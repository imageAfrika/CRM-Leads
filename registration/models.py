from django.db import models
from django.conf import settings
from django.utils import timezone

def company_logo_path(instance, filename):
    """
    Generate a unique path for company logos.
    Format: company_logos/company_id/filename
    """
    return f'company_logos/{instance.id}/{filename}'

class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Debit/Credit Card'),
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
    ]
    
    name = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    account_number = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()} - {self.account_name}"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_annually = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name='Company Name')
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    email = models.EmailField(verbose_name='Email Address')
    logo = models.ImageField(upload_to=company_logo_path, null=True, blank=True, verbose_name='Company Logo')
    tax_pin = models.CharField(max_length=50, verbose_name='Tax PIN')
    physical_address = models.TextField(verbose_name='Physical Address')
    postal_address = models.CharField(max_length=100, null=True, blank=True, verbose_name='Postal Address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    database_name = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=3, default='KES')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_companies'
    )

    def __str__(self):
        return self.name

class Subscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.amount} - {self.status}"
