from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import string
import random
from decimal import Decimal

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, help_text="Unique project code/reference number")
    description = models.TextField(blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.SET_NULL, null=True, related_name='projects')
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Financial Information
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Team
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    team_members = models.ManyToManyField(User, related_name='assigned_projects', blank=True)
    
    # Additional Information
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    notes = models.TextField(blank=True)
    
    # Metrics
    completion_percentage = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("view_project_dashboard", "Can view project dashboard"),
            ("manage_project_team", "Can manage project team"),
            ("view_project_analytics", "Can view project analytics"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_absolute_url(self):
        return reverse('project_management:project_detail', args=[str(self.id)])

    @property
    def total_income(self):
        """Calculate total income from income transactions"""
        income = sum(t.amount for t in self.transactions.filter(transaction_type='income'))
        return income or Decimal('0.00')

    @property
    def total_budget(self):
        return self.budget or 0
        
    @property
    def total_expenses(self):
        """Calculate total expenses from expense transactions and actual_cost"""
        expenses = sum(t.amount for t in self.transactions.filter(transaction_type='expense'))
        return expenses or self.actual_cost or Decimal('0.00')
        
    @property
    def remaining_budget(self):
        return (self.budget or 0) - (self.actual_cost or 0)
        
    @property
    def budget_utilization(self):
        if not self.budget or self.budget == 0:
            return 0
        return min(100, int((self.actual_cost or 0) / self.budget * 100))

    def get_budget_utilization(self):
        if not self.budget or not self.actual_cost:
            return 0
        return (self.actual_cost / self.budget) * 100

    def is_overdue(self):
        if not self.end_date:
            return False
        return self.end_date < timezone.now().date() and self.status != 'completed'

    def get_total_expenses(self):
        return sum(expense.amount for expense in self.expenses.all())

    def get_total_invoices(self):
        return sum(invoice.total_amount for invoice in self.invoices.all())

    def get_profit_margin(self):
        total_income = self.get_total_invoices()
        total_expenses = self.get_total_expenses()
        if not total_income:
            return 0
        return ((total_income - total_expenses) / total_income) * 100
    
    def get_project_account(self):
        """Get the financial account associated with this project"""
        return self.accounts.first()
    
    def get_financial_summary(self):
        """Get the financial summary for this project"""
        from banking.models import ProjectFinancialSummary
        try:
            return self.financial_summary
        except ProjectFinancialSummary.DoesNotExist:
            return ProjectFinancialSummary.objects.create(
                project=self,
                total_revenue=0,
                total_expenses=0,
                total_profit=0
            )
    
    def update_financial_summary(self):
        """Update the financial summary for this project"""
        account = self.get_project_account()
        if account:
            summary = self.get_financial_summary()
            summary.total_revenue = account.get_revenue()
            summary.total_expenses = account.get_expenditure()
            summary.total_profit = account.get_profit_loss()
            summary.save()
            return summary
        return None

class ProjectDocument(models.Model):
    DOCUMENT_TYPES = [
        ('contract', 'Contract'),
        ('proposal', 'Proposal'),
        ('specification', 'Specification'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='project_documents/%Y/%m/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.project.code} - {self.title}"

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.project.code} - {self.title}"

class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.project.code} - {self.title}"

    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now().date()

def generate_account_number():
    """Generate a random account number for project accounts"""
    prefix = 'PRJ'
    numbers = ''.join(random.choice(string.digits) for _ in range(10))
    return f"{prefix}{numbers}"

@receiver(post_save, sender=Project)
def create_project_account(sender, instance, created, **kwargs):
    """Create a financial account when a new project is created"""
    if created:
        from banking.models import Account
        
        # Check if a main company account exists, create one if not
        main_account = Account.objects.filter(is_main_company_account=True).first()
        if not main_account:
            main_account = Account.objects.create(
                account_number=f"COMP{''.join(random.choice(string.digits) for _ in range(10))}",
                account_type='COMPANY',
                owner=instance.manager or User.objects.filter(is_superuser=True).first(),
                pin='1234',  # Default PIN, should be changed
                is_main_company_account=True
            )
        
        # Create a project account
        Account.objects.create(
            account_number=generate_account_number(),
            account_type='PROJECT',
            owner=instance.manager or User.objects.filter(is_superuser=True).first(),
            pin='1234',  # Default PIN, should be changed
            project=instance
        )

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    description = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.description}"
