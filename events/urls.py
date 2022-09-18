from django.urls import path, include
from django.views.decorators.http import require_POST

from . import views


app_name = 'events'


urlpatterns = [
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('update/<int:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('delete/<int:pk>/', views.EventDeleteView.as_view(), name='event_delete'),
    path('enroll/', require_POST(views.EventEnrollView.as_view()), name='event_enroll'),
]
