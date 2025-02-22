from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile

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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('authentication:profile_selection')
        else:
            messages.error(request, 'Invalid username or password')
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
        name = request.POST.get('name')
        avatar = request.FILES.get('avatar')
        pin = request.POST.get('pin') # Get the PIN from the form
        profile = Profile.objects.create(
            user=request.user,
            name=name,
            avatar=avatar,
            pin=pin # Save the PIN
        )
        return redirect('authentication:profile_selection')
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