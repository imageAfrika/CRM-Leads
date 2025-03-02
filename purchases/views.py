from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Purchase, PurchaseCategory
from .forms import PurchaseForm, PurchaseCategoryForm
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

@login_required
def purchase_list(request):
    if request.user.is_superuser:
        purchases = Purchase.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        purchases = Purchase.objects.filter(profile=request.profile)
    else:
        purchases = Purchase.objects.filter(created_by=request.user)
    
    total_amount = purchases.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Filter categories by profile if not superuser
    if request.user.is_superuser:
        categories = PurchaseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = PurchaseCategory.objects.filter(profile=request.profile)
    else:
        categories = PurchaseCategory.objects.filter(created_by=request.user)
    
    context = {
        'purchases': purchases,
        'total_amount': total_amount,
        'categories': categories,
    }
    return render(request, 'purchases/purchase_list.html', context)

@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to view this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to view this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to view this purchase.")
            return redirect('purchases:purchase_list')
    
    return render(request, 'purchases/purchase_detail.html', {'purchase': purchase})

@login_required
def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                purchase.profile = request.profile
            purchase.save()
            messages.success(request, 'Purchase created successfully!')
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseForm()
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(profile=request.profile)
            else:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(created_by=request.user)
    
    return render(request, 'purchases/purchase_form.html', {
        'form': form,
        'title': 'Create Purchase'
    })

@login_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to update this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to update this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to update this purchase.")
            return redirect('purchases:purchase_list')
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES, instance=purchase)
        if form.is_valid():
            purchase = form.save(commit=False)
            # Don't change the created_by field, but update profile if needed
            if hasattr(request, 'profile') and request.profile:
                purchase.profile = request.profile
            purchase.save()
            messages.success(request, 'Purchase updated successfully!')
            return redirect('purchases:purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseForm(instance=purchase)
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(profile=request.profile)
            else:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(created_by=request.user)
    
    return render(request, 'purchases/purchase_form.html', {
        'form': form,
        'purchase': purchase,
        'title': 'Update Purchase'
    })

@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to delete this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to delete this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to delete this purchase.")
            return redirect('purchases:purchase_list')
    
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, 'Purchase deleted successfully!')
        return redirect('purchases:purchase_list')
    return render(request, 'purchases/purchase_confirm_delete.html', {'purchase': purchase})

@login_required
def category_list(request):
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                category.profile = request.profile
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm()
    
    # Get categories
    if request.user.is_superuser:
        categories = PurchaseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = PurchaseCategory.objects.filter(profile=request.profile)
    else:
        categories = PurchaseCategory.objects.filter(created_by=request.user)
    
    return render(request, 'purchases/category_list.html', {
        'categories': categories,
        'form': form
    })

@login_required
def category_create(request):
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                category.profile = request.profile
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm()
    
    return render(request, 'purchases/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })

@login_required
def category_update(request, pk):
    category = get_object_or_404(PurchaseCategory, pk=pk)
    
    # Check if user has permission to update this category
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if category.profile != request.profile:
                messages.error(request, "You don't have permission to update this category.")
                return redirect('purchases:category_list')
        elif category.created_by != request.user:
            messages.error(request, "You don't have permission to update this category.")
            return redirect('purchases:category_list')
    
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm(instance=category)
    
    return render(request, 'purchases/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Update Category'
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(PurchaseCategory, pk=pk)
    
    # Check if user has permission to delete this category
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if category.profile != request.profile:
                messages.error(request, "You don't have permission to delete this category.")
                return redirect('purchases:category_list')
        elif category.created_by != request.user:
            messages.error(request, "You don't have permission to delete this category.")
            return redirect('purchases:category_list')
    
    # Check if there are any purchases associated with this category
    if Purchase.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete this category because it has associated purchases.")
        return redirect('purchases:category_list')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('purchases:category_list')
    
    return render(request, 'purchases/category_confirm_delete.html', {'category': category})

@login_required
def purchase_reports(request):
    # Get the date range from request or default to last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    date_range = request.GET.get('date_range', '6months')
    
    if date_range == '30days':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90days':
        start_date = end_date - timedelta(days=90)
    elif date_range == '1year':
        start_date = end_date - timedelta(days=365)
    
    # Filter purchases by user/profile and date range
    if request.user.is_superuser:
        purchases = Purchase.objects.filter(date__range=[start_date, end_date])
    elif hasattr(request, 'profile') and request.profile:
        purchases = Purchase.objects.filter(
            profile=request.profile,
            date__range=[start_date, end_date]
        )
    else:
        purchases = Purchase.objects.filter(
            created_by=request.user,
            date__range=[start_date, end_date]
        )
    
    # Monthly purchases
    monthly_purchases = purchases.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Category wise purchases
    category_purchases = purchases.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Status wise purchases
    status_purchases = purchases.values('status').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Vendor wise purchases
    vendor_purchases = purchases.values('vendor').annotate(
        total=Sum('amount'),
        count=Sum('quantity')
    ).order_by('-total')[:10]  # Top 10 vendors
    
    return render(request, 'purchases/purchase_reports.html', {
        'monthly_purchases': monthly_purchases,
        'category_purchases': category_purchases,
        'status_purchases': status_purchases,
        'vendor_purchases': vendor_purchases,
        'total_amount': purchases.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_count': purchases.count(),
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range,
    })
