from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profiles/', views.profile_selection, name='profile_selection'),
    path('profile/create/', views.profile_create, name='profile_create'),
    path('profile/<int:pk>/select/', views.profile_select, name='profile_select'),
]