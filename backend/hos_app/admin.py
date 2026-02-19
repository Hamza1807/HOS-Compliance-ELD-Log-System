from django.contrib import admin
from .models import Trip, DailyLog, LogEntry


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['id', 'pickup_location', 'dropoff_location', 'total_miles', 'total_days', 'created_at']
    list_filter = ['created_at']
    search_fields = ['pickup_location', 'dropoff_location']


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'trip', 'day_number', 'date', 'total_driving_hours', 'total_on_duty_hours']
    list_filter = ['date']


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'daily_log', 'status', 'start_time', 'end_time', 'duration_hours']
    list_filter = ['status', 'start_time']
