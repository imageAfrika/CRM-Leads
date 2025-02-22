from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Profile

class ProfileAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication
        public_urls = [
            reverse('authentication:login'),
            reverse('authentication:profile_selection'),
            reverse('authentication:profile_select', args=[0]).rsplit('0', 1)[0],  # Base profile select URL
            '/static/',
            '/media/',
            '/admin/',
        ]

        # Check if the current URL is public
        is_public_url = any(request.path.startswith(url) for url in public_urls)

        # Always attach profile to request if user is authenticated
        if request.user.is_authenticated:
            profile_id = request.session.get('profile_id')
            if profile_id:
                try:
                    # Get profile and attach to request
                    profile = Profile.objects.get(id=profile_id, user=request.user)
                    request.profile = profile
                except Profile.DoesNotExist:
                    request.profile = None
                    if not is_public_url:
                        del request.session['profile_id']
                        messages.warning(request, 'Profile not found. Please select a profile.')
                        return redirect('authentication:profile_selection')
            else:
                request.profile = None
                if not is_public_url:
                    messages.warning(request, 'Please select a profile to continue.')
                    return redirect('authentication:profile_selection')
        else:
            request.profile = None
            if not is_public_url:
                messages.error(request, 'Please log in to access this page.')
                return redirect('authentication:login')

        response = self.get_response(request)
        return response 