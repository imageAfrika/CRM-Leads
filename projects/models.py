from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Quotation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])

    def __str__(self):
        return f'Quotation for {self.project.name}'

class Invoice(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_status = models.CharField(max_length=50, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')])

    def __str__(self):
        return f'Invoice for {self.project.name}'

class JobCard(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_description = models.TextField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])

    def __str__(self):
        return f'Job Card for {self.project.name}'

class PurchaseOrder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Purchase Order for {self.project.name}'

class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f'Expense for {self.project.name}'
