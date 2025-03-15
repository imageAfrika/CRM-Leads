from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('', views.registration_home, name='registration_home'),
    path('register-company/', views.register_company, name='register_company'),
    path('register-user/', views.register_user, name='register_user'),
    path('subscription-plans/', views.subscription_plans, name='subscription_plans'),
    path('app-selection/', views.app_selection, name='app_selection'),
] 