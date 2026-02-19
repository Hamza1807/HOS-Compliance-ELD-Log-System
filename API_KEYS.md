# HOS Compliance API Key Configuration

## OpenRouteService API Key (Recommended)

For accurate route calculations, sign up for a free API key:

1. Visit: https://openrouteservice.org/
2. Sign up for free account
3. Generate API key
4. Add to your environment

### Django Backend Configuration

#### Option 1: Environment Variable (Recommended)
```bash
# Add to your environment or .env file
export OPENROUTESERVICE_API_KEY="your_api_key_here"
```

Then update `hos_app/views.py`:
```python
import os
route_service = RouteService(api_key=os.environ.get('OPENROUTESERVICE_API_KEY'))
```

#### Option 2: Direct Configuration
Update `hos_app/views.py`:
```python
route_service = RouteService(api_key="your_api_key_here")
```

### Fallback Mode

Without an API key, the system uses:
- Haversine distance calculation
- 1.2x road factor for realistic estimates
- Built-in city coordinates database

This works for demos but may be less accurate.

## Alternative APIs

### Google Maps API
```python
# In route_service.py, you can modify to use Google Maps
# Documentation: https://developers.google.com/maps/documentation
```

### Mapbox API
```python
# Mapbox Directions API
# Documentation: https://docs.mapbox.com/api/navigation/
```

## Rate Limits

### OpenRouteService Free Tier
- 2,000 requests per day
- 40 requests per minute

### Production Recommendations
- Use paid tier for production
- Implement caching
- Add rate limiting on your API
- Consider multiple provider fallback
