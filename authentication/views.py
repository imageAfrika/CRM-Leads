from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm

@login_required
def profile_selection(request):
    # Clear any existing profile session
    if 'profile_id' in request.session:
        del request.session['profile_id']
    request.profile = None
    
    profiles = Profile.objects.filter(user=request.user)
    return render(request, 'authentication/profiles.html', {'profiles': profiles})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'staff')  # Default to staff if not provided
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Store the role in session before doing login
            request.session['user_role'] = role
            print(f"User {username} logged in as {role}")
            
            login(request, user)
            
            # Redirect based on role
            if role == 'administrator':
                return redirect('dashboard:dashboard')
            else:
                return redirect('authentication:profile')
        else:
            messages.error(request, 'Invalid username or password')
    
    # Add the form for GET requests
    return render(request, 'authentication/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('authentication:login')

@login_required
def profile_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        avatar = request.FILES.get('avatar')
        pin = request.POST.get('pin')

        # Validate name
        restricted_names = ['admin', 'administrator', 'owner']
        if name.lower() in restricted_names:
            messages.error(request, 'This profile name is not allowed')
            return render(request, 'authentication/profile_form.html')

        # Validate PIN
        if not pin or not pin.isdigit() or len(pin) != 4:
            messages.error(request, 'PIN must be 4 digits')
            return render(request, 'authentication/profile_form.html')

        try:
            profile = Profile.objects.create(
                user=request.user,
                name=name,
                avatar=avatar,
                pin=pin
            )
            messages.success(request, 'Profile created successfully')
            return redirect('authentication:profile_selection')
        except Exception as e:
            messages.error(request, f'Error creating profile: {str(e)}')
            return render(request, 'authentication/profile_form.html')

    return render(request, 'authentication/profile_form.html')

@login_required
def profile_select(request, pk):
    try:
        profile = Profile.objects.get(id=pk, user=request.user)
        
        if request.method == 'POST':
            pin = request.POST.get('pin')
            if pin == profile.pin:
                # Store profile ID in session
                request.session['profile_id'] = profile.id
                # Store profile in request
                request.profile = profile
                messages.success(request, f'Welcome back, {profile.name}!')
                
                # Get the role from session
                role = request.session.get('user_role', 'staff')
                
                # Ensure the profile has the correct role
                profile.role = role  
                profile.save()
                
                # Redirect based on role
                if role == 'administrator':
                    return redirect('dashboard:dashboard')
                else:  # staff role
                    return redirect('authentication:profile')
            else:
                messages.error(request, 'Incorrect PIN. Please try again.')
        
        return render(request, 'authentication/profile_select.html', {'profile': profile})
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('authentication:profile_selection')

@login_required
def profile_view(request):
    role = request.session.get('user_role', None)
    
    # For administrator role, redirect immediately to dashboard
    if role == 'administrator':
        return redirect('dashboard:dashboard')
    
    # Otherwise render template, but with a fixed context
    return render(request, 'authentication/profile_fixed.html', {})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('authentication:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'authentication/password_change.html', {'form': form})

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                subject_template_name='authentication/password_reset_subject.txt',
                email_template_name='authentication/password_reset_email.html'
            )
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('authentication:login')
    else:
        form = PasswordResetForm()
    return render(request, 'authentication/password_reset.html', {'form': form})

def index_view(request):
    if request.user.is_authenticated:
        if request.session.get('profile_id'):
            return redirect('dashboard:dashboard')
        return redirect('authentication:profile_selection')
    return redirect('authentication:login') 