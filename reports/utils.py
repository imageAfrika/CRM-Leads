from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
import os
import csv
import json
from io import BytesIO
import tempfile
from datetime import datetime, timedelta
import uuid

# PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
except ImportError:
    # Handle case where reportlab is not installed
    pass

# Excel generation
try:
    import xlsxwriter
except ImportError:
    # Handle case where xlsxwriter is not installed
    pass


def generate_chart_data(report_config):
    """
    Generate chart data based on report configuration.
    This function processes the data according to the report type and filters.
    """
    from django.db.models import Sum, Count, Avg, Max, Min
    
    report_type = report_config.report_type
    time_range = report_config.time_range
    filters = report_config.filters or {}
    
    # Default empty data structure
    data = {
        'labels': [],
        'datasets': [{
            'label': 'No Data',
            'data': [],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }

    # Process data based on report type
    if report_type == 'BANKING':
        data = generate_banking_report_data(report_config)
    elif report_type == 'SALES':
        data = generate_sales_report_data(report_config)
    elif report_type == 'EXPENSES':
        data = generate_expenses_report_data(report_config)
    elif report_type == 'CLIENTS':
        data = generate_clients_report_data(report_config)
    elif report_type == 'LEADS':
        data = generate_leads_report_data(report_config)
    
    return data


def get_chart_colors(report_config):
    """
    Get chart colors based on the report configuration and user settings.
    """
    # Default colors
    default_colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#5a5c69', '#858796', '#6610f2', '#fd7e14', '#20c9a6'
    ]
    
    # Use custom colors if available
    if hasattr(report_config, 'custom_colors') and report_config.custom_colors:
        return list(report_config.custom_colors.values())
    
    # Use user settings if available
    if hasattr(report_config.report.created_by, 'report_settings'):
        settings = report_config.report.created_by.report_settings
        if settings.color_scheme == 'PASTEL':
            return ['#FFB6C1', '#FFD700', '#98FB98', '#87CEFA', '#DDA0DD', '#FFDAB9', '#B0E0E6', '#F0E68C', '#E6E6FA', '#FFA07A']
        elif settings.color_scheme == 'VIBRANT':
            return ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FF8000', '#8000FF', '#0080FF', '#FF0080']
        elif settings.color_scheme == 'MONOCHROME':
            return ['#000000', '#1A1A1A', '#333333', '#4D4D4D', '#666666', '#808080', '#999999', '#B3B3B3', '#CCCCCC', '#E6E6E6']
    
    return default_colors


def generate_banking_report_data(report_config):
    """
    Generate data for banking reports.
    """
    # This is a placeholder - implement actual data retrieval logic
    return {
        'labels': ['January', 'February', 'March', 'April', 'May', 'June'],
        'datasets': [{
            'label': 'Banking Transactions',
            'data': [1000, 1500, 1200, 1800, 2000, 2500],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }


def generate_sales_report_data(report_config):
    """
    Generate data for sales reports.
    """
    # This is a placeholder - implement actual data retrieval logic
    return {
        'labels': ['January', 'February', 'March', 'April', 'May', 'June'],
        'datasets': [{
            'label': 'Sales',
            'data': [5000, 6000, 7000, 8000, 9000, 10000],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }


def generate_expenses_report_data(report_config):
    """
    Generate data for expenses reports.
    """
    # This is a placeholder - implement actual data retrieval logic
    return {
        'labels': ['January', 'February', 'March', 'April', 'May', 'June'],
        'datasets': [{
            'label': 'Expenses',
            'data': [3000, 2800, 3200, 3500, 3100, 3800],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }


def generate_clients_report_data(report_config):
    """
    Generate data for client reports.
    """
    # This is a placeholder - implement actual data retrieval logic
    return {
        'labels': ['New', 'Active', 'Inactive', 'Churned'],
        'datasets': [{
            'label': 'Client Status',
            'data': [50, 200, 30, 20],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }


def generate_leads_report_data(report_config):
    """
    Generate data for leads reports.
    """
    # This is a placeholder - implement actual data retrieval logic
    return {
        'labels': ['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Closed'],
        'datasets': [{
            'label': 'Lead Status',
            'data': [100, 80, 60, 40, 30, 20],
            'backgroundColor': get_chart_colors(report_config),
            'borderColor': get_chart_colors(report_config),
            'borderWidth': 1
        }]
    }


def export_report_to_pdf(report):
    """
    Export a report to a PDF file.
    """
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add report title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(report.name, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add report description if available
    if report.description:
        elements.append(Paragraph(report.description, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # Add metadata
    elements.append(Paragraph(f"Created by: {report.created_by.username}", styles['Normal']))
    elements.append(Paragraph(f"Created on: {report.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Last updated: {report.updated_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # Add chart data as a table
    if hasattr(report, 'configuration'):
        config = report.configuration
        chart_data = generate_chart_data(config)
        
        # Create table data
        table_data = [['Label', 'Value']]
        for i, label in enumerate(chart_data['labels']):
            if i < len(chart_data['datasets'][0]['data']):
                table_data.append([label, chart_data['datasets'][0]['data'][i]])
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response


def export_report_to_excel(report):
    """
    Export a report to an Excel file.
    """
    # Create a BytesIO object to store the Excel file
    output = BytesIO()
    
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(report.name[:31])  # Excel worksheet names limited to 31 chars
    
    # Add formats
    title_format = workbook.add_format({'bold': True, 'font_size': 16})
    header_format = workbook.add_format({'bold': True, 'bg_color': '#CCCCCC', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    
    # Add report title
    worksheet.write(0, 0, report.name, title_format)
    
    # Add report description if available
    if report.description:
        worksheet.write(1, 0, report.description)
    
    # Add metadata
    worksheet.write(3, 0, f"Created by: {report.created_by.username}")
    worksheet.write(4, 0, f"Created on: {report.created_at.strftime('%Y-%m-%d %H:%M')}")
    worksheet.write(5, 0, f"Last updated: {report.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Add chart data
    if hasattr(report, 'configuration'):
        config = report.configuration
        chart_data = generate_chart_data(config)
        
        # Write headers
        worksheet.write(7, 0, 'Label', header_format)
        worksheet.write(7, 1, 'Value', header_format)
        
        # Write data
        row = 8
        for i, label in enumerate(chart_data['labels']):
            if i < len(chart_data['datasets'][0]['data']):
                worksheet.write(row, 0, label, cell_format)
                worksheet.write(row, 1, chart_data['datasets'][0]['data'][i], cell_format)
                row += 1
        
        # Create a chart
        chart = workbook.add_chart({'type': config.chart_type.lower() if config.chart_type.lower() in ['bar', 'line', 'pie'] else 'column'})
        
        # Configure the chart
        chart.add_series({
            'name': chart_data['datasets'][0]['label'],
            'categories': [report.name[:31], 8, 0, row - 1, 0],
            'values': [report.name[:31], 8, 1, row - 1, 1],
        })
        
        # Add the chart to the worksheet
        worksheet.insert_chart('D7', chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
    # Close the workbook
    workbook.close()
    
    # Get the value of the BytesIO buffer
    excel_data = output.getvalue()
    output.close()
    
    # Create the HttpResponse object with Excel headers
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{report.name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    return response


def export_report_to_csv(report):
    """
    Export a report to a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow(['Label', 'Value'])
    
    # Write data
    if hasattr(report, 'configuration'):
        config = report.configuration
        chart_data = generate_chart_data(config)
        
        for i, label in enumerate(chart_data['labels']):
            if i < len(chart_data['datasets'][0]['data']):
                writer.writerow([label, chart_data['datasets'][0]['data'][i]])
    
    return response


def send_scheduled_report(schedule, is_resend=False):
    """
    Send a scheduled report via email.
    """
    from .models import ReportDelivery
    
    # Create a delivery record
    delivery = ReportDelivery.objects.create(
        schedule=schedule,
        status='PENDING',
        recipients=schedule.recipients,
        subject=schedule.subject,
        message=schedule.message,
        format=schedule.format
    )
    
    try:
        # Generate the report file
        report = schedule.report
        temp_file = None
        
        if schedule.format == 'PDF':
            response = export_report_to_pdf(report)
            content_type = 'application/pdf'
            file_ext = 'pdf'
        elif schedule.format == 'EXCEL':
            response = export_report_to_excel(report)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_ext = 'xlsx'
        else:  # CSV
            response = export_report_to_csv(report)
            content_type = 'text/csv'
            file_ext = 'csv'
        
        # Save the file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"{report.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")
        
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Send the email
        email = EmailMessage(
            subject=schedule.subject,
            body=schedule.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=schedule.recipients.split(','),
        )
        
        with open(temp_file, 'rb') as f:
            email.attach(os.path.basename(temp_file), f.read(), content_type)
        
        email.send()
        
        # Update delivery record
        delivery.status = 'SENT'
        delivery.sent_at = timezone.now()
        delivery.file_path = temp_file
        delivery.file_size = os.path.getsize(temp_file)
        delivery.save()
        
        # Update schedule last run time if not a resend
        if not is_resend:
            schedule.last_run = timezone.now()
            schedule.calculate_next_run()
            schedule.save()
        
        return True
    
    except Exception as e:
        # Update delivery status
        delivery.status = 'FAILED'
        delivery.error_message = str(e)
        delivery.save()
        
        return False
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
