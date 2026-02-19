"""
Route Calculation Service

Uses OpenRouteService API (free tier) to calculate routes.
Can be easily swapped for Google Maps, Mapbox, etc.
"""

import requests
from typing import List, Dict, Tuple
import math


class RouteService:
    """Service for calculating routes between locations"""
    
    # OpenRouteService API (Free - get key from https://openrouteservice.org/)
    BASE_URL = "https://api.openrouteservice.org/v2"
    
    def __init__(self, api_key: str = None):
        """
        Initialize route service
        
        Args:
            api_key: OpenRouteService API key (optional for demo)
        """
        self.api_key = api_key
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        } if api_key else {}
    
    def calculate_route(
        self, 
        locations: List[str], 
        use_geocoding: bool = True
    ) -> Dict:
        """
        Calculate route between multiple locations
        
        Args:
            locations: List of location strings (addresses or lat/lng)
            use_geocoding: Whether to geocode address strings
            
        Returns:
            Dictionary with route information
        """
        if use_geocoding:
            # Geocode all locations first
            coordinates = []
            for location in locations:
                coords = self.geocode_address(location)
                if coords:
                    coordinates.append(coords)
                else:
                    # Fallback: use approximate coordinates
                    coordinates.append(self._get_approximate_coords(location))
        else:
            coordinates = locations
        
        if len(coordinates) < 2:
            raise ValueError("At least 2 locations required")
        
        # Calculate route using coordinates
        try:
            if self.api_key:
                route_data = self._calculate_route_with_api(coordinates)
            else:
                # Fallback: calculate straight-line distance
                route_data = self._calculate_route_fallback(coordinates, locations)
        except Exception as e:
            # Fallback on error
            route_data = self._calculate_route_fallback(coordinates, locations)
        
        return route_data
    
    def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Geocode an address to coordinates
        
        Args:
            address: Address string
            
        Returns:
            Tuple of (longitude, latitude)
        """
        if not self.api_key:
            return self._get_approximate_coords(address)
        
        try:
            url = f"{self.BASE_URL}/geocode/search"
            params = {
                'text': address,
                'size': 1
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    coords = data['features'][0]['geometry']['coordinates']
                    return tuple(coords)  # [lng, lat]
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return self._get_approximate_coords(address)
    
    def _calculate_route_with_api(self, coordinates: List[Tuple]) -> Dict:
        """Calculate route using OpenRouteService API"""
        url = f"{self.BASE_URL}/directions/driving-car"
        
        payload = {
            'coordinates': coordinates,
            'units': 'mi'
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        route = data['routes'][0]
        
        distance_miles = route['summary']['distance']  # Already in miles
        duration_hours = route['summary']['duration'] / 3600  # Convert seconds to hours
        
        return {
            'total_miles': round(distance_miles, 1),
            'total_duration_hours': round(duration_hours, 2),
            'coordinates': coordinates,
            'geometry': route['geometry'],
            'segments': self._extract_segments(route),
            'waypoints': [{'location': coord} for coord in coordinates]
        }
    
    def _calculate_route_fallback(
        self, 
        coordinates: List[Tuple], 
        locations: List[str]
    ) -> Dict:
        """
        Fallback route calculation using straight-line distance
        Uses a factor of 1.2 to account for road curvature
        """
        total_miles = 0
        segments = []
        
        for i in range(len(coordinates) - 1):
            start = coordinates[i]
            end = coordinates[i + 1]
            
            distance = self._haversine_distance(start, end)
            # Apply road factor (roads are typically 20% longer than straight line)
            distance_miles = distance * 0.621371 * 1.2  # km to miles with road factor
            
            total_miles += distance_miles
            segments.append({
                'start': start,
                'end': end,
                'distance_miles': round(distance_miles, 1)
            })
        
        # Estimate duration at 60 mph average
        duration_hours = total_miles / 60
        
        return {
            'total_miles': round(total_miles, 1),
            'total_duration_hours': round(duration_hours, 2),
            'coordinates': coordinates,
            'segments': segments,
            'waypoints': [
                {'location': coord, 'address': locations[i] if i < len(locations) else None} 
                for i, coord in enumerate(coordinates)
            ],
            'method': 'fallback'
        }
    
    def _extract_segments(self, route: Dict) -> List[Dict]:
        """Extract route segments from API response"""
        segments = []
        if 'segments' in route:
            for segment in route['segments']:
                segments.append({
                    'distance_miles': segment['distance'],
                    'duration_hours': segment['duration'] / 3600
                })
        return segments
    
    def _haversine_distance(
        self, 
        coord1: Tuple[float, float], 
        coord2: Tuple[float, float]
    ) -> float:
        """
        Calculate haversine distance between two coordinates
        
        Returns:
            Distance in kilometers
        """
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        
        # Convert to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in km
        r = 6371
        
        return c * r
    
    def _get_approximate_coords(self, location: str) -> Tuple[float, float]:
        """
        Get approximate coordinates for common US cities
        This is a fallback when geocoding is not available
        """
        # Common locations (longitude, latitude)
        locations_db = {
            'new york': (-74.0060, 40.7128),
            'los angeles': (-118.2437, 34.0522),
            'chicago': (-87.6298, 41.8781),
            'houston': (-95.3698, 29.7604),
            'phoenix': (-112.0740, 33.4484),
            'philadelphia': (-75.1652, 39.9526),
            'san antonio': (-98.4936, 29.4241),
            'san diego': (-117.1611, 32.7157),
            'dallas': (-96.7970, 32.7767),
            'san jose': (-121.8863, 37.3382),
            'austin': (-97.7431, 30.2672),
            'jacksonville': (-81.6557, 30.3322),
            'miami': (-80.1918, 25.7617),
            'atlanta': (-84.3880, 33.7490),
            'boston': (-71.0589, 42.3601),
            'seattle': (-122.3321, 47.6062),
            'denver': (-104.9903, 39.7392),
            'las vegas': (-115.1398, 36.1699),
            'portland': (-122.6765, 45.5231),
            'detroit': (-83.0458, 42.3314),
        }
        
        location_lower = location.lower()
        
        # Check for known cities
        for city, coords in locations_db.items():
            if city in location_lower:
                return coords
        
        # Default to center of US
        return (-98.5795, 39.8283)
