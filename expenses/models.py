from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from authentication.models import Profile
from django.utils import timezone

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_categories')
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='categories')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card'),
        ('CHEQUE', 'Cheque'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(
        ExpenseCategory, 
        on_delete=models.SET_NULL,
        null=True
    )
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='CASH'
    )
    description = models.TextField(blank=True)
    receipt = models.FileField(
        upload_to='expenses/receipts/%Y/%m/',
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.date})"

class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    next_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.frequency}"

    def get_next_date(self):
        """Calculate the next occurrence date based on frequency"""
        if not self.is_active:
            return None
            
        today = timezone.now().date()
        if self.end_date and self.end_date < today:
            return None
            
        last_date = max(self.start_date, today)
        
        if self.frequency == 'monthly':
            next_date = last_date.replace(day=self.start_date.day)
            if next_date <= today:
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
        elif self.frequency == 'quarterly':
            months_ahead = 3 - ((last_date.month - self.start_date.month) % 3)
            next_date = last_date + timezone.timedelta(days=months_ahead * 30)
            next_date = next_date.replace(day=self.start_date.day)
        else:  # yearly
            next_date = last_date.replace(day=self.start_date.day, month=self.start_date.month)
            if next_date <= today:
                next_date = next_date.replace(year=next_date.year + 1)
                
        return next_date if not self.end_date or next_date <= self.end_date else None

    def create_expense(self):
        """Create a new expense instance from this recurring expense"""
        if not self.is_active:
            return None
            
        next_date = self.get_next_date()
        if not next_date:
            return None
            
        expense = Expense.objects.create(
            title=self.title,
            amount=self.amount,
            category=self.category,
            date=next_date,
            description=f"Auto-generated from recurring expense: {self.title}",
            created_by=self.created_by,
            profile=self.profile
        )
        return expense
