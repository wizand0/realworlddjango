from django.urls import path, include
from . import views


app_name = 'events'


urlpatterns = [
    path('list/', views.event_list, name='event_list'),
    path('detail/<int:pk>/', views.event_detail, name='event_detail'),
]