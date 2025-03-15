from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('', views.people_list, name='people_list'),
    path('register/', views.register_person, name='register_person'),
    path('<int:pk>/', views.person_detail, name='person_detail'),
    path('contact/', views.contact_people, name='contact_people'),
    path('debug-static/', views.debug_static, name='debug_static'),  # Debug URL for static files
]