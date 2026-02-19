from django.db import models
from django.utils import timezone


class Trip(models.Model):
    """Model to store trip information"""
    created_at = models.DateTimeField(default=timezone.now)
    current_location = models.CharField(max_length=500)
    pickup_location = models.CharField(max_length=500)
    dropoff_location = models.CharField(max_length=500)
    current_cycle_used = models.FloatField(help_text="Hours used out of 70 in rolling 8 days")
    
    # Trip calculations
    total_miles = models.FloatField(null=True, blank=True)
    total_driving_hours = models.FloatField(null=True, blank=True)
    total_days = models.IntegerField(null=True, blank=True)
    
    # Route data
    route_data = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Trip {self.id} - {self.pickup_location} to {self.dropoff_location}"


class DailyLog(models.Model):
    """Model to store daily HOS logs"""
    DUTY_STATUS_CHOICES = [
        ('OFF', 'Off Duty'),
        ('SB', 'Sleeper Berth'),
        ('D', 'Driving'),
        ('ON', 'On Duty (Not Driving)'),
    ]
    
    trip = models.ForeignKey(Trip, related_name='daily_logs', on_delete=models.CASCADE)
    day_number = models.IntegerField()
    date = models.DateField()
    
    # Log entries as JSON array
    log_entries = models.JSONField(help_text="Array of {status, start_time, end_time, duration, notes}")
    
    # Daily summary
    total_driving_hours = models.FloatField()
    total_on_duty_hours = models.FloatField()
    total_off_duty_hours = models.FloatField()
    
    # Remaining hours
    remaining_drive_time = models.FloatField()
    remaining_on_duty_time = models.FloatField()
    cycle_hours_remaining = models.FloatField()
    
    class Meta:
        ordering = ['day_number']
    
    def __str__(self):
        return f"Day {self.day_number} - Trip {self.trip.id}"


class LogEntry(models.Model):
    """Individual log entry for a duty status change"""
    DUTY_STATUS_CHOICES = [
        ('OFF', 'Off Duty'),
        ('SB', 'Sleeper Berth'),
        ('D', 'Driving'),
        ('ON', 'On Duty (Not Driving)'),
    ]
    
    daily_log = models.ForeignKey(DailyLog, related_name='entries', on_delete=models.CASCADE)
    status = models.CharField(max_length=3, choices=DUTY_STATUS_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.FloatField()
    notes = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.status} - {self.start_time} to {self.end_time}"
