from django.db import models
from django.urls import reverse


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('clients:client_detail', kwargs={'pk': self.pk})

