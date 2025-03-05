from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('SAVINGS', 'Savings Account'),
        ('CHECKING', 'Checking Account'),
        ('CREDIT', 'Credit Account'),
        ('LOAN', 'Loan Account'),
    )
    
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    pin = models.CharField(max_length=4, help_text="4-digit PIN for transactions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_type} - {self.account_number}"
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.save()
        Transaction.objects.create(
            account=self,
            transaction_type='DEPOSIT',
            amount=amount,
            description=f"Deposit to {self.account_number}"
        )
        return True
    
    def withdraw(self, amount, pin):
        if pin != self.pin:
            raise ValueError("Invalid PIN")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()
        Transaction.objects.create(
            account=self,
            transaction_type='WITHDRAWAL',
            amount=amount,
            description=f"Withdrawal from {self.account_number}"
        )
        return True
    
    def transfer(self, destination_account, amount, pin):
        if pin != self.pin:
            raise ValueError("Invalid PIN")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        destination_account.balance += amount
        self.save()
        destination_account.save()
        
        # Create transaction records for both accounts
        Transaction.objects.create(
            account=self,
            transaction_type='TRANSFER_OUT',
            amount=amount,
            description=f"Transfer to {destination_account.account_number}",
            related_account=destination_account
        )
        Transaction.objects.create(
            account=destination_account,
            transaction_type='TRANSFER_IN',
            amount=amount,
            description=f"Transfer from {self.account_number}",
            related_account=self
        )
        return True

class Debt(models.Model):
    DEBT_TYPES = (
        ('LOAN', 'Loan'),
        ('CREDIT', 'Credit Card'),
        ('MORTGAGE', 'Mortgage'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='debts')
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPES)
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.debt_type} - {self.account.account_number}"
    
    def calculate_interest(self):
        # Calculate monthly interest
        monthly_rate = self.interest_rate / 12 / 100
        return self.remaining_amount * monthly_rate

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('PAYMENT', 'Payment'),
        ('FEE', 'Fee'),
        ('INTEREST', 'Interest'),
        ('TAX', 'Tax'),
    )
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_transactions')
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Tax(models.Model):
    TAX_TYPES = (
        ('INCOME', 'Income Tax'),
        ('TRANSACTION', 'Transaction Tax'),
        ('INTEREST', 'Interest Tax'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='taxes')
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    date_applied = models.DateField()
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='taxes', null=True, blank=True)
    
    def __str__(self):
        return f"{self.tax_type} - {self.amount} - {self.date_applied}"
