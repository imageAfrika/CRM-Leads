from django.db import models
from clients.models import Client
from documents.models import Document
from django.urls import reverse

# Create your models here.
class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sale_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.name} - {self.sale_date}"

    def get_absolute_url(self):
        return reverse('sales:sale_detail', kwargs={'pk': self.pk})


