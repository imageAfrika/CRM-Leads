from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import Group

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
        role = request.POST.get('role')

        # Debug prints
        print(f"Login attempt - Username: {username}, Role: {role}")

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"User authenticated - Is superuser: {user.is_superuser}, Is staff: {user.is_staff}")
            print(f"User groups: {list(user.groups.all())}")
            
            # Check if user has the appropriate role
            if role == 'admin' and user.is_superuser:
                login(request, user)
                profile = Profile.objects.filter(user=user).first()
                if not profile:
                    profile = Profile.objects.create(
                        user=user,
                        name='Administrator',
                        pin='0000'
                    )
                request.session['profile_id'] = profile.id
                return redirect('dashboard:dashboard')
            
            elif role == 'staff' and user.is_staff:  # Changed condition
                if not user.groups.filter(name='Staff').exists():
                    # Add user to Staff group if not already in it
                    from django.contrib.auth.models import Group
                    staff_group, _ = Group.objects.get_or_create(name='Staff')
                    user.groups.add(staff_group)
                
                login(request, user)
                return redirect('authentication:profile_selection')
            
            else:
                if role == 'admin':
                    messages.error(request, 'You do not have administrator privileges')
                else:
                    messages.error(request, 'You do not have staff privileges')
        else:
            messages.error(request, 'Invalid username or password')
            print("Authentication failed")
    
    return render(request, 'authentication/login.html')

@login_required
def logout_view(request):
    # Clear profile from session on logout
    if 'profile_id' in request.session:
        del request.session['profile_id']
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
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Incorrect PIN. Please try again.')
        
        return render(request, 'authentication/profile_select.html', {'profile': profile})
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('authentication:profile_selection')

def index_view(request):
    if request.user.is_authenticated:
        if request.session.get('profile_id'):
            return redirect('dashboard:dashboard')
        return redirect('authentication:profile_selection')
    return redirect('authentication:login') 