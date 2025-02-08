from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Sale, SaleItem
from documents.models import Document
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.utils import timezone
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.core.files.base import ContentFile
from io import BytesIO
from clients.models import Client
from django.db import transaction
from django.conf import settings

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
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, 9*inch, "Sales Receipt")
    
    # Receipt Info
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 8.3*inch, f"Receipt #: {document.get_document_number()}")
    p.drawString(1*inch, 8*inch, f"Date: {document.document_date.strftime('%Y-%m-%d')}")
    p.drawString(1*inch, 7.7*inch, f"Client: {document.client.name}")
    p.drawString(1*inch, 7.4*inch, f"Payment Method: {sale.get_payment_method_display()}")
    
    # Items Header
    y_position = 7*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y_position, "Description")
    p.drawString(3.5*inch, y_position, "Quantity")
    p.drawString(4.5*inch, y_position, "Unit Price")
    p.drawString(5.5*inch, y_position, "Total")
    
    # Items
    y_position -= 0.3*inch
    p.setFont("Helvetica", 12)
    for item in sale.items.all():
        p.drawString(1*inch, y_position, item.description[:30])
        p.drawString(3.5*inch, y_position, f"{item.quantity}")
        p.drawString(4.5*inch, y_position, f"${item.unit_price:.2f}")
        item_total = item.get_total()
        p.drawString(5.5*inch, y_position, f"${item_total:.2f}")
        y_position -= 0.25*inch
    
    # Totals
    y_position -= 0.3*inch
    p.drawString(4*inch, y_position, "Subtotal:")
    p.drawString(5.5*inch, y_position, f"${sale.subtotal:.2f}")
    
    y_position -= 0.25*inch
    p.drawString(4*inch, y_position, f"Tax ({document.tax_rate}%):")
    p.drawString(5.5*inch, y_position, f"${sale.tax_amount:.2f}")
    
    y_position -= 0.25*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(4*inch, y_position, "Total:")
    p.drawString(5.5*inch, y_position, f"${sale.total_amount:.2f}")
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(1*inch, 1*inch, "Thank you for your business!")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    return ContentFile(pdf)

def direct_sale_form(request):
    """Render the direct sale form"""
    clients = Client.objects.all()
    tax_rate = 15
    return render(request, 'sales/direct_sale.html', {
        'clients': clients,
        'tax_rate': tax_rate
    })

@require_POST
def direct_sale_create(request):
    """Handle the direct sale form submission"""
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            # Create the sale
            sale = Sale.objects.create(
                client_id=data['client_id'],
                payment_method=data['payment_method'],
                payment_status=data['payment_status'],
                include_tax=data['include_tax'],
                subtotal=Decimal(str(data['subtotal'])),
                tax_amount=Decimal(str(data['tax_amount'])),
                total_amount=Decimal(str(data['total_amount']))
            )
            
            # Then create all sale items
            sale_items = []
            for item in data['items']:
                sale_items.append(SaleItem(
                    sale=sale,
                    description=item['description'],
                    quantity=Decimal(str(item['quantity'])),
                    unit_price=Decimal(str(item['unit_price'])),
                    discount=Decimal(str(item['discount']))
                ))
            
            # Bulk create all items
            SaleItem.objects.bulk_create(sale_items)
            
            return JsonResponse({
                'success': True,
                'redirect_url': sale.get_absolute_url()
            })
            
    except Exception as e:
        import traceback
        print("Error:", str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def sale_list(request):
    sales = Sale.objects.all().order_by('-created_at')
    return render(request, 'sales/sale_list.html', {'sales': sales})

def generate_receipt(request, pk):
    try:
        sale = get_object_or_404(Sale.objects.prefetch_related('items'), pk=pk)
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Create the list of flowables for the document
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add the receipt header
        elements.append(Paragraph("RECEIPT", title_style))
        elements.append(Paragraph(f"Receipt #{sale.pk}", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Add company info
        elements.append(Paragraph("Company Information", styles['Heading3']))
        elements.append(Paragraph(settings.COMPANY_NAME, styles['Normal']))
        elements.append(Paragraph(settings.COMPANY_ADDRESS, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Add client info
        elements.append(Paragraph("Client Information", styles['Heading3']))
        elements.append(Paragraph(f"Client: {sale.client.name}", styles['Normal']))
        elements.append(Paragraph(f"Date: {timezone.localtime(sale.sale_date).strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Payment Method: {sale.get_payment_method_display()}", styles['Normal']))
        elements.append(Paragraph(f"Status: {sale.get_payment_status_display()}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Create items table
        table_data = [['Description', 'Quantity', 'Unit Price', 'Discount', 'Total']]
        for item in sale.items.all():
            table_data.append([
                item.description,
                str(item.quantity),
                f"${item.unit_price:.2f}",
                f"{item.discount}%",
                f"${item.get_total():.2f}"
            ])
            
        # Add totals
        table_data.extend([
            ['', '', '', 'Subtotal:', f"${sale.subtotal:.2f}"],
            ['', '', '', f"Tax ({sale.tax_rate}%):", f"${sale.tax_amount:.2f}"],
            ['', '', '', 'Total:', f"${sale.total_amount:.2f}"]
        ])
        
        # Create and style the table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (-2, -3), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEBELOW', (-2, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Add thank you message
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))
        
        # Build the PDF document
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the HTTP response with PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{sale.pk}.pdf"'
        response.write(pdf)
        
        return response

    except Exception as e:
        print(f"Receipt Generation Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def preview_receipt(request, pk):
    sale = get_object_or_404(Sale.objects.prefetch_related('items'), pk=pk)
    return render(request, 'sales/receipt_preview.html', {
        'sale': sale,
        'company_name': settings.COMPANY_NAME,
        'company_address': settings.COMPANY_ADDRESS,
        'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
        'company_email': getattr(settings, 'COMPANY_EMAIL', ''),
    })
