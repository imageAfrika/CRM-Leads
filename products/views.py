from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.db import transaction
import json

from .models import (
    Category, 
    Product, 
    InventoryTransaction, 
    Supplier, 
    Purchase, 
    PurchaseItem
)
from .forms import (
    CategoryForm, 
    ProductForm, 
    InventoryTransactionForm, 
    SupplierForm, 
    PurchaseForm, 
    PurchaseItemFormSet
)

# Product Views
@login_required
def product_list(request):
    products = Product.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)
    
    # Filter by stock level
    stock_level = request.GET.get('stock_level')
    if stock_level:
        if stock_level == 'low':
            products = products.filter(current_stock__lte=F('reorder_level'), current_stock__gt=0)
        elif stock_level == 'out':
            products = products.filter(current_stock__lte=0)
        elif stock_level == 'in':
            products = products.filter(current_stock__gt=F('reorder_level'))
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(item_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'page_obj': page_obj,
        'categories': categories,
        'status_choices': Product.STATUS_CHOICES,
        'selected_category': category_id,
        'selected_status': status,
        'selected_stock_level': stock_level,
        'search_query': search_query,
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Get recent transactions
    transactions = InventoryTransaction.objects.filter(product=product).order_by('-created_at')[:10]
    
    context = {
        'product': product,
        'transactions': transactions,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.created_by = request.user
                    product.updated_by = request.user
                    product.save()
                    messages.success(request, 'Product created successfully!')
                    return redirect('products:product_list')
            except Exception as e:
                messages.error(request, f'Error saving product: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Create Product',
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.updated_by = request.user
                product.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('products:product_list')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Update Product',
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:product_list')
    
    context = {
        'product': product,
    }
    return render(request, 'products/product_confirm_delete.html', context)

# Category Views
@login_required
def category_list(request):
    categories = Category.objects.all()
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    # Add product count to each category
    categories = categories.annotate(product_count=Count('products'))
    
    context = {
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'products/category_list.html', context)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    category = form.save(commit=False)
                    category.created_by = request.user
                    category.save()
                    messages.success(request, 'Category created successfully!')
                    return redirect('products:category_list')
            except Exception as e:
                messages.error(request, f'Error saving category: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Create Category',
    }
    return render(request, 'products/category_form.html', context)

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Category updated successfully!')
                return redirect('products:category_list')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Update Category',
    }
    return render(request, 'products/category_form.html', context)

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    # Check if there are products in this category
    if Product.objects.filter(category=category).exists():
        messages.error(request, 'Cannot delete category with associated products.')
        return redirect('products:category_list')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('products:category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'products/category_confirm_delete.html', context)

# Inventory Transaction Views
@login_required
def transaction_list(request):
    transactions = InventoryTransaction.objects.all()
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by product
    product_id = request.GET.get('product')
    if product_id:
        transactions = transactions.filter(product_id=product_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)  # Include the end date
            transactions = transactions.filter(created_at__range=[start_date, end_date])
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get products for filter
    products = Product.objects.all()
    
    context = {
        'page_obj': page_obj,
        'products': products,
        'transaction_types': InventoryTransaction.TRANSACTION_TYPES,
        'selected_type': transaction_type,
        'selected_product': product_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'products/transaction_list.html', context)

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Transaction recorded successfully!')
            return redirect('products:transaction_list')
    else:
        form = InventoryTransactionForm()
    
    context = {
        'form': form,
        'title': 'Record Transaction',
    }
    return render(request, 'products/transaction_form.html', context)

# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) | 
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
    }
    return render(request, 'products/supplier_list.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    # Get recent purchases
    purchases = Purchase.objects.filter(supplier=supplier).order_by('-purchase_date')[:10]
    
    context = {
        'supplier': supplier,
        'purchases': purchases,
    }
    return render(request, 'products/supplier_detail.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            try:
                supplier = form.save(commit=False)
                supplier.created_by = request.user
                supplier.save()
                messages.success(request, 'Supplier created successfully!')
                return redirect('products:supplier_list')
            except Exception as e:
                messages.error(request, f'Error saving supplier: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': 'Create Supplier',
    }
    return render(request, 'products/supplier_form.html', context)

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            try:
                supplier = form.save()
                messages.success(request, 'Supplier updated successfully!')
                return redirect('products:supplier_list')
            except Exception as e:
                messages.error(request, f'Error updating supplier: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'supplier': supplier,
        'title': 'Update Supplier',
    }
    return render(request, 'products/supplier_form.html', context)

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    # Check if there are purchases from this supplier
    if Purchase.objects.filter(supplier=supplier).exists():
        messages.error(request, 'Cannot delete supplier with associated purchases.')
        return redirect('products:supplier_detail', pk=supplier.pk)
    
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('products:supplier_list')
    
    context = {
        'supplier': supplier,
    }
    return render(request, 'products/supplier_confirm_delete.html', context)

# Purchase Views
@login_required
def purchase_list(request):
    purchases = Purchase.objects.all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        purchases = purchases.filter(status=status)
    
    # Filter by supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            purchases = purchases.filter(purchase_date__range=[start_date, end_date])
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(purchases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get suppliers for filter
    suppliers = Supplier.objects.all()
    
    context = {
        'page_obj': page_obj,
        'suppliers': suppliers,
        'status_choices': Purchase.STATUS_CHOICES,
        'selected_status': status,
        'selected_supplier': supplier_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'products/purchase_list.html', context)

@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    context = {
        'purchase': purchase,
    }
    return render(request, 'products/purchase_detail.html', context)

@login_required
def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                purchase = form.save(commit=False)
                purchase.created_by = request.user
                purchase.updated_by = request.user
                purchase.save()
                
                formset.instance = purchase
                formset.save()
                
                # Calculate total amount
                total = sum(item.total_price for item in purchase.items.all())
                purchase.total_amount = total
                purchase.save()
                
                # Create inventory transactions for each item if status is 'received'
                if purchase.status == 'received':
                    for item in purchase.items.all():
                        InventoryTransaction.objects.create(
                            product=item.product,
                            transaction_type='purchase',
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            total_amount=item.total_price,
                            reference_number=purchase.reference_number,
                            created_by=request.user
                        )
                
                messages.success(request, 'Purchase created successfully!')
                return redirect('products:purchase_list')
            except Exception as e:
                messages.error(request, f'Error saving purchase: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PurchaseForm()
        formset = PurchaseItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Purchase',
    }
    return render(request, 'products/purchase_form.html', context)

@login_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        formset = PurchaseItemFormSet(request.POST, instance=purchase)
        
        if form.is_valid() and formset.is_valid():
            try:
                purchase = form.save(commit=False)
                purchase.updated_by = request.user
                purchase.save()
                
                formset.save()
                
                # Calculate total amount
                total = sum(item.total_price for item in purchase.items.all())
                purchase.total_amount = total
                purchase.save()
                
                messages.success(request, 'Purchase updated successfully!')
                return redirect('products:purchase_list')
            except Exception as e:
                messages.error(request, f'Error updating purchase: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PurchaseForm(instance=purchase)
        formset = PurchaseItemFormSet(instance=purchase)
    
    context = {
        'form': form,
        'formset': formset,
        'purchase': purchase,
        'title': 'Update Purchase',
    }
    return render(request, 'products/purchase_form.html', context)

@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, 'Purchase deleted successfully!')
        return redirect('products:purchase_list')
    
    context = {
        'purchase': purchase,
    }
    return render(request, 'products/purchase_confirm_delete.html', context)

# Report Views
@login_required
def inventory_report(request):
    # Get all products with their current stock value
    products = Product.objects.annotate(
        stock_value=ExpressionWrapper(
            F('current_stock') * F('buying_price'),
            output_field=DecimalField()
        )
    )
    
    # Calculate total inventory value
    total_value = products.aggregate(total=Sum('stock_value'))['total'] or 0
    
    # Get low stock products
    low_stock = products.filter(current_stock__lte=F('reorder_level'))
    
    # Get out of stock products
    out_of_stock = products.filter(current_stock=0)
    
    context = {
        'products': products,
        'total_value': total_value,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    return render(request, 'products/reports/inventory_report.html', context)

@login_required
def sales_report(request):
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    date_range = request.GET.get('date_range')
    if date_range:
        if date_range == 'week':
            start_date = end_date - timedelta(days=7)
        elif date_range == 'month':
            start_date = end_date - timedelta(days=30)
        elif date_range == 'quarter':
            start_date = end_date - timedelta(days=90)
        elif date_range == 'year':
            start_date = end_date - timedelta(days=365)
    
    # Get custom date range if provided
    custom_start = request.GET.get('start_date')
    custom_end = request.GET.get('end_date')
    if custom_start and custom_end:
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Get sales transactions
    sales = InventoryTransaction.objects.filter(
        transaction_type='sale',
        created_at__date__range=[start_date, end_date]
    )
    
    # Calculate total sales
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get top selling products
    top_products = Product.objects.annotate(
        sales_count=Sum(
            'transactions__quantity',
            filter=Q(
                transactions__transaction_type='sale',
                transactions__created_at__date__range=[start_date, end_date]
            )
        )
    ).filter(sales_count__gt=0).order_by('-sales_count')[:10]
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'top_products': top_products,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range or 'custom',
    }
    return render(request, 'products/reports/sales_report.html', context)

@login_required
def purchases_report(request):
    # Get date range
    end_date = request.GET.get('end_date', None)
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.now().date()
        
    start_date = request.GET.get('start_date', None)
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    
    status = request.GET.get('status', None)
    
    # Get purchases data
    purchases_query = Purchase.objects.filter(
        purchase_date__range=[start_date, end_date]
    )
    
    if status:
        purchases_query = purchases_query.filter(status=status)
    
    total_purchases = purchases_query.count()
    total_amount = purchases_query.aggregate(total=Sum('total_amount'))['total'] or 0
    total_items = PurchaseItem.objects.filter(purchase__in=purchases_query).count()
    total_suppliers = purchases_query.values('supplier').distinct().count()
    
    # Group purchases by month
    purchases_by_month = purchases_query.annotate(
        month=TruncMonth('purchase_date')
    ).values('month').annotate(
        amount=Sum('total_amount')
    ).order_by('month')
    
    purchase_trend_labels = [item['month'].strftime('%b %Y') for item in purchases_by_month]
    purchase_trend_data = [float(item['amount']) for item in purchases_by_month]

    # Get top suppliers
    top_suppliers = Supplier.objects.annotate(
        total_purchases=Sum('product_purchases__total_amount'),
        purchase_count=Count('product_purchases')
    ).filter(
        product_purchases__isnull=False
    ).order_by('-total_purchases')[:5]
    
    # Calculate percentages for top suppliers
    top_suppliers_data = []
    for supplier in top_suppliers:
        percentage = (supplier.total_purchases / total_amount) * 100 if total_amount > 0 else 0
        top_suppliers_data.append({
            'name': supplier.name,
            'total_purchases': supplier.total_purchases,
            'purchase_count': supplier.purchase_count,
            'percentage': percentage
        })
    
    top_suppliers_labels = [supplier['name'] for supplier in top_suppliers_data]
    top_suppliers_amounts = [float(supplier['total_purchases']) for supplier in top_suppliers_data]
    
    # Get recent purchases
    recent_purchases = purchases_query.order_by('-purchase_date')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'total_purchases': total_purchases,
        'total_amount': total_amount,
        'total_items': total_items,
        'total_suppliers': total_suppliers,
        'purchase_trend_labels': json.dumps(purchase_trend_labels),
        'purchase_trend_data': json.dumps(purchase_trend_data),
        'top_suppliers': top_suppliers_data,
        'top_suppliers_labels': json.dumps(top_suppliers_labels),
        'top_suppliers_amounts': json.dumps(top_suppliers_amounts),
        'recent_purchases': recent_purchases
    }
    
    return render(request, 'products/reports/purchases_report.html', context) 