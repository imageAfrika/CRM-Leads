from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Sale

# Create your views here.

class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'

class SaleDetailView(DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'

class SaleCreateView(CreateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    fields = ['client', 'sale_date', 'amount', 'description']
    success_url = reverse_lazy('sales:sale_list')

class SaleUpdateView(UpdateView):
    model = Sale
    template_name = 'sales/sale_form.html'
    fields = ['client', 'sale_date', 'amount', 'description']
    success_url = reverse_lazy('sales:sale_list')

class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sale_list')
