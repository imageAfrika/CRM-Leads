from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .models import Quote, Document, QuoteItem, Client, Expenditure
from .forms import QuoteForm
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from clients.models import Client
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.conf import settings
import tempfile
import os
import pdfkit
from django.utils.dateparse import parse_date

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

@require_POST
def quote_create(request):
    try:
        data = json.loads(request.body)
        
        # Create the quote
        quote = Quote.objects.create(
            client_id=data['client_id'],
            quote_number=data['quote_number'],
            title=data['title'],
            description=data.get('description', ''),
            subtotal=Decimal(data['subtotal']),
            tax_rate=Decimal(data['tax_rate']),
            tax_amount=Decimal(data['tax_amount']),
            total_amount=Decimal(data['total_amount']),
            valid_until=parse_date(data['valid_until']),
            terms=data.get('terms', '')
        )
        
        # Generate PDF for the quote
        pdf_file = quote.generate_pdf()
        quote.pdf_file = pdf_file
        quote.save()
        
        return JsonResponse({
            'success': True,
            'quote_id': quote.id,
            'redirect_url': reverse('documents:quote_detail', args=[quote.id])
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
    
    def get_queryset(self):
        queryset = Document.objects.all().order_by('-created_at')
        
        # Filter by document type
        doc_type = self.request.GET.get('type')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type.upper())
            
        # Filter by date
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(created_at__date=date)
            
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(document_number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(notes__icontains=search)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc_type = self.request.GET.get('type', '').upper()
        
        # Add document type to context for template
        context['current_type'] = doc_type
        context['title'] = f"{doc_type.title()}s" if doc_type else "All Documents"
        
        return context

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

@require_POST
def generate_invoice_from_quote(request, quote_id):
    try:
        quote = get_object_or_404(Quote, pk=quote_id)
        
        # Check if quote can be converted to invoice
        if quote.status not in ['DRAFT', 'SENT']:
            raise ValueError('This quote cannot be converted to an invoice')
            
        # Generate invoice number
        today = timezone.now().strftime('%Y%m%d')
        last_invoice = Document.objects.filter(
            document_type='INVOICE',
            invoice_number__startswith=f'INV-{today}'
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
            
        invoice_number = f'INV-{today}-{new_number:04d}'
        
        # Create new invoice
        invoice = Document.objects.create(
            client=quote.client,
            title=f"Invoice for {quote.quote_number}",
            document_type='INVOICE',
            invoice_number=invoice_number,
            description=quote.description,
            subtotal=quote.subtotal,
            tax_rate=quote.tax_rate,
            tax_amount=quote.tax_amount,
            total_amount=quote.total_amount,
            status='DRAFT',
            quote=quote  # Link back to original quote
        )
        
        # Update quote status
        quote.status = 'INVOICED'
        quote.save()
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('documents:document_detail', args=[invoice.pk])
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # For debugging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

class DocumentUpdateView(UpdateView):
    model = Document
    template_name = 'documents/document_form.html'
    fields = ['title', 'description', 'client', 'document_type', 'status', 'total_amount']
    
    def get_success_url(self):
        return reverse_lazy('documents:document_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add any additional processing here if needed
        return response

def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Use the print-specific template
    return render(request, 'documents/document_print.html', {
        'document': document
    })

def expenditure_view(request):
    expenses = Expenditure.objects.all()
    
    # Apply filters
    category = request.GET.get('category')
    month = request.GET.get('month')
    search = request.GET.get('search')
    
    if category:
        expenses = expenses.filter(category=category)
    
    if month:
        year, month = month.split('-')
        expenses = expenses.filter(date__year=year, date__month=month)
    
    if search:
        expenses = expenses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'documents/expenditure.html', {
        'expenses': expenses,
        'category_choices': Expenditure.CATEGORY_CHOICES,
        'total_amount': total_amount
    })

@require_POST
def expenditure_create(request):
    try:
        expense = Expenditure.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            amount=request.POST['amount'],
            category=request.POST['category'],
            date=request.POST['date'],
            notes=request.POST.get('notes', '')
        )
        
        if 'receipt' in request.FILES:
            expense.receipt = request.FILES['receipt']
            expense.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def expenditure_edit(request, pk):
    try:
        expense = get_object_or_404(Expenditure, pk=pk)
        
        # Update expense fields
        expense.title = request.POST['title']
        expense.description = request.POST['description']
        expense.amount = request.POST['amount']
        expense.category = request.POST['category']
        expense.date = request.POST['date']
        expense.notes = request.POST.get('notes', '')
        
        # Handle receipt file if provided
        if 'receipt' in request.FILES:
            expense.receipt = request.FILES['receipt']
        
        expense.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_POST
def expenditure_delete(request, pk):
    try:
        expense = get_object_or_404(Expenditure, pk=pk)
        expense.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def invoice_list(request):
    invoices = Document.objects.filter(document_type='INVOICE').order_by('-created_at')
    total_revenue = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    
    return render(request, 'documents/invoice_list.html', {
        'invoices': invoices,
        'total_revenue': total_revenue
    })