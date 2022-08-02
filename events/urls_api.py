from django.urls import path
from . import views


app_name = 'api_events'


urlpatterns = [
    path('reviews/create/', views.create_review.as_view(), name='create_review'),
]