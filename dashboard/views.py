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
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authentication.models import Profile
import json
from calendar import month_name
from expenses.models import Expense
from purchases.models import Purchase

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get profile if available
        if hasattr(self.request.user, 'profile'):
            context['profile'] = self.request.user.profile
        
        # Recent items for quick access
        context['recent_clients'] = Client.objects.order_by('-created_at')[:5]
        context['recent_documents'] = Document.objects.order_by('-created_at')[:5]
        context['recent_quotes'] = Quote.objects.filter(status='DRAFT').order_by('-created_at')[:5]
        context['recent_sales'] = Document.objects.filter(document_type='INVOICE').order_by('-created_at')[:5]

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
        
        # Get quotes total amount
        quotes_amount = Quote.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
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
        
        # Get invoices total amount
        invoices_amount = Document.objects.filter(document_type='INVOICE').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate trends (percentage change)
        quote_trend = self._calculate_trend(quotes_this_month, quotes_last_month)
        invoice_trend = self._calculate_trend(invoices_this_month, invoices_last_month)
        
        # Get revenue and expenditure
        total_revenue = Document.objects.filter(document_type='INVOICE').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        total_expenditure = Expense.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calculate revenue and expenditure for this month and last month
        revenue_this_month = Document.objects.filter(
            document_type='INVOICE',
            created_at__gte=this_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        revenue_last_month = Document.objects.filter(
            document_type='INVOICE',
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        expenditure_this_month = Expense.objects.filter(
            date__gte=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenditure_last_month = Expense.objects.filter(
            date__gte=last_month_start,
            date__lt=this_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate trends
        revenue_trend = self._calculate_trend(revenue_this_month, revenue_last_month)
        expenditure_trend = self._calculate_trend(expenditure_this_month, expenditure_last_month)
        
        # Calculate conversion rate (quotes to invoices)
        conversion_rate = 0
        if total_quotes > 0:
            conversion_rate = round((total_invoices / total_quotes) * 100)
        
        # Calculate conversion trend
        conversion_this_month = 0
        if quotes_this_month > 0:
            conversion_this_month = (invoices_this_month / quotes_this_month) * 100
            
        conversion_last_month = 0
        if quotes_last_month > 0:
            conversion_last_month = (invoices_last_month / quotes_last_month) * 100
            
        conversion_trend = self._calculate_trend(conversion_this_month, conversion_last_month)
        
        # Prepare stats dictionary
        context['stats'] = {
            'total_quotes': total_quotes,
            'total_invoices': total_invoices,
            'quotes_amount': quotes_amount,
            'invoices_amount': invoices_amount,
            'quote_trend': quote_trend,
            'invoice_trend': invoice_trend,
            'total_revenue': total_revenue,
            'total_expenditure': total_expenditure,
            'revenue_trend': revenue_trend,
            'expenditure_trend': expenditure_trend,
            'conversion_rate': conversion_rate,
            'conversion_trend': conversion_trend,
        }
        
        # Get monthly data for charts (last 6 months)
        six_months_ago = now - timedelta(days=180)
        
        # Get monthly expenses
        monthly_expenses = self._get_monthly_data(
            Expense.objects.filter(date__gte=six_months_ago),
            'date', 'amount'
        )
        
        # Get monthly purchases
        monthly_purchases = self._get_monthly_data(
            Purchase.objects.filter(date__gte=six_months_ago),
            'date', 'amount'
        )
        
        # Get monthly revenue
        monthly_revenue = self._get_monthly_data(
            Document.objects.filter(
                document_type='INVOICE',
                created_at__gte=six_months_ago
            ),
            'created_at', 'total_amount'
        )
        
        # Prepare months labels
        months = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            months.append(month_name[month_date.month][:3])
        
        # Add monthly data to context
        context['months'] = json.dumps(months)
        context['monthly_expenses'] = json.dumps(list(monthly_expenses.values()))
        context['monthly_purchases'] = json.dumps(list(monthly_purchases.values()))
        context['monthly_revenue'] = json.dumps(list(monthly_revenue.values()))
        
        return context
    
    def _calculate_trend(self, current, previous):
        """Calculate percentage change between current and previous values"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)
    
    def _get_monthly_data(self, queryset, date_field, amount_field):
        """Get monthly aggregated data for the last 6 months"""
        now = timezone.now()
        result = {}
        
        # Initialize with zeros for the last 6 months
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_key = month_date.month
            result[month_key] = 0
        
        # Get data from database
        monthly_data = queryset.annotate(
            month=TruncMonth(date_field)
        ).values('month').annotate(
            total=Sum(amount_field)
        ).order_by('month')
        
        # Fill in the data
        for item in monthly_data:
            month_key = item['month'].month
            if month_key in result:
                result[month_key] = float(item['total'])
        
        return result

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
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('date')

    # Get invoices data
    invoices_data = Document.objects.filter(
        document_type='INVOICE',
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        total=Sum('total_amount')
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
        'quotes_amount': [float(next((item['total'] for item in quotes_data if item['date'] == date), 0)) for date in dates],
        'invoices_amount': [float(next((item['total'] for item in invoices_data if item['date'] == date), 0)) for date in dates],
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