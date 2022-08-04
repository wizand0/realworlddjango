from django.urls import path, include
from . import views


app_name = 'events'


urlpatterns = [
    path('list/', views.Eventlist.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.Eventdetail, name='event_detail')
]