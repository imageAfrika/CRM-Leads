from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Sale, SaleItem
from documents.models import Document
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.utils import timezone
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.core.files.base import ContentFile
import io
from clients.models import Client

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

def generate_receipt_pdf(sale, document):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw the receipt content
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, 10*inch, "Sales Receipt")
    
    # Company Info
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 9.5*inch, "Your Company Name")
    p.drawString(1*inch, 9.3*inch, "Your Company Address")
    p.drawString(1*inch, 9.1*inch, "Phone: Your Company Phone")
    p.drawString(1*inch, 8.9*inch, "Email: your@email.com")
    
    # Receipt Info
    p.drawString(1*inch, 8.3*inch, f"Receipt #: {document.title}")
    p.drawString(1*inch, 8.1*inch, f"Date: {sale.sale_date.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(1*inch, 7.9*inch, f"Client: {sale.client.name}")
    p.drawString(1*inch, 7.7*inch, f"Payment Method: {sale.get_payment_method_display()}")
    p.drawString(1*inch, 7.5*inch, f"Payment Status: {sale.get_payment_status_display()}")
    
    # Items Header
    y = 7.0
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y*inch, "Description")
    p.drawString(3.5*inch, y*inch, "Qty")
    p.drawString(4.5*inch, y*inch, "Price")
    p.drawString(5.5*inch, y*inch, "Discount")
    p.drawString(6.5*inch, y*inch, "Total")
    
    # Items
    p.setFont("Helvetica", 12)
    y -= 0.3
    for item in sale.items.all():
        p.drawString(1*inch, y*inch, str(item.description))
        p.drawString(3.5*inch, y*inch, str(item.quantity))
        p.drawString(4.5*inch, y*inch, f"${item.unit_price}")
        p.drawString(5.5*inch, y*inch, f"{item.discount}%")
        p.drawString(6.5*inch, y*inch, f"${item.get_total()}")
        y -= 0.25
    
    # Totals
    y -= 0.5
    p.setFont("Helvetica-Bold", 12)
    p.drawString(5*inch, y*inch, f"Subtotal: ${sale.subtotal}")
    y -= 0.25
    p.drawString(5*inch, y*inch, f"Tax: ${sale.tax_amount}")
    y -= 0.25
    p.drawString(5*inch, y*inch, f"Total: ${sale.total_amount}")
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(3*inch, 1*inch, "Thank you for your business!")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create a Django File object
    return ContentFile(pdf, name=f'receipt_{document.title}.pdf')

def direct_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)
            
            # Create sale record
            sale = Sale.objects.create(
                client_id=data['client_id'],
                payment_method=data['payment_method'],
                payment_status=data['payment_status'],
                subtotal=Decimal(data['subtotal']),
                tax_amount=Decimal(data['tax_amount']),
                total_amount=Decimal(data['total_amount'])
            )
            
            # Create sale items
            for item in data['items']:
                SaleItem.objects.create(
                    sale=sale,
                    description=item['description'],
                    quantity=Decimal(item['quantity']),
                    unit_price=Decimal(item['unit_price']),
                    discount=Decimal(item['discount'])
                )
            
            # Generate receipt number
            receipt_number = f'RCP-{timezone.now().strftime("%Y%m%d")}-{sale.id:04d}'
            
            # Create receipt document
            document = Document.objects.create(
                title=f"Sales Receipt #{receipt_number}",
                document_type='RECEIPT',
                client_id=data['client_id'],
                description=f"Direct sale receipt",
                document_date=timezone.now(),
                total_amount=Decimal(data['total_amount']),
                tax_amount=Decimal(data['tax_amount']),
                subtotal=Decimal(data['subtotal']),
                status='PAID' if data['payment_status'] == 'PAID' else 'PENDING'
            )
            
            # Generate PDF receipt
            pdf_file = generate_receipt_pdf(sale, document)
            document.file.save(f'receipt_{receipt_number}.pdf', pdf_file)
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('sales:sale_detail', args=[sale.id])
            })
            
        except Exception as e:
            import traceback
            print("Error:", str(e))
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    else:
        clients = Client.objects.all()
        tax_rate = 15
        return render(request, 'sales/direct_sale.html', {
            'clients': clients,
            'tax_rate': tax_rate
        })
