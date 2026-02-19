"""
HOS (Hours of Service) Compliance Engine

Implements FMCSA regulations for property carrying drivers:
- 11-hour driving limit
- 14-hour on-duty window
- 30-minute break after 8 cumulative driving hours
- 70-hour/8-day cycle
- 10 consecutive hours off-duty to reset daily limits
- 34-hour restart to reset 70-hour cycle
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math


class HOSEngine:
    """Core HOS compliance calculation engine"""
    
    # HOS Constants
    MAX_DRIVING_HOURS = 11
    MAX_ON_DUTY_HOURS = 14
    REQUIRED_BREAK_AFTER_HOURS = 8
    REQUIRED_BREAK_DURATION = 0.5  # 30 minutes
    MAX_CYCLE_HOURS = 70
    CYCLE_DAYS = 8
    RESET_OFF_DUTY_HOURS = 10
    RESTART_OFF_DUTY_HOURS = 34
    
    # Operational Constants
    AVG_SPEED_MPH = 60
    FUEL_STOP_MILES = 1000
    FUEL_STOP_DURATION = 0.5  # 30 minutes
    PICKUP_DURATION = 1.0  # 1 hour
    DROPOFF_DURATION = 1.0  # 1 hour
    
    def __init__(self, current_cycle_used: float):
        """
        Initialize HOS Engine
        
        Args:
            current_cycle_used: Hours already used in the current 8-day cycle
        """
        self.current_cycle_used = current_cycle_used
        self.cycle_remaining = self.MAX_CYCLE_HOURS - current_cycle_used
        
    def calculate_trip(self, total_miles: float, route_segments: List[Dict] = None) -> Dict:
        """
        Calculate complete trip with HOS compliance
        
        Args:
            total_miles: Total trip distance in miles
            route_segments: Optional list of route segments with distances
            
        Returns:
            Dictionary with complete trip plan including daily logs
        """
        # Calculate basic trip metrics
        total_driving_hours = total_miles / self.AVG_SPEED_MPH
        num_fuel_stops = math.floor(total_miles / self.FUEL_STOP_MILES)
        
        # Calculate total operational time
        total_fuel_time = num_fuel_stops * self.FUEL_STOP_DURATION
        total_operational_hours = (
            total_driving_hours + 
            self.PICKUP_DURATION + 
            self.DROPOFF_DURATION + 
            total_fuel_time
        )
        
        # Estimate number of days needed
        estimated_days = math.ceil(total_driving_hours / self.MAX_DRIVING_HOURS)
        
        # Generate daily schedule
        daily_logs = self._generate_daily_schedule(
            total_miles=total_miles,
            total_driving_hours=total_driving_hours,
            num_fuel_stops=num_fuel_stops
        )
        
        return {
            'total_miles': total_miles,
            'total_driving_hours': round(total_driving_hours, 2),
            'estimated_days': estimated_days,
            'actual_days': len(daily_logs),
            'num_fuel_stops': num_fuel_stops,
            'daily_logs': daily_logs,
            'cycle_used_before': self.current_cycle_used,
            'cycle_used_after': self._calculate_final_cycle_usage(daily_logs),
            'restart_needed': self._check_restart_needed(daily_logs)
        }
    
    def _generate_daily_schedule(
        self, 
        total_miles: float, 
        total_driving_hours: float,
        num_fuel_stops: int
    ) -> List[Dict]:
        """
        Generate day-by-day schedule with HOS compliance
        
        Returns:
            List of daily logs with duty status changes
        """
        daily_logs = []
        remaining_miles = total_miles
        remaining_driving_hours = total_driving_hours
        miles_since_fuel = 0
        
        current_cycle = self.current_cycle_used
        day_number = 1
        current_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)  # Start at 6 AM
        
        # First day includes pickup
        pickup_done = False
        dropoff_done = False
        
        while remaining_driving_hours > 0 or not dropoff_done:
            # Check if 34-hour restart is needed
            if current_cycle >= self.MAX_CYCLE_HOURS:
                # Need 34-hour restart
                restart_log = self._create_restart_log(day_number, current_time)
                daily_logs.append(restart_log)
                current_cycle = 0  # Reset cycle
                current_time = restart_log['end_time']
                day_number += 1
                continue
            
            # Check if we have enough cycle hours to work
            available_cycle_hours = self.MAX_CYCLE_HOURS - current_cycle
            if available_cycle_hours < 1:
                # Need restart
                restart_log = self._create_restart_log(day_number, current_time)
                daily_logs.append(restart_log)
                current_cycle = 0
                current_time = restart_log['end_time']
                day_number += 1
                continue
            
            # Start a new day
            day_log = {
                'day_number': day_number,
                'date': current_time.date().isoformat(),
                'start_time': current_time,
                'log_entries': [],
                'total_driving_hours': 0,
                'total_on_duty_hours': 0,
                'total_off_duty_hours': 0,
            }
            
            # Available hours for this day
            max_drive_hours = min(
                self.MAX_DRIVING_HOURS,
                remaining_driving_hours,
                available_cycle_hours
            )
            max_on_duty_hours = min(
                self.MAX_ON_DUTY_HOURS,
                available_cycle_hours
            )
            
            hours_driven_today = 0
            hours_on_duty_today = 0
            hours_since_break = 0
            day_start_time = current_time
            
            # Pickup on first day
            if not pickup_done:
                entry = self._create_log_entry(
                    status='ON',
                    start_time=current_time,
                    duration=self.PICKUP_DURATION,
                    notes='Pickup - Loading'
                )
                day_log['log_entries'].append(entry)
                current_time = entry['end_time']
                hours_on_duty_today += self.PICKUP_DURATION
                pickup_done = True
            
            # Drive and manage breaks
            while (hours_driven_today < max_drive_hours and 
                   hours_on_duty_today < max_on_duty_hours and 
                   remaining_driving_hours > 0):
                
                # Check if break is needed
                if hours_since_break >= self.REQUIRED_BREAK_AFTER_HOURS:
                    entry = self._create_log_entry(
                        status='OFF',
                        start_time=current_time,
                        duration=self.REQUIRED_BREAK_DURATION,
                        notes='30-minute break (8-hour rule)'
                    )
                    day_log['log_entries'].append(entry)
                    current_time = entry['end_time']
                    hours_since_break = 0
                    continue
                
                # Check if fuel stop is needed
                if miles_since_fuel >= self.FUEL_STOP_MILES and remaining_miles > 0:
                    entry = self._create_log_entry(
                        status='ON',
                        start_time=current_time,
                        duration=self.FUEL_STOP_DURATION,
                        notes='Fuel stop'
                    )
                    day_log['log_entries'].append(entry)
                    current_time = entry['end_time']
                    hours_on_duty_today += self.FUEL_STOP_DURATION
                    miles_since_fuel = 0
                    continue
                
                # Calculate driving segment
                hours_until_break = self.REQUIRED_BREAK_AFTER_HOURS - hours_since_break
                hours_until_drive_limit = max_drive_hours - hours_driven_today
                hours_until_duty_limit = max_on_duty_hours - hours_on_duty_today
                
                drive_duration = min(
                    hours_until_break,
                    hours_until_drive_limit,
                    hours_until_duty_limit,
                    remaining_driving_hours,
                    2.0  # Max 2-hour segments for readability
                )
                
                if drive_duration < 0.1:
                    break
                
                # Create driving entry
                miles_driven = drive_duration * self.AVG_SPEED_MPH
                entry = self._create_log_entry(
                    status='D',
                    start_time=current_time,
                    duration=drive_duration,
                    notes=f'Driving - {miles_driven:.0f} miles'
                )
                day_log['log_entries'].append(entry)
                current_time = entry['end_time']
                
                hours_driven_today += drive_duration
                hours_on_duty_today += drive_duration
                hours_since_break += drive_duration
                remaining_driving_hours -= drive_duration
                remaining_miles -= miles_driven
                miles_since_fuel += miles_driven
                
                # Check if this is the last bit of driving
                if remaining_driving_hours <= 0 and not dropoff_done:
                    # Add dropoff
                    entry = self._create_log_entry(
                        status='ON',
                        start_time=current_time,
                        duration=self.DROPOFF_DURATION,
                        notes='Dropoff - Unloading'
                    )
                    day_log['log_entries'].append(entry)
                    current_time = entry['end_time']
                    hours_on_duty_today += self.DROPOFF_DURATION
                    dropoff_done = True
                    break
            
            # End of day - 10 hour rest period
            if not dropoff_done or day_number < math.ceil(total_driving_hours / self.MAX_DRIVING_HOURS):
                entry = self._create_log_entry(
                    status='SB',
                    start_time=current_time,
                    duration=self.RESET_OFF_DUTY_HOURS,
                    notes='10-hour rest period (daily reset)'
                )
                day_log['log_entries'].append(entry)
                current_time = entry['end_time']
            
            # Calculate day totals
            for entry in day_log['log_entries']:
                if entry['status'] == 'D':
                    day_log['total_driving_hours'] += entry['duration']
                if entry['status'] in ['D', 'ON']:
                    day_log['total_on_duty_hours'] += entry['duration']
                if entry['status'] in ['OFF', 'SB']:
                    day_log['total_off_duty_hours'] += entry['duration']
            
            # Update cycle
            current_cycle += day_log['total_on_duty_hours']
            
            # Calculate remaining hours
            day_log['remaining_drive_time'] = round(self.MAX_DRIVING_HOURS - day_log['total_driving_hours'], 2)
            day_log['remaining_on_duty_time'] = round(self.MAX_ON_DUTY_HOURS - day_log['total_on_duty_hours'], 2)
            day_log['cycle_hours_remaining'] = round(self.MAX_CYCLE_HOURS - current_cycle, 2)
            day_log['end_time'] = current_time
            
            # Round totals
            day_log['total_driving_hours'] = round(day_log['total_driving_hours'], 2)
            day_log['total_on_duty_hours'] = round(day_log['total_on_duty_hours'], 2)
            day_log['total_off_duty_hours'] = round(day_log['total_off_duty_hours'], 2)
            
            daily_logs.append(day_log)
            day_number += 1
            
            # Check if we're done
            if dropoff_done and remaining_driving_hours <= 0:
                break
        
        return daily_logs
    
    def _create_log_entry(
        self, 
        status: str, 
        start_time: datetime, 
        duration: float, 
        notes: str = ''
    ) -> Dict:
        """Create a single log entry"""
        end_time = start_time + timedelta(hours=duration)
        return {
            'status': status,
            'start_time': start_time,
            'end_time': end_time,
            'duration': round(duration, 2),
            'notes': notes,
            'start_time_str': start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time_str': end_time.strftime('%Y-%m-%d %H:%M'),
        }
    
    def _create_restart_log(self, day_number: int, start_time: datetime) -> Dict:
        """Create a 34-hour restart log"""
        end_time = start_time + timedelta(hours=self.RESTART_OFF_DUTY_HOURS)
        return {
            'day_number': day_number,
            'date': start_time.date().isoformat(),
            'start_time': start_time,
            'end_time': end_time,
            'log_entries': [{
                'status': 'OFF',
                'start_time': start_time,
                'end_time': end_time,
                'duration': self.RESTART_OFF_DUTY_HOURS,
                'notes': '34-hour restart (cycle reset)',
                'start_time_str': start_time.strftime('%Y-%m-%d %H:%M'),
                'end_time_str': end_time.strftime('%Y-%m-%d %H:%M'),
            }],
            'total_driving_hours': 0,
            'total_on_duty_hours': 0,
            'total_off_duty_hours': self.RESTART_OFF_DUTY_HOURS,
            'remaining_drive_time': self.MAX_DRIVING_HOURS,
            'remaining_on_duty_time': self.MAX_ON_DUTY_HOURS,
            'cycle_hours_remaining': self.MAX_CYCLE_HOURS,
            'is_restart': True
        }
    
    def _calculate_final_cycle_usage(self, daily_logs: List[Dict]) -> float:
        """Calculate total cycle hours used after trip"""
        total = self.current_cycle_used
        restart_occurred = False
        
        for log in daily_logs:
            if log.get('is_restart'):
                total = 0  # Reset on restart
                restart_occurred = True
            else:
                total += log['total_on_duty_hours']
        
        return round(total, 2)
    
    def _check_restart_needed(self, daily_logs: List[Dict]) -> bool:
        """Check if a 34-hour restart was needed during trip"""
        return any(log.get('is_restart', False) for log in daily_logs)
