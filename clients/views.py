from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client
from django.http import HttpResponseRedirect

# Create your views here.

class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

class ClientCreateView(CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'contact_person', 'email', 'phone', 'address', 'notes']
    success_url = reverse_lazy('clients:client_list')

class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'contact_person', 'email', 'phone', 'address', 'notes']
    success_url = reverse_lazy('clients:client_list')

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

