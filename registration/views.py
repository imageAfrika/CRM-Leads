from django.shortcuts import render
from .models import SubscriptionPlan

# Create your views here.

def registration_home(request):
    """Registration app home page"""
    return render(request, 'registration/registration_home.html')

def register_company(request):
    """Company registration form"""
    return render(request, 'registration/register_company.html')

def register_user(request):
    """User registration form"""
    return render(request, 'registration/register_user.html')

def subscription_plans(request):
    """Subscription plans page"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    context = {
        'basic_plan': plans.filter(name='Basic Plan').first(),
        'professional_plan': plans.filter(name='Professional Plan').first(),
        'enterprise_plan': plans.filter(name='Enterprise Plan').first(),
    }
    return render(request, 'registration/subscription_plans.html', context)

def app_selection(request):
    """App selection page"""
    return render(request, 'registration/app_selection.html')
