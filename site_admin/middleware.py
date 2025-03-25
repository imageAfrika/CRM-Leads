from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings


class SiteAdminMiddleware:
    """
    Middleware to ensure that only staff and superusers can access the site admin.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        if request.path.startswith('/site-admin/') and not request.path.startswith('/site-admin/login/') and not request.user.is_authenticated:
            # Redirect to site admin login page if user is not authenticated
            messages.warning(request, 'Please log in to access the site administration.')
            return redirect('/admin/login/?next=' + request.path)
        
        if request.path.startswith('/site-admin/') and not request.path.startswith('/site-admin/login/') and not request.user.is_staff:
            # Redirect to homepage if user is not staff
            messages.error(request, 'You do not have permission to access the site administration.')
            return redirect('/')
        
        response = self.get_response(request)
        return response
