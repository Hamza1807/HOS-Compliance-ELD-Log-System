# 🚛 HOS Compliance & ELD Log System

A comprehensive Full-Stack Django + React application for Hours of Service (HOS) compliance management and Electronic Logging Device (ELD) record generation following FMCSA regulations.

## 📋 Features

### Core Functionality
- ✅ **HOS Compliance Engine** - Ensures all trips comply with FMCSA regulations
- ✅ **Route Calculation** - Calculates optimal routes with multiple stops
- ✅ **Auto-Generated ELD Logs** - Creates FMCSA-compliant graph grids
- ✅ **Interactive Map** - Visual route display with waypoints
- ✅ **Daily Breakdown** - Detailed timeline for each day of travel
- ✅ **Cycle Management** - Tracks 70-hour/8-day rolling cycle

### HOS Regulations Implemented
- 11-hour daily driving limit
- 14-hour on-duty window
- 30-minute break after 8 cumulative driving hours
- 70-hour/8-day cycle management
- 10-hour off-duty reset requirement
- 34-hour restart logic when needed
- Automatic fuel stops every 1,000 miles
- 1-hour pickup and dropoff times

### ELD Logs
- FMCSA-compliant 24-hour graph grids
- Exact format matching FMCSA guide pages 15-18
- Four duty statuses: Off Duty, Sleeper Berth, Driving, On Duty (Not Driving)
- Multiple log sheets for multi-day trips
- Exportable formats (SVG, PDF ready)

## 🏗️ Architecture

### Backend (Django + DRF)
```
backend/
├── hos_project/          # Django project configuration
│   ├── settings.py       # Project settings
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI configuration
├── hos_app/             # Main application
│   ├── models.py        # Database models (Trip, DailyLog, LogEntry)
│   ├── views.py         # API endpoints
│   ├── serializers.py   # DRF serializers
│   ├── hos_engine.py    # Core HOS compliance logic
│   ├── route_service.py # Route calculation service
│   └── eld_generator.py # ELD log generation
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

### Frontend (React)
```
frontend/
├── public/              # Static files
├── src/
│   ├── pages/          # Main pages
│   │   ├── TripInputPage.js    # Trip input form
│   │   └── ResultsPage.js      # Results display
│   ├── components/     # Reusable components
│   │   ├── RouteMap.js         # Leaflet map component
│   │   ├── ELDLogDisplay.js    # ELD graph renderer
│   │   └── DailyLogAccordion.js # Daily breakdown
│   ├── App.js          # Main app component
│   ├── App.css         # Global styles
│   └── index.js        # Entry point
└── package.json        # Node dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```
   Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```
   Frontend will run on `http://localhost:3000`

## 📡 API Endpoints

### Calculate Trip
```http
POST /api/calculate-trip/
Content-Type: application/json

{
  "current_location": "New York, NY",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 15.5
}
```

**Response:**
```json
{
  "trip_id": 1,
  "route": {
    "total_miles": 2789.5,
    "total_duration_hours": 46.49,
    "coordinates": [[lng, lat], ...],
    "waypoints": [...]
  },
  "trip_plan": {
    "total_driving_hours": 46.49,
    "estimated_days": 5,
    "actual_days": 5,
    "daily_logs": [...],
    "cycle_used_before": 15.5,
    "cycle_used_after": 61.99,
    "restart_needed": false
  },
  "summary": {...}
}
```

### Get Trip
```http
GET /api/trips/{trip_id}/
```

### List Trips
```http
GET /api/trips/
```

### Download ELD Logs
```http
GET /api/trips/{trip_id}/download-logs/
```

### Health Check
```http
GET /api/health/
```

## 🧮 HOS Engine Logic

The HOS compliance engine (`hos_engine.py`) implements the core regulatory logic:

### Daily Limits
```python
MAX_DRIVING_HOURS = 11      # Daily driving limit
MAX_ON_DUTY_HOURS = 14      # On-duty window
REQUIRED_BREAK_AFTER_HOURS = 8   # Break after 8 hours
REQUIRED_BREAK_DURATION = 0.5    # 30-minute break
RESET_OFF_DUTY_HOURS = 10        # Daily reset
```

### Cycle Management
```python
MAX_CYCLE_HOURS = 70        # 70-hour/8-day cycle
RESTART_OFF_DUTY_HOURS = 34 # Restart duration
```

### Operational Constants
```python
AVG_SPEED_MPH = 60          # Average driving speed
FUEL_STOP_MILES = 1000      # Fuel every 1,000 miles
FUEL_STOP_DURATION = 0.5    # 30-minute fuel stop
PICKUP_DURATION = 1.0       # 1-hour pickup
DROPOFF_DURATION = 1.0      # 1-hour dropoff
```

## 🗺️ Route Service

The route service supports multiple providers:

### Primary: OpenRouteService (Free)
```python
route_service = RouteService(api_key="your_api_key")
route = route_service.calculate_route(locations)
```

### Fallback: Haversine Distance
If no API key is provided, the system uses haversine distance calculation with a road factor multiplier.

### Adding Your Own API Key
1. Sign up at [OpenRouteService](https://openrouteservice.org/)
2. Get your free API key
3. Add to `route_service.py`:
   ```python
   route_service = RouteService(api_key="your_api_key_here")
   ```

## 📊 ELD Log Generator

Generates FMCSA-compliant logs with:
- 24-hour grid (0-24 hours)
- 4 duty status levels (Off Duty, Sleeper Berth, Driving, On Duty)
- Vertical lines every hour (bold every 2 hours)
- Horizontal status lines
- Status change indicators
- Daily summary statistics

### Output Formats
- **JSON** - For frontend rendering
- **SVG** - Scalable vector graphics
- **Canvas** - HTML5 canvas rendering
- **PDF** - Ready for ReportLab integration

## 🎨 Frontend Components

### TripInputPage
Clean form with:
- Address inputs with validation
- Cycle hours slider (0-70)
- Real-time validation
- Loading states

### ResultsPage
Comprehensive results display:
- Trip summary cards
- Interactive route map
- Daily breakdown accordion
- ELD log visualizations
- Download functionality

### RouteMap
Leaflet-based map with:
- Route polylines
- Location markers
- Interactive popups

### ELDLogDisplay
Canvas-based ELD renderer:
- FMCSA-compliant grid
- Color-coded duty statuses
- Timeline visualization
- Summary statistics

## 🔧 Configuration

### Django Settings
Key settings in `settings.py`:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
TIME_ZONE = 'America/New_York'
```

### React Proxy
Configured in `frontend/package.json`:
```json
"proxy": "http://localhost:8000"
```

## 📦 Database Models

### Trip
- Current/Pickup/Dropoff locations
- Cycle hours used
- Total miles and days
- Route data (JSON)

### DailyLog
- Day number and date
- Log entries (JSON)
- Daily totals
- Remaining hours

### LogEntry
- Duty status
- Start/End times
- Duration
- Notes and location

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📱 Usage Example

1. **Enter Trip Information**
   - Current Location: "Dallas, TX"
   - Pickup Location: "Houston, TX"  
   - Dropoff Location: "Seattle, WA"
   - Current Cycle Used: 20 hours

2. **Calculate Trip**
   - System calculates ~2,300 mile route
   - Generates 3-4 day trip plan
   - Creates compliant daily schedules
   - Includes breaks and fuel stops

3. **View Results**
   - See interactive route map
   - Review daily breakdowns
   - Check ELD logs
   - Download for records

## 🚨 Important Notes

### Compliance Disclaimer
This system is designed to help with HOS compliance planning but should not replace:
- Professional legal advice
- Official FMCSA guidance
- Certified ELD devices
- Driver judgment and safety

### Production Considerations
Before deploying to production:
- [ ] Add user authentication
- [ ] Implement proper API keys management
- [ ] Add database backups
- [ ] Enable HTTPS
- [ ] Add logging and monitoring
- [ ] Implement rate limiting
- [ ] Add comprehensive error handling
- [ ] Enable PDF export
- [ ] Add email notifications
- [ ] Implement data retention policies

## 🔐 Security

### Current Setup (Development)
- SQLite database (not for production)
- No authentication required
- CORS enabled for localhost
- Debug mode enabled

### Production Recommendations
- Use PostgreSQL or MySQL
- Implement JWT authentication
- Configure proper CORS settings
- Disable DEBUG mode
- Use environment variables for secrets
- Enable HTTPS only
- Add request validation
- Implement rate limiting

## 🛠️ Troubleshooting

### Backend Issues

**Import Error: No module named 'rest_framework'**
```bash
pip install -r requirements.txt
```

**Database Error**
```bash
python manage.py migrate --run-syncdb
```

**Port Already in Use**
```bash
python manage.py runserver 8001
```

### Frontend Issues

**Module Not Found**
```bash
rm -rf node_modules package-lock.json
npm install
```

**API Connection Error**
- Check backend is running on port 8000
- Verify proxy setting in package.json
- Check CORS settings in Django

**Map Not Displaying**
```bash
npm install leaflet react-leaflet
```

## 📈 Future Enhancements

### Planned Features
- [ ] User authentication and profiles
- [ ] Historical trip analytics
- [ ] Real-time GPS tracking
- [ ] Mobile app (React Native)
- [ ] Weather integration
- [ ] Traffic data integration
- [ ] Multi-driver support
- [ ] Company fleet management
- [ ] Automated compliance reporting
- [ ] Integration with telematics systems

### API Integrations
- [ ] Google Maps API
- [ ] Mapbox API
- [ ] Weather API
- [ ] Traffic API
- [ ] Fuel price API

## 📝 License

This project is for educational purposes. Ensure compliance with FMCSA regulations in production use.

## 👥 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Review documentation
- Check troubleshooting section
- Submit GitHub issue

## 🙏 Acknowledgments

- FMCSA for HOS regulations guidance
- OpenRouteService for free routing API
- React-Leaflet for mapping components
- Django REST Framework team

---

**Built with ❤️ for the trucking industry**

For the latest updates and documentation, visit the project repository.
