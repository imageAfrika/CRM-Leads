from django.views.generic import TemplateView
from clients.models import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from django.http import JsonResponse
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, TruncQuarter, TruncYear
from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from authentication.models import Profile
import json
from calendar import month_name
from humanize import intcomma   

# Import models from other apps
from documents.models import Quote, Document
from sales.models import Sale
from expenses.models import Expense
from purchases.models import Purchase

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = 'authentication:login'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        # Check user role and redirect if necessary
        if request.user.is_authenticated:
            role = request.session.get('user_role')
            print(f"DashboardView: User role is {role}")
            
            # If staff role, redirect to profile 
            if role == 'staff':
                print(f"Redirecting staff user to profile")
                return redirect('authentication:profile')
        
        # Continue with normal processing for administrators
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get profile if available
        if hasattr(self.request.user, 'profile'):
            context['profile'] = self.request.user.profile
        
        # Recent items for quick access
        context['recent_clients'] = Client.objects.order_by('-created_at')[:5]
        
        # Get date ranges
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Get clients statistics
        total_clients = Client.objects.count()
        clients_this_month = Client.objects.filter(created_at__gte=this_month_start).count()
        clients_last_month = Client.objects.filter(
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).count()
        
        # Calculate client trend (percentage change)
        client_trend = self._calculate_trend(clients_this_month, clients_last_month)
        
        # Quotes vs Invoices data
        quotes_count = Quote.objects.filter(status='INVOICED').count()
        invoices_count = Document.objects.filter(document_type='INVOICE').count()
        quotes_amount = Quote.objects.filter(status='INVOICED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        invoices_amount = Document.objects.filter(document_type='INVOICE').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Revenue vs Expenditure data
        # Revenue = Paid invoices + Sales
        invoice_revenue = Document.objects.filter(document_type='INVOICE', status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        sales_revenue = Sale.objects.filter(payment_status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_revenue = invoice_revenue + sales_revenue
        
        # Expenditure = Expenses + Purchases
        total_expenses = Expense.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
        total_purchases = Purchase.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenditure = total_expenses + total_purchases
        
        # Purchases vs Sales data
        # Sales = Invoices (paid) + Sales
        total_sales = invoice_revenue + sales_revenue

        # Calculate profit and margin
        total_profit = total_revenue - total_expenditure
        total_margin = self._calculate_percentage(total_profit, total_revenue)
        total_margin_percentage = self._calculate_percentage(total_profit, total_revenue)
        total_margin_percentage_trend = self._calculate_trend(total_margin_percentage, total_margin_percentage)
        total_margin_percentage_trend_percentage = self._calculate_percentage(total_margin_percentage_trend, total_margin_percentage)
        
        # Get monthly data for charts
        monthly_data = self._get_monthly_data()
        
        # Debug logging
        print("Monthly Data Debug:")
        print("Months:", monthly_data['months'])
        print("Income:", monthly_data['income'])
        print("Expenses:", monthly_data['expenses'])
        print("Purchases:", monthly_data['purchases'])
        print("Sales:", monthly_data['sales'])
        print("Quotes:", monthly_data['quotes'])
        print("Invoices:", monthly_data['invoices'])
        
        # Prepare stats dictionary
        context['stats'] = {
            'total_clients': total_clients,
            'client_trend': client_trend,
            'quotes_count': quotes_count,
            'invoices_count': invoices_count,
            'quotes_amount': quotes_amount,
            'invoices_amount': invoices_amount,
            'total_revenue': total_revenue,
            'total_expenditure': total_expenditure,
            'total_purchases': total_purchases,
            'total_sales': total_sales,
            'total_profit': total_profit,
            'total_margin': total_margin,
            'total_margin_percentage': total_margin_percentage,
            'total_margin_percentage_trend': total_margin_percentage_trend,
            'total_margin_percentage_trend_percentage': total_margin_percentage_trend_percentage,
            # Add monthly data for charts
            'months': json.dumps(monthly_data['months']),
            'monthly_revenue': json.dumps(monthly_data['income']),
            'monthly_expenditure': json.dumps(monthly_data['expenses']),
            'monthly_purchases': json.dumps(monthly_data['purchases']),
            'monthly_sales': json.dumps(monthly_data['sales']),
            'monthly_profit': json.dumps([sales - purchases for sales, purchases in zip(monthly_data['income'], monthly_data['expenses'])]),
            'monthly_quotes': json.dumps(monthly_data['quotes']),
            'monthly_invoices': json.dumps(monthly_data['invoices'])
        }
        
        return context
    
    def _calculate_trend(self, current, previous):
        if previous == 0:
            return current
        return round(((current - previous) / previous) * 100, 2)
    
    def _calculate_percentage(self, part, whole):
        if whole == 0:
            return 0
        return round((part / whole) * 100, 2)
    
    def _get_monthly_data(self):
        """Get real-time monthly data for multiple financial metrics"""
        # Get current time and date ranges
        now = timezone.now()
        current_year = now.year
        
        # Prepare months list and data
        months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'
        ]
        
        # Debug print
        print(f"Current Year: {current_year}")
        
        # Retrieve data for each month
        purchases_data = []
        sales_data = []
        invoices_data = []
        quotes_data = []
        expenses_data = []
        income_data = []
        
        for month in range(1, 7):
            # Retrieve data for the specific month
            purchases = Purchase.objects.filter(
                date__year=current_year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            sales = Sale.objects.filter(
                sale_date__year=current_year,
                sale_date__month=month,
                payment_status='PAID'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            invoices = Document.objects.filter(
                document_type='INVOICE',
                status='PAID',
                created_at__year=current_year,
                created_at__month=month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            quotes = Quote.objects.filter(
                status='INVOICED',
                created_at__year=current_year,
                created_at__month=month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            expenses = Expense.objects.filter(
                date__year=current_year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Debug print for each month
            print(f"Month {month} Debug:")
            print(f"Purchases: {purchases}")
            print(f"Sales: {sales}")
            print(f"Invoices: {invoices}")
            print(f"Quotes: {quotes}")
            print(f"Expenses: {expenses}")
            
            # Append data
            purchases_data.append(float(purchases))
            sales_data.append(float(sales))
            invoices_data.append(float(invoices))
            quotes_data.append(float(quotes))
            expenses_data.append(float(expenses))
            income_data.append(float(sales + invoices))
        
        # Final debug print
        print("Final Monthly Data:")
        print("Months:", months)
        print("Purchases:", purchases_data)
        print("Sales:", sales_data)
        print("Invoices:", invoices_data)
        print("Quotes:", quotes_data)
        print("Expenses:", expenses_data)
        print("Income:", income_data)
        
        return {
            'months': months,
            'purchases': purchases_data,
            'sales': sales_data,
            'invoices': invoices_data,
            'quotes': quotes_data,
            'expenses': expenses_data,
            'income': income_data
        }

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile.html'
    login_url = 'authentication:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['profile'] = profile
        context['active_tab'] = 'profile'
        return context

    def post(self, request):
        profile = request.user.profile
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            bio = request.POST.get('bio')
            
            # Update profile
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.user.email = email
            profile.phone = phone
            profile.bio = bio
            
            # Handle avatar upload
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            try:
                profile.user.save()
                profile.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully.',
                    'avatar_url': profile.avatar.url if profile.avatar else None,
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e),
                }, status=400)
        
        # Traditional form submission
        return redirect('dashboard:profile')

class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/calendar.html'
    login_url = 'authentication:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/schedule.html'
    login_url = 'authentication:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/statistics.html'
    login_url = 'authentication:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def get_chart_data(request):
    """Get data for dashboard charts"""
    chart_type = request.GET.get('type', 'monthly')
    timeline = request.GET.get('timeline', 'month')  # Options: week, month, quarter, year
    
    # Get date range based on timeline
    now = timezone.now()
    if timeline == 'week':
        start_date = now - timedelta(days=7)
        truncate_func = TruncDate
        date_format = '%d %b'  # e.g., "01 Jan"
    elif timeline == 'month':
        start_date = now - timedelta(days=30)
        truncate_func = TruncDate
        date_format = '%d %b'  # e.g., "01 Jan"
    elif timeline == 'quarter':
        start_date = now - timedelta(days=90)
        truncate_func = TruncWeek
        date_format = 'Week %W'  # e.g., "Week 01"
    elif timeline == 'year':
        start_date = now - timedelta(days=365)
        truncate_func = TruncMonth
        date_format = '%b %Y'  # e.g., "Jan 2023"
    else:
        # Default to month
        start_date = now - timedelta(days=30)
        truncate_func = TruncDate
        date_format = '%d %b'
    
    # Quotes vs Invoices data
    if chart_type == 'quotes_invoices':
        if request.GET.get('view_type') == 'amount':
            # Get quotes and invoices amounts over time
            quotes = Quote.objects.filter(
                created_at__gte=start_date, 
                status='INVOICED'
            ).annotate(
                date=truncate_func('created_at')
            ).values('date').annotate(
                total=Sum('total_amount')
            ).order_by('date')
            
            invoices = Document.objects.filter(
                document_date__gte=start_date,
                document_date__lt=now,
                document_type='INVOICE'
            ).annotate(
                date=truncate_func('document_date')
            ).values('date').annotate(
                total=Sum('total_amount')
            ).order_by('date')
        else:
            # Get quotes and invoices count over time
            quotes = Quote.objects.filter(
                created_at__gte=start_date,
                status='INVOICED'
            ).annotate(
                date=truncate_func('created_at')
            ).values('date').annotate(
                total=Count('id')
            ).order_by('date')
            
            invoices = Document.objects.filter(
                document_date__gte=start_date,
                document_date__lt=now,
                document_type='INVOICE'
            ).annotate(
                date=truncate_func('document_date')
            ).values('date').annotate(
                total=Count('id')
            ).order_by('date')
        
        # Create a dict of date mapped to data
        quote_dict = {item['date'].strftime('%Y-%m-%d'): item['total'] for item in quotes}
        invoice_dict = {item['date'].strftime('%Y-%m-%d'): item['total'] for item in invoices}
        
        # Generate list of dates
        current_date = start_date
        labels = []
        quote_data = []
        invoice_data = []
        
        while current_date <= now:
            date_key = current_date.strftime('%Y-%m-%d')
            labels.append(current_date.strftime(date_format))
            quote_data.append(float(quote_dict.get(date_key, 0)))
            invoice_data.append(float(invoice_dict.get(date_key, 0)))
            current_date += timedelta(days=1)
        
        data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Quotes',
                    'data': quote_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Invoices',
                    'data': invoice_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }
    
    # Purchases vs Sales data
    elif chart_type == 'purchases_sales':
        # Get purchases data
        purchases = Purchase.objects.filter(
            date__gte=start_date
        ).annotate(
            date=truncate_func('date')
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        # Get sales data (Invoices + Sales)
        invoice_sales = Document.objects.filter(
            document_date__gte=start_date,
            document_date__lt=now,
            document_type='INVOICE',
            status='PAID'
        ).annotate(
            date=truncate_func('document_date')
        ).values('date').annotate(
            total=Sum('total_amount')
        ).order_by('date')
        
        sales_sales = Sale.objects.filter(
            sale_date__gte=start_date,
            sale_date__lt=now,
            payment_status='PAID'
        ).annotate(
            date=truncate_func('sale_date')
        ).values('date').annotate(
            total=Sum('total_amount')
        ).order_by('date')
        
        # Create a dict of date mapped to data
        purchase_dict = {item['date'].strftime('%Y-%m-%d'): item['total'] for item in purchases}
        invoice_dict = {item['date'].strftime('%Y-%m-%d'): item['total'] for item in invoice_sales}
        sales_dict = {item['date'].strftime('%Y-%m-%d'): item['total'] for item in sales_sales}
        
        # Generate list of dates
        current_date = start_date
        labels = []
        purchase_data = []
        sales_data = []
        
        while current_date <= now:
            date_key = current_date.strftime('%Y-%m-%d')
            labels.append(current_date.strftime(date_format))
            
            # Purchases
            purchase_data.append(float(purchase_dict.get(date_key, 0)))
            
            # Sales = Invoices + Sales
            date_invoice = invoice_dict.get(date_key, 0)
            date_sales = sales_dict.get(date_key, 0)
            sales_data.append(float(date_invoice + date_sales))
            
            current_date += timedelta(days=1)

        
        data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Purchases',
                    'data': purchase_data,
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Sales',
                    'data': sales_data,
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 1
                }
            ]
        }
    
    # Revenue Expenditure data
    elif chart_type == 'revenue_expenditure':
        return JsonResponse({
            'labels': [],
            'datasets': []
        })
    
    # Monthly trends
    else:
        # Default to monthly trends
        # Use _get_monthly_data from DashboardView
        monthly_data = DashboardView()._get_monthly_data()
        
        data = {
            'labels': monthly_data['months'],
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': monthly_data['income'],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Expenditure',
                    'data': monthly_data['expenses'],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Profit/Loss',
                    'data': [sales - purchases for sales, purchases in zip(monthly_data['income'], monthly_data['expenses'])],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }
            ]
        }
    
    return JsonResponse(data) 