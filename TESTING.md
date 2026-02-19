# 🧪 Testing & Examples

## Test Scenarios

### 1. Short Trip (Single Day)
**Scenario**: Local delivery within state
```json
{
  "current_location": "Dallas, TX",
  "pickup_location": "Fort Worth, TX",
  "dropoff_location": "Austin, TX",
  "current_cycle_used": 5
}
```
**Expected Results**:
- ~200 miles
- ~4 hours driving
- 1 day duration
- No restart needed
- Cycle after: ~11 hours

---

### 2. Medium Trip (Multi-Day)
**Scenario**: Cross-country delivery
```json
{
  "current_location": "New York, NY",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 0
}
```
**Expected Results**:
- ~2,800 miles
- ~47 hours driving
- 5 days duration
- 2-3 fuel stops
- Multiple 10-hour resets

---

### 3. Long Trip with Restart
**Scenario**: High cycle usage requiring restart
```json
{
  "current_location": "Miami, FL",
  "pickup_location": "Boston, MA",
  "dropoff_location": "Seattle, WA",
  "current_cycle_used": 55
}
```
**Expected Results**:
- ~3,500 miles
- ~58 hours driving
- 34-hour restart triggered
- 7-8 days total
- Cycle reset during trip

---

### 4. Edge Case: Maximum Cycle
**Scenario**: At cycle limit
```json
{
  "current_location": "Phoenix, AZ",
  "pickup_location": "Las Vegas, NV",
  "dropoff_location": "San Francisco, CA",
  "current_cycle_used": 68
}
```
**Expected Results**:
- Immediate restart required
- Trip delayed by 34 hours
- Fresh cycle after restart

---

### 5. Quick Turnaround
**Scenario**: Short distance, fresh cycle
```json
{
  "current_location": "Portland, OR",
  "pickup_location": "Seattle, WA",
  "dropoff_location": "Vancouver, BC",
  "current_cycle_used": 0
}
```
**Expected Results**:
- ~300 miles
- ~5 hours driving
- 1 day
- Plenty of cycle remaining

---

## API Testing with cURL

### Calculate Trip
```bash
curl -X POST http://localhost:8000/api/calculate-trip/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_location": "New York, NY",
    "pickup_location": "Chicago, IL",
    "dropoff_location": "Los Angeles, CA",
    "current_cycle_used": 15.5
  }'
```

### Get Trip by ID
```bash
curl http://localhost:8000/api/trips/1/
```

### List All Trips
```bash
curl http://localhost:8000/api/trips/
```

### Health Check
```bash
curl http://localhost:8000/api/health/
```

### Download Logs
```bash
curl http://localhost:8000/api/trips/1/download-logs/
```

---

## Testing with Postman

### Import Collection

Create a Postman collection with these requests:

#### 1. Calculate Trip
- **Method**: POST
- **URL**: `http://localhost:8000/api/calculate-trip/`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "current_location": "New York, NY",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 15.5
}
```

#### 2. Get Trip
- **Method**: GET
- **URL**: `http://localhost:8000/api/trips/{{trip_id}}/`

#### 3. List Trips
- **Method**: GET
- **URL**: `http://localhost:8000/api/trips/`

---

## Python Unit Tests

Create `backend/hos_app/tests.py`:

```python
from django.test import TestCase
from .hos_engine import HOSEngine

class HOSEngineTests(TestCase):
    
    def test_short_trip(self):
        """Test short trip calculation"""
        engine = HOSEngine(current_cycle_used=5)
        result = engine.calculate_trip(total_miles=200)
        
        self.assertEqual(result['estimated_days'], 1)
        self.assertLess(result['total_driving_hours'], 11)
        self.assertFalse(result['restart_needed'])
    
    def test_long_trip_with_restart(self):
        """Test long trip requiring restart"""
        engine = HOSEngine(current_cycle_used=60)
        result = engine.calculate_trip(total_miles=1500)
        
        self.assertTrue(result['restart_needed'])
        self.assertGreater(result['actual_days'], result['estimated_days'])
    
    def test_fuel_stops(self):
        """Test fuel stop calculation"""
        engine = HOSEngine(current_cycle_used=0)
        result = engine.calculate_trip(total_miles=2500)
        
        self.assertEqual(result['num_fuel_stops'], 2)
    
    def test_daily_driving_limit(self):
        """Test 11-hour daily driving limit"""
        engine = HOSEngine(current_cycle_used=0)
        result = engine.calculate_trip(total_miles=700)  # ~12 hours at 60mph
        
        for day in result['daily_logs']:
            if not day.get('is_restart'):
                self.assertLessEqual(day['total_driving_hours'], 11.1)
    
    def test_break_after_8_hours(self):
        """Test 30-minute break requirement"""
        engine = HOSEngine(current_cycle_used=0)
        result = engine.calculate_trip(total_miles=600)  # 10 hours driving
        
        # Check for break entries
        day1 = result['daily_logs'][0]
        break_entries = [e for e in day1['log_entries'] if 'break' in e['notes'].lower()]
        self.assertGreater(len(break_entries), 0)
```

Run tests:
```bash
cd backend
python manage.py test hos_app
```

---

## React Component Tests

Create `frontend/src/components/ELDLogDisplay.test.js`:

```javascript
import { render, screen } from '@testing-library/react';
import ELDLogDisplay from './ELDLogDisplay';

const mockDayLog = {
  day_number: 1,
  date: '2026-02-19',
  log_entries: [
    {
      status: 'D',
      start_time: '2026-02-19T08:00:00',
      end_time: '2026-02-19T11:00:00',
      duration: 3,
      notes: 'Driving'
    }
  ],
  total_driving_hours: 3,
  total_on_duty_hours: 4,
  remaining_drive_time: 8,
  cycle_hours_remaining: 66
};

test('renders day number and date', () => {
  render(<ELDLogDisplay dayLog={mockDayLog} />);
  expect(screen.getByText(/Day 1/i)).toBeInTheDocument();
});

test('renders canvas element', () => {
  const { container } = render(<ELDLogDisplay dayLog={mockDayLog} />);
  const canvas = container.querySelector('canvas');
  expect(canvas).toBeInTheDocument();
});
```

Run tests:
```bash
cd frontend
npm test
```

---

## Manual Testing Checklist

### Frontend Testing
- [ ] Trip input form validation
- [ ] Form submission with valid data
- [ ] Loading state during calculation
- [ ] Error handling for invalid input
- [ ] Navigation between pages
- [ ] Route map displays correctly
- [ ] Accordion expand/collapse
- [ ] ELD logs render properly
- [ ] Responsive design on mobile
- [ ] Browser compatibility

### Backend Testing
- [ ] API endpoints respond correctly
- [ ] Data validation works
- [ ] Database saves trips
- [ ] HOS calculations are accurate
- [ ] Route service handles errors
- [ ] ELD generator creates valid logs
- [ ] CORS headers configured
- [ ] Error responses are informative

### HOS Compliance Testing
- [ ] 11-hour driving limit enforced
- [ ] 14-hour window enforced
- [ ] 30-minute break after 8 hours
- [ ] 10-hour reset calculated
- [ ] 34-hour restart triggered when needed
- [ ] Cycle tracking accurate
- [ ] Fuel stops every 1000 miles
- [ ] Pickup/dropoff times included

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/api/health/

# Test trip calculation (with POST data)
ab -n 100 -c 5 -p trip_data.json -T application/json \
   http://localhost:8000/api/calculate-trip/
```

Create `trip_data.json`:
```json
{
  "current_location": "New York, NY",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 15
}
```

### Expected Performance
- Health check: < 10ms
- Trip calculation: < 2 seconds
- List trips: < 100ms
- Get trip: < 50ms

---

## Integration Testing

### Full Stack Flow Test

```python
# backend/hos_app/test_integration.py
from django.test import TestCase, Client
import json

class IntegrationTests(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_flow(self):
        """Test complete trip calculation flow"""
        
        # 1. Submit trip
        response = self.client.post(
            '/api/calculate-trip/',
            data=json.dumps({
                'current_location': 'New York, NY',
                'pickup_location': 'Chicago, IL',
                'dropoff_location': 'Los Angeles, CA',
                'current_cycle_used': 0
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        trip_id = data['trip_id']
        
        # 2. Verify trip was saved
        response = self.client.get(f'/api/trips/{trip_id}/')
        self.assertEqual(response.status_code, 200)
        
        # 3. Download logs
        response = self.client.get(f'/api/trips/{trip_id}/download-logs/')
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify in list
        response = self.client.get('/api/trips/')
        self.assertEqual(response.status_code, 200)
        trips = response.json()
        self.assertGreater(len(trips), 0)
```

---

## Debugging Tips

### Backend Debugging

1. **Enable verbose logging**
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

2. **Use Django shell**
```bash
python manage.py shell
```
```python
from hos_app.hos_engine import HOSEngine
engine = HOSEngine(current_cycle_used=0)
result = engine.calculate_trip(total_miles=500)
print(result)
```

3. **Check database**
```bash
python manage.py dbshell
```
```sql
SELECT * FROM hos_app_trip;
SELECT * FROM hos_app_dailylog;
```

### Frontend Debugging

1. **React DevTools**
   - Install React Developer Tools extension
   - Inspect component state and props

2. **Console logging**
```javascript
console.log('Trip data:', tripData);
console.log('API response:', response.data);
```

3. **Network tab**
   - Check API request/response
   - Verify CORS headers
   - Check status codes

---

## Common Issues & Solutions

### Issue: Route calculation returns 0 miles
**Solution**: 
- Check API key configuration
- Verify location names are valid
- Check internet connection for API calls

### Issue: ELD logs not rendering
**Solution**:
- Check browser console for errors
- Verify canvas element is mounted
- Check dayLog data structure

### Issue: CORS errors
**Solution**:
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Issue: 34-hour restart not triggering
**Solution**:
- Check initial cycle_used value
- Verify trip distance requires restart
- Check HOSEngine logic

---

## Test Data Generator

Create `backend/generate_test_data.py`:

```python
import requests
import random

locations = [
    ("New York, NY", "Chicago, IL", "Los Angeles, CA"),
    ("Miami, FL", "Atlanta, GA", "Dallas, TX"),
    ("Seattle, WA", "Portland, OR", "San Francisco, CA"),
    ("Houston, TX", "Denver, CO", "Phoenix, AZ"),
    ("Boston, MA", "Philadelphia, PA", "Washington, DC"),
]

for current, pickup, dropoff in locations:
    data = {
        "current_location": current,
        "pickup_location": pickup,
        "dropoff_location": dropoff,
        "current_cycle_used": random.uniform(0, 50)
    }
    
    response = requests.post(
        'http://localhost:8000/api/calculate-trip/',
        json=data
    )
    
    if response.status_code == 200:
        print(f"✓ Created trip: {current} → {pickup} → {dropoff}")
    else:
        print(f"✗ Failed: {response.status_code}")
```

Run:
```bash
python generate_test_data.py
```

---

**For more information, see [README.md](README.md)**
