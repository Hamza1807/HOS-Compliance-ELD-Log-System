import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function RouteMap({ route }) {
  if (!route || !route.coordinates || route.coordinates.length === 0) {
    return (
      <div className="map-container" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#f0f0f0'
      }}>
        <p>Map data not available</p>
      </div>
    );
  }

  // Convert coordinates from [lng, lat] to [lat, lng] for Leaflet
  const leafletCoords = route.coordinates.map(coord => [coord[1], coord[0]]);
  
  // Calculate center
  const center = leafletCoords.length > 0 
    ? leafletCoords[Math.floor(leafletCoords.length / 2)]
    : [39.8283, -98.5795]; // Center of US

  return (
    <div className="map-container">
      <MapContainer 
        center={center} 
        zoom={5} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Route polyline */}
        {leafletCoords.length > 1 && (
          <Polyline 
            positions={leafletCoords} 
            color="#2a5298"
            weight={4}
            opacity={0.7}
          />
        )}
        
        {/* Markers for waypoints */}
        {leafletCoords.map((coord, index) => (
          <Marker key={index} position={coord}>
            <Popup>
              {index === 0 && 'Start Location'}
              {index === 1 && 'Pickup Location'}
              {index === leafletCoords.length - 1 && index > 1 && 'Dropoff Location'}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default RouteMap;
