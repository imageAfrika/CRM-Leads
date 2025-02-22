from django.views.generic import TemplateView
from clients.models import Client
from sales.models import Sale
from documents.models import Document, Quote, Expenditure
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from decimal import Decimal
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authentication.models import Profile

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
        
        # Get date ranges
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Get quotes statistics
        total_quotes = Quote.objects.count()
        quotes_this_month = Quote.objects.filter(created_at__gte=this_month_start).count()
        quotes_last_month = Quote.objects.filter(
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).count()
        
        # Get invoices statistics
        total_invoices = Document.objects.filter(document_type='INVOICE').count()
        invoices_this_month = Document.objects.filter(
            document_type='INVOICE',
            created_at__gte=this_month_start
        ).count()
        invoices_last_month = Document.objects.filter(
            document_type='INVOICE',
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).count()
        
        # Calculate revenue
        total_revenue = Document.objects.filter(
            document_type='INVOICE'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate previous month's revenue
        last_month_revenue = Document.objects.filter(
            document_type='INVOICE',
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate revenue trend
        if last_month_revenue > 0:
            revenue_trend = ((total_revenue - last_month_revenue) / last_month_revenue) * 100
        else:
            revenue_trend = 0
        
        # Calculate conversion rate
        conversion_rate = round((total_invoices / total_quotes * 100) if total_quotes > 0 else 0, 1)
        conversion_this_month = (invoices_this_month / quotes_this_month * 100) if quotes_this_month > 0 else 0
        conversion_last_month = (invoices_last_month / quotes_last_month * 100) if quotes_last_month > 0 else 0
        conversion_trend = self.calculate_trend(conversion_this_month, conversion_last_month)
        
        # Calculate expenditure
        total_expenditure = Expenditure.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calculate previous month's expenditure
        last_month_expenditure = Expenditure.objects.filter(
            date__gte=last_month_start,
            date__lt=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expenditure trend
        if last_month_expenditure > 0:
            expenditure_trend = ((total_expenditure - last_month_expenditure) / last_month_expenditure) * 100
        else:
            expenditure_trend = 0

        # Get current month's expenses
        today = timezone.now()
        current_month_expenses = Expenditure.objects.filter(
            date__year=today.year,
            date__month=today.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context['stats'] = {
            'total_quotes': total_quotes,
            'total_invoices': total_invoices,
            'total_revenue': total_revenue,
            'revenue_trend': revenue_trend,
            'total_expenditure': total_expenditure,
            'expenditure_trend': expenditure_trend,
            'total_expenses': current_month_expenses,
        }
        
        return context
    
    def calculate_trend(self, current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

class CalendarView(TemplateView):
    template_name = 'dashboard/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents_url'] = reverse('documents:document_list')
        return context 

class ScheduleView(TemplateView):
    template_name = 'dashboard/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your events data here
        context['events'] = []
        return context 

class StatisticsView(TemplateView):
    template_name = 'dashboard/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get project statistics
        context['stats'] = {
            'quotes_data': self.get_quotes_stats(),
            'revenue_data': self.get_revenue_stats()
        }
        return context

    def get_quotes_stats(self):
        total_quotes = Quote.objects.count()
        total_invoices = Document.objects.filter(document_type='INVOICE').count()
        
        return {
            'total_quotes': total_quotes,
            'total_invoices': total_invoices
        }

    def get_revenue_stats(self):
        total_revenue = Document.objects.filter(
            document_type='INVOICE'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_expenditure = Document.objects.filter(
            document_type='EXPENSE'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        return {
            'total_revenue': float(total_revenue),
            'total_expenditure': float(total_expenditure)
        }

def get_chart_data(request):
    period = request.GET.get('period', 'month')
    
    # Calculate date range
    end_date = datetime.now()
    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:  # year
        start_date = end_date - timedelta(days=365)

    # Get quotes data
    quotes_data = Quote.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Get invoices data
    invoices_data = Document.objects.filter(
        document_type='INVOICE',
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Get revenue data
    revenue_data = Document.objects.filter(
        document_type='INVOICE',
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    # Get expenditure data
    expenditure_data = Document.objects.filter(
        document_type='EXPENSE',
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    # Prepare data for charts
    dates = sorted(set(
        [item['date'] for item in quotes_data] +
        [item['date'] for item in invoices_data] +
        [item['date'] for item in revenue_data] +
        [item['date'] for item in expenditure_data]
    ))

    return JsonResponse({
        'labels': [date.strftime('%Y-%m-%d') for date in dates],
        'quotes_data': [next((item['count'] for item in quotes_data if item['date'] == date), 0) for date in dates],
        'invoices_data': [next((item['count'] for item in invoices_data if item['date'] == date), 0) for date in dates],
        'revenue_data': [float(next((item['total'] for item in revenue_data if item['date'] == date), 0)) for date in dates],
        'expenditure_data': [float(next((item['total'] for item in expenditure_data if item['date'] == date), 0)) for date in dates],
    }) 

@login_required
def dashboard(request):
    profile_id = request.session.get('profile_id')
    profile = Profile.objects.get(id=profile_id) if profile_id else None
    
    context = {
        'profile': profile,
    }
    return render(request, 'dashboard/dashboard.html', context) 