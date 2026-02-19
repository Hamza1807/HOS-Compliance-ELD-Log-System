"""
API Views for HOS application
"""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone

from .models import Trip, DailyLog
from .serializers import TripSerializer, TripInputSerializer, DailyLogSerializer
from .hos_engine import HOSEngine
from .route_service import RouteService
from .eld_generator import ELDLogGenerator

import json
from datetime import datetime
import json


def serialize_datetime_in_dict(obj):
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime_in_dict(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_in_dict(item) for item in obj]
    return obj


@api_view(['POST'])
def calculate_trip(request):
    """
    Calculate trip with HOS compliance
    
    POST /api/calculate-trip/
    Body: {
        "current_location": "New York, NY",
        "pickup_location": "Chicago, IL", 
        "dropoff_location": "Los Angeles, CA",
        "current_cycle_used": 15.5
    }
    """
    serializer = TripInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Step 1: Calculate route
        route_service = RouteService()  # Add API key here if available
        
        locations = [
            data['current_location'],
            data['pickup_location'],
            data['dropoff_location']
        ]
        
        route_data = route_service.calculate_route(locations)
        
        # Step 2: Calculate HOS compliance
        hos_engine = HOSEngine(current_cycle_used=data['current_cycle_used'])
        trip_plan = hos_engine.calculate_trip(
            total_miles=route_data['total_miles']
        )
        
        # Step 3: Generate ELD logs
        eld_generator = ELDLogGenerator()
        
        # Add ELD grid data to each daily log
        for day_log in trip_plan['daily_logs']:
            day_log['eld_grid'] = eld_generator.generate_json_for_frontend(day_log)
        
        # Step 4: Save to database (optional)
        trip = Trip.objects.create(
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            current_cycle_used=data['current_cycle_used'],
            total_miles=route_data['total_miles'],
            total_driving_hours=trip_plan['total_driving_hours'],
            total_days=trip_plan['actual_days'],
            route_data=route_data
        )
        
        # Create daily logs
        for day_log_data in trip_plan['daily_logs']:
            # Serialize datetime objects in log_entries
            serialized_log_entries = serialize_datetime_in_dict(day_log_data['log_entries'])
            
            DailyLog.objects.create(
                trip=trip,
                day_number=day_log_data['day_number'],
                date=datetime.fromisoformat(day_log_data['date']) if isinstance(day_log_data['date'], str) else day_log_data['date'],
                log_entries=serialized_log_entries,
                total_driving_hours=day_log_data['total_driving_hours'],
                total_on_duty_hours=day_log_data['total_on_duty_hours'],
                total_off_duty_hours=day_log_data['total_off_duty_hours'],
                remaining_drive_time=day_log_data['remaining_drive_time'],
                remaining_on_duty_time=day_log_data['remaining_on_duty_time'],
                cycle_hours_remaining=day_log_data['cycle_hours_remaining']
            )
        
        # Step 5: Return complete response
        # Serialize datetime objects for JSON response
        serialized_trip_plan = serialize_datetime_in_dict(trip_plan)
        
        response_data = {
            'trip_id': trip.id,
            'route': route_data,
            'trip_plan': serialized_trip_plan,
            'summary': {
                'total_miles': route_data['total_miles'],
                'total_driving_hours': trip_plan['total_driving_hours'],
                'total_days': trip_plan['actual_days'],
                'cycle_before': trip_plan['cycle_used_before'],
                'cycle_after': trip_plan['cycle_used_after'],
                'restart_needed': trip_plan['restart_needed']
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_trip(request, trip_id):
    """
    Get trip details
    
    GET /api/trips/{trip_id}/
    """
    try:
        trip = Trip.objects.get(id=trip_id)
        serializer = TripSerializer(trip)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Trip.DoesNotExist:
        return Response(
            {'error': 'Trip not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def download_eld_logs(request, trip_id):
    """
    Download ELD logs as SVG files (zipped)
    
    GET /api/trips/{trip_id}/download-logs/
    """
    try:
        trip = Trip.objects.get(id=trip_id)
        daily_logs = trip.daily_logs.all()
        
        eld_generator = ELDLogGenerator()
        
        # For now, return JSON with SVG strings
        # In production, you'd zip these files
        svgs = []
        for day_log in daily_logs:
            # Convert to dict format
            day_log_dict = {
                'day_number': day_log.day_number,
                'date': day_log.date.isoformat(),
                'log_entries': day_log.log_entries,
                'total_driving_hours': day_log.total_driving_hours,
                'total_on_duty_hours': day_log.total_on_duty_hours,
                'total_off_duty_hours': day_log.total_off_duty_hours,
                'remaining_drive_time': day_log.remaining_drive_time,
                'remaining_on_duty_time': day_log.remaining_on_duty_time,
                'cycle_hours_remaining': day_log.cycle_hours_remaining,
            }
            
            svg = eld_generator.generate_daily_log_svg(day_log_dict)
            svgs.append({
                'day': day_log.day_number,
                'svg': svg
            })
        
        return Response({
            'trip_id': trip_id,
            'logs': svgs
        }, status=status.HTTP_200_OK)
        
    except Trip.DoesNotExist:
        return Response(
            {'error': 'Trip not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_trips(request):
    """
    List all trips
    
    GET /api/trips/
    """
    trips = Trip.objects.all().order_by('-created_at')[:50]
    serializer = TripSerializer(trips, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    
    GET /api/health/
    """
    return Response({
        'status': 'ok',
        'message': 'HOS API is running'
    }, status=status.HTTP_200_OK)
