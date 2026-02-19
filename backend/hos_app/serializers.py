from rest_framework import serializers
from .models import Trip, DailyLog, LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = ['id', 'status', 'start_time', 'end_time', 'duration_hours', 'notes', 'location']


class DailyLogSerializer(serializers.ModelSerializer):
    entries = LogEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = DailyLog
        fields = [
            'id', 'day_number', 'date', 'log_entries', 'entries',
            'total_driving_hours', 'total_on_duty_hours', 'total_off_duty_hours',
            'remaining_drive_time', 'remaining_on_duty_time', 'cycle_hours_remaining'
        ]


class TripSerializer(serializers.ModelSerializer):
    daily_logs = DailyLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'created_at', 'current_location', 'pickup_location', 
            'dropoff_location', 'current_cycle_used', 'total_miles', 
            'total_driving_hours', 'total_days', 'route_data', 'daily_logs'
        ]


class TripInputSerializer(serializers.Serializer):
    """Serializer for trip input"""
    current_location = serializers.CharField(max_length=500)
    pickup_location = serializers.CharField(max_length=500)
    dropoff_location = serializers.CharField(max_length=500)
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)
