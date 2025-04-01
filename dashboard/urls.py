from django.urls import path
from . import views
from .views import (
    DashboardView, 
    ScheduleView, 
    CalendarView, 
    StatisticsView,
    ProfileView  
)

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    
    # Add profile URL
    path('profile/', ProfileView.as_view(), name='profile'),
]
