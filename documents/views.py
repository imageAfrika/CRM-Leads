from django.views.generic import CreateView, DetailView, ListView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from .models import Quote, Document, QuoteItem
from .forms import QuoteForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal

def quote_create(request):
    try:
        # Extract data from request
        data = request.POST
        
        # Create quote
        quote = Quote.objects.create(
            client_id=data.get('client'),
            quote_number=data.get('quote_number'),
            title=data.get('title'),
            description=data.get('description'),
            subtotal=Decimal(data.get('subtotal', '0')),
            tax_rate=Decimal(data.get('tax_rate', '0')),
            valid_until=data.get('valid_until'),
            terms=data.get('terms', '')
        )
        
        # Create quote items
        items_data = request.POST.getlist('items[]')
        for item_data in items_data:
            QuoteItem.objects.create(
                quote=quote,
                description=item_data.get('description'),
                quantity=Decimal(item_data.get('quantity')),
                unit_price=Decimal(item_data.get('unit_price'))
            )
        
        # Generate PDF
        pdf_url = quote.generate_pdf()
        
        return JsonResponse({
            'success': True,
            'quote_id': quote.id,
            'pdf_url': pdf_url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, 'documents/quote_detail.html', {'quote': quote})

class QuoteCreateView(CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'documents/quote_form.html'
    success_url = reverse_lazy('documents:quote_detail')

    def get(self, request, *args, **kwargs):
        print("GET request received")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("POST request received")
        print("POST data:", request.POST)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("Form is valid")
        quote = form.save()
        print("Quote saved:", quote)
        return render(self.request, 'documents/quote.html', {'quote': quote})

    def form_invalid(self, form):
        print("Form is invalid")
        print("Form errors:", form.errors)
        return super().form_invalid(form)

class QuoteDetailView(DetailView):
    model = Quote
    template_name = 'documents/quote_detail.html'
    context_object_name = 'quote'

    def get_success_url(self):
        return reverse_lazy('documents:quote_detail', kwargs={'pk': self.object.pk})

class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

@require_POST
def generate_quote_pdf(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    try:
        pdf_url = quote.generate_pdf()
        return JsonResponse({
            'success': True,
            'pdf_url': pdf_url.url
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)