from django.urls import path
from . import views
from .views import DashboardView, ScheduleView, CalendarView, StatisticsView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
]
