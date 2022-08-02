from django.urls import path
from . import views


app_name = 'events'


urlpatterns = [
    path('list', views.EventListView.as_view(), name='event_list'),
    path('events/detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
]