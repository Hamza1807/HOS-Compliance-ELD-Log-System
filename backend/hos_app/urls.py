"""
URL configuration for HOS app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('calculate-trip/', views.calculate_trip, name='calculate_trip'),
    path('trips/', views.list_trips, name='list_trips'),
    path('trips/<int:trip_id>/', views.get_trip, name='get_trip'),
    path('trips/<int:trip_id>/download-logs/', views.download_eld_logs, name='download_logs'),
]
