from django.views.generic import CreateView, DetailView, ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .models import Quote, Document, QuoteItem, Client
from .forms import QuoteForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from clients.models import Client
import json
from django.utils import timezone
from datetime import timedelta

def generate_quote_number():
    # Get today's date in YYYYMMDD format
    today = timezone.now().strftime('%Y%m%d')
    
    # Get the last quote number for today
    last_quote = Quote.objects.filter(
        quote_number__startswith=f'Q{today}'
    ).order_by('-quote_number').first()
    
    if last_quote:
        # Extract the sequence number and increment it
        seq_num = int(last_quote.quote_number[-3:]) + 1
    else:
        seq_num = 1
    
    # Format: Q + YYYYMMDD + 3-digit sequence number
    return f'Q{today}{seq_num:03d}'

def quote_create(request):
    try:
        # Extract data from request
        data = request.POST
        items_data = json.loads(data.get('items', '[]'))
        
        # Set valid_until to 30 days from now by default
        valid_until = timezone.now() + timedelta(days=30)
        
        # Generate unique quote number
        quote_number = generate_quote_number()
        
        # Create quote
        quote = Quote.objects.create(
            client_id=data.get('client'),
            quote_number=quote_number,
            title=data.get('quote_title'),
            description=data.get('description', ''),
            subtotal=Decimal(data.get('subtotal', '0')),
            tax_amount=Decimal(data.get('tax_amount', '0')),
            total_amount=Decimal(data.get('total_amount', '0')),
            terms=data.get('terms', ''),
            created_at=timezone.now(),
            valid_until=valid_until
        )
        
        # Create quote items
        for item_data in items_data:
            QuoteItem.objects.create(
                quote=quote,
                description=item_data['description'],
                quantity=Decimal(item_data['quantity']),
                unit_price=Decimal(item_data['unit_price']),
                discount=Decimal(item_data['discount'])
            )
        
        # Create document
        document = Document.objects.create(
            title=f"Quote - {quote.quote_number}",
            document_type='QUOTE',
            client_id=data.get('client'),
            description=quote.description,
            document_date=quote.created_at,
            total_amount=quote.total_amount,
            quote=quote
        )
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('documents:document_list')
        })
        
    except Exception as e:
        print(f"Error creating quote: {str(e)}")  # For debugging
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
    template_name = 'documents/quote_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        print("GET request received")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("POST request received")
        print("POST data:", request.POST)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        quote = form.save()
        # Create a Document instance linked to this quote
        Document.objects.create(
            title=f"Quote - {quote.quote_number}",
            document_type='QUOTE',
            client=quote.client,
            description=quote.description,
            document_date=quote.created_at,
            total_amount=quote.total_amount,
            quote=quote
        )
        return redirect('documents:document_list')

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
        pdf_file = quote.generate_pdf()
        return JsonResponse({
            'success': True,
            'pdf_url': pdf_file.url
        })
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")  # For debugging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_quote_number(request):
    quote_number = generate_quote_number()
    return JsonResponse({'quote_number': quote_number})

def generate_invoice_from_quote(request, quote_id):
    try:
        quote = get_object_or_404(Quote, id=quote_id)
        
        # Create invoice number (similar to quote number but with 'INV' prefix)
        today = timezone.now().strftime('%Y%m%d')
        last_invoice = Document.objects.filter(
            document_type='INVOICE',
            title__startswith=f'INV{today}'
        ).order_by('-title').first()
        
        if last_invoice:
            seq_num = int(last_invoice.title[-3:]) + 1
        else:
            seq_num = 1
            
        invoice_number = f'INV{today}{seq_num:03d}'
        
        # Create invoice document
        invoice = Document.objects.create(
            title=invoice_number,
            document_type='INVOICE',
            client=quote.client,
            description=quote.description,
            document_date=timezone.now(),
            total_amount=quote.total_amount,
            quote=quote  # Link to original quote
        )
        
        # Create invoice items (if you have a separate InvoiceItem model)
        # for quote_item in quote.items.all():
        #     InvoiceItem.objects.create(
        #         invoice=invoice,
        #         description=quote_item.description,
        #         quantity=quote_item.quantity,
        #         unit_price=quote_item.unit_price,
        #         discount=quote_item.discount
        #     )
        
        return JsonResponse({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice_id': invoice.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)