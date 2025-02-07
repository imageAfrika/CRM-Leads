from django.urls import path
from . import views
from .views import DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
]
