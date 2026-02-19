"""
ELD Log Generator

Generates FMCSA-compliant ELD logs with graph grids
Following the format shown in FMCSA guide pages 15-18
"""

import svgwrite
from datetime import datetime, timedelta
from typing import List, Dict
import io


class ELDLogGenerator:
    """Generator for FMCSA-compliant ELD log sheets"""
    
    # Grid dimensions (matching FMCSA format)
    WIDTH = 1200
    HEIGHT = 600
    MARGIN_LEFT = 100
    MARGIN_RIGHT = 50
    MARGIN_TOP = 150
    MARGIN_BOTTOM = 100
    
    # Graph dimensions
    GRAPH_WIDTH = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    GRAPH_HEIGHT = 400
    
    # Duty status Y positions (from top)
    STATUS_POSITIONS = {
        'OFF': 0,      # Off Duty
        'SB': 1,       # Sleeper Berth
        'D': 2,        # Driving
        'ON': 3,       # On Duty (Not Driving)
    }
    
    STATUS_LABELS = {
        'OFF': 'Off Duty',
        'SB': 'Sleeper Berth',
        'D': 'Driving',
        'ON': 'On Duty (Not Driving)',
    }
    
    def __init__(self):
        """Initialize ELD log generator"""
        pass
    
    def generate_daily_log_svg(self, day_log: Dict, driver_name: str = "Driver") -> str:
        """
        Generate SVG for a single day's log
        
        Args:
            day_log: Daily log data with entries
            driver_name: Driver name to display
            
        Returns:
            SVG as string
        """
        dwg = svgwrite.Drawing(size=(self.WIDTH, self.HEIGHT))
        
        # Add styles
        dwg.defs.add(dwg.style("""
            .grid-line { stroke: #ccc; stroke-width: 1; }
            .grid-line-bold { stroke: #666; stroke-width: 2; }
            .status-line { stroke: #000; stroke-width: 3; fill: none; }
            .label { font-family: Arial, sans-serif; font-size: 14px; }
            .label-small { font-family: Arial, sans-serif; font-size: 11px; }
            .title { font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; }
            .header { font-family: Arial, sans-serif; font-size: 12px; }
        """))
        
        # Draw header
        self._draw_header(dwg, day_log, driver_name)
        
        # Draw grid
        self._draw_grid(dwg)
        
        # Draw duty status lines
        self._draw_status_lines(dwg, day_log)
        
        # Draw summary
        self._draw_summary(dwg, day_log)
        
        return dwg.tostring()
    
    def _draw_header(self, dwg, day_log: Dict, driver_name: str):
        """Draw header information"""
        y_pos = 30
        
        # Title
        dwg.add(dwg.text(
            'RECORD OF DUTY STATUS',
            insert=(self.WIDTH // 2, y_pos),
            text_anchor='middle',
            class_='title'
        ))
        
        y_pos += 30
        
        # Date and driver info
        date_str = day_log.get('date', datetime.now().strftime('%Y-%m-%d'))
        dwg.add(dwg.text(
            f"Date: {date_str}",
            insert=(self.MARGIN_LEFT, y_pos),
            class_='header'
        ))
        
        dwg.add(dwg.text(
            f"Driver: {driver_name}",
            insert=(self.WIDTH - self.MARGIN_RIGHT - 200, y_pos),
            class_='header'
        ))
        
        y_pos += 25
        
        # Day number
        day_num = day_log.get('day_number', 1)
        dwg.add(dwg.text(
            f"Day {day_num}",
            insert=(self.MARGIN_LEFT, y_pos),
            class_='header'
        ))
    
    def _draw_grid(self, dwg):
        """Draw the 24-hour grid"""
        graph_top = self.MARGIN_TOP
        graph_left = self.MARGIN_LEFT
        
        # Draw vertical hour lines (24 hours)
        hour_width = self.GRAPH_WIDTH / 24
        for i in range(25):  # 0 to 24
            x = graph_left + (i * hour_width)
            
            # Bold lines every 2 hours
            line_class = 'grid-line-bold' if i % 2 == 0 else 'grid-line'
            
            dwg.add(dwg.line(
                start=(x, graph_top),
                end=(x, graph_top + self.GRAPH_HEIGHT),
                class_=line_class
            ))
            
            # Hour labels
            if i < 24:
                dwg.add(dwg.text(
                    f"{i:02d}",
                    insert=(x + 2, graph_top - 5),
                    class_='label-small'
                ))
        
        # Draw horizontal status lines (4 status levels)
        status_height = self.GRAPH_HEIGHT / 4
        status_order = ['OFF', 'SB', 'D', 'ON']
        
        for i in range(5):  # 5 lines for 4 sections
            y = graph_top + (i * status_height)
            
            dwg.add(dwg.line(
                start=(graph_left, y),
                end=(graph_left + self.GRAPH_WIDTH, y),
                class_='grid-line-bold'
            ))
            
            # Status labels
            if i < 4:
                status = status_order[i]
                label_y = y + (status_height / 2) + 5
                dwg.add(dwg.text(
                    self.STATUS_LABELS[status],
                    insert=(graph_left - 10, label_y),
                    text_anchor='end',
                    class_='label-small'
                ))
    
    def _draw_status_lines(self, dwg, day_log: Dict):
        """Draw duty status lines on the graph"""
        graph_top = self.MARGIN_TOP
        graph_left = self.MARGIN_LEFT
        hour_width = self.GRAPH_WIDTH / 24
        status_height = self.GRAPH_HEIGHT / 4
        
        log_entries = day_log.get('log_entries', [])
        
        if not log_entries:
            return
        
        # Get day start time
        day_date = datetime.fromisoformat(day_log['date'])
        day_start = day_date.replace(hour=0, minute=0, second=0)
        
        # Create path for status line
        path_data = []
        
        for i, entry in enumerate(log_entries):
            status = entry['status']
            start_time = entry['start_time']
            end_time = entry['end_time']
            
            # Handle datetime objects or strings
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Calculate hours from midnight
            start_hours = (start_time - day_start).total_seconds() / 3600
            end_hours = (end_time - day_start).total_seconds() / 3600
            
            # Clip to 24-hour window
            start_hours = max(0, min(24, start_hours))
            end_hours = max(0, min(24, end_hours))
            
            # Calculate positions
            x1 = graph_left + (start_hours * hour_width)
            x2 = graph_left + (end_hours * hour_width)
            
            # Y position based on status
            status_index = self.STATUS_POSITIONS.get(status, 0)
            y = graph_top + (status_index * status_height) + (status_height / 2)
            
            # Add to path
            if i == 0:
                path_data.append(f"M {x1},{y}")
            else:
                # Draw vertical line to connect status changes
                prev_entry = log_entries[i - 1]
                prev_status = prev_entry['status']
                prev_status_index = self.STATUS_POSITIONS.get(prev_status, 0)
                prev_y = graph_top + (prev_status_index * status_height) + (status_height / 2)
                
                if status != prev_status:
                    path_data.append(f"L {x1},{prev_y}")
                    path_data.append(f"L {x1},{y}")
            
            # Draw horizontal line for this status
            path_data.append(f"L {x2},{y}")
        
        # Draw the path
        if path_data:
            dwg.add(dwg.path(
                d=' '.join(path_data),
                class_='status-line'
            ))
    
    def _draw_summary(self, dwg, day_log: Dict):
        """Draw summary information below the graph"""
        summary_y = self.MARGIN_TOP + self.GRAPH_HEIGHT + 30
        x = self.MARGIN_LEFT
        
        # Totals
        dwg.add(dwg.text(
            f"Total Driving: {day_log.get('total_driving_hours', 0):.2f} hrs",
            insert=(x, summary_y),
            class_='label'
        ))
        
        dwg.add(dwg.text(
            f"Total On Duty: {day_log.get('total_on_duty_hours', 0):.2f} hrs",
            insert=(x + 200, summary_y),
            class_='label'
        ))
        
        dwg.add(dwg.text(
            f"Cycle Remaining: {day_log.get('cycle_hours_remaining', 0):.2f} hrs",
            insert=(x + 400, summary_y),
            class_='label'
        ))
        
        # Remaining hours
        summary_y += 25
        dwg.add(dwg.text(
            f"Drive Time Remaining: {day_log.get('remaining_drive_time', 0):.2f} hrs",
            insert=(x, summary_y),
            class_='label-small'
        ))
        
        dwg.add(dwg.text(
            f"On Duty Remaining: {day_log.get('remaining_on_duty_time', 0):.2f} hrs",
            insert=(x + 250, summary_y),
            class_='label-small'
        ))
    
    def generate_all_logs_svg(self, daily_logs: List[Dict], driver_name: str = "Driver") -> List[str]:
        """
        Generate SVG for all daily logs
        
        Args:
            daily_logs: List of daily log data
            driver_name: Driver name
            
        Returns:
            List of SVG strings
        """
        svgs = []
        for day_log in daily_logs:
            svg = self.generate_daily_log_svg(day_log, driver_name)
            svgs.append(svg)
        return svgs
    
    def generate_json_for_frontend(self, day_log: Dict) -> Dict:
        """
        Generate structured JSON for frontend rendering
        
        Args:
            day_log: Daily log data
            
        Returns:
            Dictionary with grid data for frontend
        """
        # Get day start time
        day_date = datetime.fromisoformat(day_log['date'])
        day_start = day_date.replace(hour=0, minute=0, second=0)
        
        log_entries = day_log.get('log_entries', [])
        
        # Process entries for frontend
        processed_entries = []
        for entry in log_entries:
            start_time = entry['start_time']
            end_time = entry['end_time']
            
            # Handle datetime objects or strings
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Calculate hours from midnight
            start_hours = (start_time - day_start).total_seconds() / 3600
            end_hours = (end_time - day_start).total_seconds() / 3600
            
            # Clip to 24-hour window
            start_hours = max(0, min(24, start_hours))
            end_hours = max(0, min(24, end_hours))
            
            processed_entries.append({
                'status': entry['status'],
                'status_label': self.STATUS_LABELS[entry['status']],
                'status_y': self.STATUS_POSITIONS[entry['status']],
                'start_hours': round(start_hours, 2),
                'end_hours': round(end_hours, 2),
                'duration': entry['duration'],
                'notes': entry.get('notes', ''),
                'start_time_str': start_time.strftime('%H:%M'),
                'end_time_str': end_time.strftime('%H:%M'),
            })
        
        return {
            'day_number': day_log.get('day_number'),
            'date': day_log.get('date'),
            'entries': processed_entries,
            'summary': {
                'total_driving_hours': day_log.get('total_driving_hours', 0),
                'total_on_duty_hours': day_log.get('total_on_duty_hours', 0),
                'total_off_duty_hours': day_log.get('total_off_duty_hours', 0),
                'remaining_drive_time': day_log.get('remaining_drive_time', 0),
                'remaining_on_duty_time': day_log.get('remaining_on_duty_time', 0),
                'cycle_hours_remaining': day_log.get('cycle_hours_remaining', 0),
            }
        }
