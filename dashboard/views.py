from django.views.generic import TemplateView
from clients.models import Client
from sales.models import Sale
from documents.models import Document, Quote

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = Client.objects.count()
        context['total_sales'] = Sale.objects.count()
        context['total_documents'] = Document.objects.count()
        context['recent_sales'] = Sale.objects.order_by('-sale_date')[:5]
        context['recent_clients'] = Client.objects.order_by('-created_at')[:5]
        context['recent_documents'] = Document.objects.order_by('-created_at')[:5]
        context['recent_quotes'] = Quote.objects.filter(status='DRAFT').order_by('-created_at')[:5]
        return context 