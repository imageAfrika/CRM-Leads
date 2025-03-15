from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal
from .models import Account, Transaction, Debt, Tax
from projects.models import Project
import uuid
import random
import string

@login_required
def dashboard(request):
    """
    Display the banking dashboard with account overview, recent transactions, and active debts.
    """
    accounts = Account.objects.filter(owner=request.user, is_active=True)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        account__owner=request.user
    ).order_by('-timestamp')[:10]
    
    # Get active debts
    active_debts = Debt.objects.filter(
        account__owner=request.user,
        is_active=True
    )
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'active_debts': active_debts,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/dashboard.html', context)

@login_required
def account_detail(request, account_number):
    """
    Display details for a specific account, including recent transactions.
    """
    account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')[:20]
    
    context = {
        'account': account,
        'transactions': transactions,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/account_detail.html', context)

@login_required
def create_account(request):
    """
    Create a new bank account with a random account number and PIN.
    """
    # Fetch all registered projects
    projects = Project.objects.all()  # Adjust the query as needed (e.g., filter by user, status, etc.)
    
    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        
        # Generate a random account number
        account_number = ''.join(random.choices(string.digits, k=10))
        
        # Generate a random PIN
        pin = ''.join(random.choices(string.digits, k=4))
        
        try:
            # Get the project instance based on the selected project ID
            project = Project.objects.get(id=account_type)
            
            # Create the account
            account = Account.objects.create(
                account_number=account_number,
                account_type='PROJECT',  # Set account type to PROJECT
                owner=request.user,
                pin=pin,
                balance=0.00,
                project=project  # Link the account to the selected project
            )
            
            messages.success(request, f'Account created successfully! Your account number is {account_number} and your PIN is {pin}. Please keep these safe.')
            return redirect('banking:account_detail', account_number=account_number)
        except Project.DoesNotExist:
            messages.error(request, 'Selected project does not exist.')
    
    context = {
        'projects': projects,  # Add the projects to the context
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/create_account.html', context)

@login_required
def deposit(request, account_number):
    """
    Deposit funds into an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        
        try:
            account.deposit(amount)
            messages.success(request, f'Successfully deposited ${amount} to your account.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('banking:account_detail', account_number=account_number)
    
    context = {
        'account': account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/deposit.html', context)

@login_required
def withdraw(request, account_number):
    """
    Withdraw funds from an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        pin = request.POST.get('pin')
        
        try:
            account.withdraw(amount, pin)
            messages.success(request, f'Successfully withdrew ${amount} from your account.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('banking:account_detail', account_number=account_number)
    
    context = {
        'account': account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/withdraw.html', context)

@login_required
def transfer(request, account_number):
    """
    Transfer funds from one account to another.
    """
    source_account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    
    if request.method == 'POST':
        destination_account_number = request.POST.get('destination_account')
        amount = Decimal(request.POST.get('amount', 0))
        pin = request.POST.get('pin')
        
        try:
            destination_account = Account.objects.get(account_number=destination_account_number)
            source_account.transfer(destination_account, amount, pin)
            messages.success(request, f'Successfully transferred ${amount} to account {destination_account_number}.')
        except Account.DoesNotExist:
            messages.error(request, 'Destination account not found.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('banking:account_detail', account_number=account_number)
    
    context = {
        'account': source_account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/transfer.html', context)

@login_required
def transaction_history(request, account_number=None):
    """
    Display transaction history for a specific account or all accounts.
    """
    if account_number:
        account = get_object_or_404(Account, account_number=account_number, owner=request.user)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
        context = {
            'account': account, 
            'transactions': transactions,
            'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
        }
    else:
        transactions = Transaction.objects.filter(account__owner=request.user).order_by('-timestamp')
        context = {
            'transactions': transactions,
            'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
        }
    
    return render(request, 'banking/transaction_history.html', context)

@login_required
def change_pin(request, account_number):
    """
    Change the PIN for an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    
    if request.method == 'POST':
        current_pin = request.POST.get('current_pin')
        new_pin = request.POST.get('new_pin')
        confirm_pin = request.POST.get('confirm_pin')
        
        if current_pin != account.pin:
            messages.error(request, 'Current PIN is incorrect.')
        elif new_pin != confirm_pin:
            messages.error(request, 'New PIN and confirmation do not match.')
        elif len(new_pin) != 4 or not new_pin.isdigit():
            messages.error(request, 'PIN must be a 4-digit number.')
        else:
            account.pin = new_pin
            account.save()
            messages.success(request, 'PIN changed successfully.')
            return redirect('banking:account_detail', account_number=account_number)
    
    context = {
        'account': account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/change_pin.html', context)

@login_required
def payment(request, account_number):
    """
    Make a payment from an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner=request.user)
    
    if request.method == 'POST':
        payee = request.POST.get('payee')
        amount = Decimal(request.POST.get('amount', 0))
        description = request.POST.get('description')
        pin = request.POST.get('pin')
        
        try:
            if pin != account.pin:
                raise ValueError("Invalid PIN")
            if amount <= 0:
                raise ValueError("Payment amount must be positive")
            if account.balance < amount:
                raise ValueError("Insufficient funds")
                
            account.balance -= amount
            account.save()
            
            Transaction.objects.create(
                account=account,
                transaction_type='PAYMENT',
                amount=amount,
                description=f"Payment to {payee}: {description}"
            )
            
            messages.success(request, f'Payment of ${amount} to {payee} was successful.')
            return redirect('banking:account_detail', account_number=account_number)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'account': account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/payment.html', context)

@login_required
def report_list(request):
    """
    Display a list of reports.
    """
    # Logic to retrieve and display reports
    return render(request, 'reports/report_list.html', {
        'title': 'Report List'
    })
