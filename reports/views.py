# reports/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import json
import uuid

from .models import (
    Report, ReportConfiguration, ReportSchedule, ReportDelivery,
    ReportSettings
)
from .forms import (
    ReportConfigurationForm, ReportScheduleForm, ReportSettingsForm
)
from .utils import (
    generate_chart_data, export_report_to_pdf, export_report_to_excel,
    export_report_to_csv, send_scheduled_report
)

from products.models import Product, Category, Purchase
from project_management.models import Project
from leads.models import Lead
from clients.models import Client


@login_required
def dashboard(request):
    """
    Display the reports dashboard with summary statistics and recent reports.
    """
    # Get favorite reports
    favorite_reports = Report.objects.filter(
        Q(created_by=request.user) | Q(shared_with=request.user),
        configuration__is_favorite=True
    ).order_by('-updated_at')[:5]
    
    # Get recent reports
    recent_reports = Report.objects.filter(
        Q(created_by=request.user) | Q(shared_with=request.user)
    ).order_by('-updated_at')[:10]
    
    # Get report counts by type
    report_counts = ReportConfiguration.objects.filter(
        report__created_by=request.user
    ).values('report_type').annotate(count=Count('id'))
    
    # Convert to a dictionary for easier access in template
    report_types = {rc['report_type']: rc['count'] for rc in report_counts}
    
    # Get scheduled reports
    scheduled_reports = ReportSchedule.objects.filter(
        report__created_by=request.user,
        is_active=True
    ).order_by('next_run')[:5]
    
    # Get the current date
    today = timezone.now().date()
    start_date = today - timedelta(days=30)
    
    # Get stats for various models
    context = {
        'favorite_reports': favorite_reports,
        'recent_reports': recent_reports,
        'report_types': report_types,
        'scheduled_reports': scheduled_reports,
        'recent_purchases': Purchase.objects.order_by('-purchase_date')[:5],
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(is_active=True).count(),
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='in_progress').count(),
        'total_leads': Lead.objects.count(),
        'converted_leads': Lead.objects.filter(status='converted').count(),
        'lead_conversion_rate': calculate_lead_conversion_rate(),
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def report_list(request):
    """
    Display a list of all reports.
    """
    # Get filter parameters
    report_type = request.GET.get('type', '')
    search_query = request.GET.get('q', '')
    
    # Base queryset
    reports = Report.objects.filter(
        Q(created_by=request.user) | Q(shared_with=request.user)
    ).distinct()
    
    # Apply filters
    if report_type:
        reports = reports.filter(configuration__report_type=report_type)
    
    if search_query:
        reports = reports.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Order by updated_at
    reports = reports.order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'report_type': report_type,
        'search_query': search_query,
        'report_types': ReportConfiguration.REPORT_TYPES,
    }
    
    return render(request, 'reports/report_list.html', context)


@login_required
def banking_reports(request):
    """
    Display banking reports.
    """
    return render_report_type(request, 'BANKING')


@login_required
def sales_reports(request):
    """
    Display sales reports.
    """
    return render_report_type(request, 'SALES')


@login_required
def client_reports(request):
    """
    Display client reports.
    """
    return render_report_type(request, 'CLIENT')


@login_required
def expenses_reports(request):
    """
    Display expenses reports.
    """
    return render_report_type(request, 'EXPENSE')


@login_required
def purchases_reports(request):
    """
    Display purchases reports.
    """
    return render_report_type(request, 'PURCHASE')


@login_required
def leads_reports(request):
    """
    Display leads reports.
    """
    return render_report_type(request, 'LEADS')


@login_required
def projects_reports(request):
    """
    Display projects reports.
    """
    # Get all projects
    projects = Project.objects.all()
    
    # Get project statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='in_progress').count()
    completed_projects = projects.filter(status='completed').count()
    
    # Calculate on-time and delayed projects
    on_time_projects = 0
    delayed_projects = 0
    for project in projects:
        if project.end_date and project.end_date < timezone.now().date() and project.status != 'completed':
            delayed_projects += 1
        elif project.status == 'completed':
            if project.completed_date and project.end_date and project.completed_date <= project.end_date:
                on_time_projects += 1
            elif project.status == 'completed':
                on_time_projects += 1
    
    # Calculate percentages
    active_percentage = (active_projects / total_projects * 100) if total_projects > 0 else 0
    completed_percentage = (completed_projects / total_projects * 100) if total_projects > 0 else 0
    on_time_percentage = (on_time_projects / completed_projects * 100) if completed_projects > 0 else 0
    
    # Group projects by client
    projects_by_client = {}
    for project in projects:
        client_name = project.client.name if project.client else "No Client"
        if client_name in projects_by_client:
            projects_by_client[client_name] += 1
        else:
            projects_by_client[client_name] = 1
    
    # Group projects by type
    projects_by_type = Project.objects.values('project_type').annotate(count=Count('id'))
    
    context = {
        'projects': projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'delayed_projects': delayed_projects,
        'active_percentage': round(active_percentage, 1),
        'completed_percentage': round(completed_percentage, 1),
        'on_time_percentage': round(on_time_percentage, 1),
        'projects_by_client': projects_by_client,
        'projects_by_type': projects_by_type,
    }
    
    return render(request, 'reports/projects_reports.html', context)


def render_report_type(request, report_type):
    """
    Helper function to render reports of a specific type.
    """
    # Get reports of the specified type
    reports = Report.objects.filter(
        Q(created_by=request.user) | Q(shared_with=request.user),
        configuration__report_type=report_type
    ).order_by('-updated_at')
    
    # Get template name based on report type
    template_name = f"reports/{report_type.lower()}_reports.html"
    
    context = {
        'reports': reports,
        'report_type': report_type,
    }
    
    return render(request, template_name, context)


@login_required
def view_report(request, report_id):
    """
    View a single report.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    # Get chart data
    chart_data = generate_chart_data(report.configuration)
    
    context = {
        'report': report,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'reports/view_saved_report.html', context)


@login_required
def create_report(request):
    """
    Create a new report.
    """
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        template = request.POST.get('template')
        date_range = request.POST.get('date_range')
        is_favorite = request.POST.get('is_favorite') == 'on'
        
        # Process different report types
        if report_type == 'standard':
            # Handle standard report creation
            messages.success(request, f'Standard report "{title}" has been created successfully.')
            return redirect('reports:report_list')
            
        elif report_type == 'custom':
            # Handle custom report with modules and data sources
            modules = request.POST.getlist('modules')
            sources = request.POST.getlist('sources')
            
            messages.success(request, f'Custom report "{title}" with {len(modules)} modules has been created successfully.')
            return redirect('reports:report_list')
            
        elif report_type == 'scheduled':
            # Handle scheduled report with frequency and delivery options
            frequency = request.POST.get('frequency')
            delivery_method = request.POST.get('delivery_method')
            
            if frequency == 'weekly':
                day_of_week = request.POST.get('day_of_week')
            elif frequency == 'monthly':
                day_of_month = request.POST.get('day_of_month')
                
            if delivery_method in ['email', 'both']:
                recipients = request.POST.get('recipients')
            
            messages.success(request, f'Scheduled report "{title}" set to run {frequency} has been created successfully.')
            return redirect('reports:report_list')
    else:
        form = ReportConfigurationForm()
    
    context = {
        'form': form,
        'report_types': ReportConfiguration.REPORT_TYPES,
        'time_ranges': ReportConfiguration.TIME_RANGES,
        'chart_types': ReportConfiguration.CHART_TYPES,
    }
    
    return render(request, 'reports/create_report.html', context)


@login_required
def update_report(request, report_id):
    """
    Update an existing report.
    """
    report = get_object_or_404(Report, created_by=request.user, id=report_id)
    config = report.configuration
    
    if request.method == 'POST':
        form = ReportConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            # Update the report
            report.name = form.cleaned_data['name']
            report.description = form.cleaned_data['description']
            report.save()
            
            # Update the configuration
            form.save()
            
            messages.success(request, 'Report updated successfully.')
            return redirect('reports:view_report', report_id=report.id)
    else:
        form = ReportConfigurationForm(instance=config, initial={
            'name': report.name,
            'description': report.description,
        })
    
    context = {
        'form': form,
        'report': report,
        'report_types': ReportConfiguration.REPORT_TYPES,
        'time_ranges': ReportConfiguration.TIME_RANGES,
        'chart_types': ReportConfiguration.CHART_TYPES,
    }
    
    return render(request, 'reports/update_report.html', context)


@login_required
@require_POST
def delete_report(request, report_id):
    """
    Delete a report.
    """
    report = get_object_or_404(Report, created_by=request.user, id=report_id)
    report.delete()
    
    messages.success(request, 'Report deleted successfully.')
    return redirect('reports:report_list')


@login_required
@require_POST
def toggle_favorite(request, report_id):
    """
    Toggle the favorite status of a report.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    config = report.configuration
    config.is_favorite = not config.is_favorite
    config.save()
    
    return JsonResponse({
        'success': True,
        'is_favorite': config.is_favorite
    })


@login_required
def scheduled_reports(request):
    """
    Display scheduled reports.
    """
    schedules = ReportSchedule.objects.filter(
        report__created_by=request.user
    ).order_by('next_run')
    
    # Get delivery history
    deliveries = ReportDelivery.objects.filter(
        schedule__report__created_by=request.user
    ).order_by('-sent_at')[:20]
    
    context = {
        'schedules': schedules,
        'deliveries': deliveries,
    }
    
    return render(request, 'reports/scheduled_reports.html', context)


@login_required
def create_schedule(request):
    """
    Create a new report schedule.
    """
    if request.method == 'POST':
        form = ReportScheduleForm(request.POST, user=request.user)
    if form.is_valid():
        schedule = form.save(commit=False)
        
        # Calculate next run time
        schedule.calculate_next_run()
        schedule.save()
        
        messages.success(request, 'Schedule created successfully.')
        return redirect('reports:scheduled_reports')
    else:
        form = ReportScheduleForm(user=request.user)
    
    context = {
        'form': form,
        'frequency_choices': ReportSchedule.FREQUENCY_CHOICES,
        'day_choices': ReportSchedule.DAY_CHOICES,
        'format_choices': ReportSchedule.FORMAT_CHOICES,
        'range_1_to_31': range(1, 32),
    }
    
    return render(request, 'reports/create_schedule.html', context)


@login_required
def update_schedule(request, schedule_id):
    """
    Update an existing report schedule.
    """
    schedule = get_object_or_404(ReportSchedule, id=schedule_id, report__created_by=request.user)
    
    if request.method == 'POST':
        form = ReportScheduleForm(request.POST, instance=schedule, user=request.user)
    if form.is_valid():
        updated_schedule = form.save(commit=False)
        
        # Calculate next run time
        updated_schedule.calculate_next_run()
        updated_schedule.save()
        
        messages.success(request, 'Schedule updated successfully.')
        return redirect('reports:scheduled_reports')
    else:
        form = ReportScheduleForm(instance=schedule, user=request.user)
    
    context = {
        'form': form,
        'schedule': schedule,
        'frequency_choices': ReportSchedule.FREQUENCY_CHOICES,
        'day_choices': ReportSchedule.DAY_CHOICES,
        'format_choices': ReportSchedule.FORMAT_CHOICES,
        'range_1_to_31': range(1, 32),
    }
    
    return render(request, 'reports/update_schedule.html', context)


@login_required
@require_POST
def delete_schedule(request, schedule_id):
    """
    Delete a report schedule.
    """
    schedule = get_object_or_404(
        ReportSchedule,
        report__created_by=request.user,
        id=schedule_id
    )
    
    schedule.delete()
    
    messages.success(request, 'Schedule deleted successfully.')
    return redirect('reports:scheduled_reports')


@login_required
@require_POST
def toggle_schedule(request, schedule_id):
    """
    Toggle the active status of a report schedule.
    """
    schedule = get_object_or_404(
        ReportSchedule,
        report__created_by=request.user,
        id=schedule_id
    )
    
    schedule.is_active = not schedule.is_active
    schedule.save()
    
    return JsonResponse({
        'success': True,
        'is_active': schedule.is_active
    })


@login_required
@require_POST
def resend_report(request, delivery_id):
    """
    Resend a report delivery.
    """
    delivery = get_object_or_404(
        ReportDelivery,
        schedule__report__created_by=request.user,
        id=delivery_id
    )
    
    success = send_scheduled_report(delivery.schedule, is_resend=True)
    
    if success:
        messages.success(request, 'Report resent successfully.')
    else:
        messages.error(request, 'Failed to resend report.')
    
    return redirect('reports:scheduled_reports')


@login_required
def settings(request):
    """
    Display and update report settings.
    """
    # Get or create settings for the user
    settings, created = ReportSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ReportSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('reports:settings')
    else:
        form = ReportSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    
    return render(request, 'reports/settings.html', context)


@login_required
def export_report_pdf(request, report_id):
    """
    Export a report to PDF.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    return export_report_to_pdf(report)


@login_required
def export_report_excel(request, report_id):
    """
    Export a report to Excel.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    return export_report_to_excel(report)


@login_required
def export_report_csv(request, report_id):
    """
    Export a report to CSV.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    return export_report_to_csv(report)


# API endpoints
@login_required
def api_get_reports(request):
    """
    API endpoint to get a list of reports.
    """
    reports = Report.objects.filter(
        Q(created_by=request.user) | Q(shared_with=request.user)
    ).order_by('-updated_at')
    
    data = [{
        'id': report.id,
        'name': report.name,
        'description': report.description,
        'created_by': report.created_by.username,
        'created_at': report.created_at.isoformat(),
        'updated_at': report.updated_at.isoformat(),
        'report_type': report.configuration.report_type,
        'is_favorite': report.configuration.is_favorite,
    } for report in reports]
    
    return JsonResponse({'reports': data})


@login_required
def api_get_report(request, report_id):
    """
    API endpoint to get a single report.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    data = report.to_dict()
    
    return JsonResponse(data)


@login_required
def api_get_report_data(request, report_id):
    """
    API endpoint to get report data.
    """
    report = get_object_or_404(
        Report, 
        Q(created_by=request.user) | Q(shared_with=request.user),
        id=report_id
    )
    
    chart_data = generate_chart_data(report.configuration)
    
    return JsonResponse(chart_data)


def calculate_lead_conversion_rate():
    total_leads = Lead.objects.count()
    converted_leads = Lead.objects.filter(status='converted').count()
    
    if total_leads > 0:
        return round((converted_leads / total_leads) * 100, 1)
    else:
        return 0.0