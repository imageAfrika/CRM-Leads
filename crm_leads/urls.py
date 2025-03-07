"""
URL configuration for crm_leads project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from documents.views import quote_create, quote_detail
from dashboard.views import DashboardView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
# from . import views

urlpatterns = [
    # Redirect root URL to login
    path('', RedirectView.as_view(url='auth/login/', permanent=False), name='index'),
    
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path('clients/', include('clients.urls')),
    path('sales/', include('sales.urls')),
    path('documents/', include('documents.urls')),  
    path('expenses/', include('expenses.urls')),  # Add expenses URLs
    path('purchases/', include('purchases.urls')),  # Add purchases URLs
    path('banking/', include('banking.urls')),  # Add banking URLs
    path('reports/', include('reports.urls')),  # Add reports URLs
    path('products/', include('products.urls')),  # Add products URLs
    path('access-control/', include('access_control.urls')),  # Add access control URLs
    # path('documents/quote/', include('documents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
