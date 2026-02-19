# Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Mac/Linux users:
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Start backend server
python manage.py runserver
```

Backend is now running at `http://localhost:8000`

### Step 2: Frontend Setup (2 minutes)

Open a **NEW** terminal window:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend server
npm start
```

Frontend will open automatically at `http://localhost:3000`

### Step 3: Test the Application (1 minute)

1. Fill in the trip form:
   - **Current Location**: `New York, NY`
   - **Pickup Location**: `Chicago, IL`
   - **Dropoff Location**: `Los Angeles, CA`
   - **Current Cycle Used**: `0`

2. Click "Calculate Trip & Generate Logs"

3. View your results:
   - Route map
   - Daily breakdown
   - ELD compliance logs

## ✅ Verification

### Check Backend is Running
Visit: `http://localhost:8000/api/health/`

Should see: `{"status": "ok", "message": "HOS API is running"}`

### Check Frontend is Running
Visit: `http://localhost:3000`

Should see: The trip input form

## 🔧 Common Issues

### Backend won't start?
```bash
# Make sure you're in the backend directory
cd backend

# Check Python version (needs 3.8+)
python --version

# Try reinstalling dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start?
```bash
# Make sure you're in the frontend directory
cd frontend

# Check Node version (needs 16+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port already in use?
```bash
# Backend - use different port
python manage.py runserver 8001

# Frontend will need to update proxy in package.json
```

## 📝 Next Steps

1. **Explore the API**: Visit `http://localhost:8000/admin/` (create superuser first)
2. **Try different routes**: Enter various US cities
3. **Test edge cases**: Try a trip that requires 34-hour restart
4. **Review the code**: Check out the HOS engine logic

## 🎯 Example Trips to Try

### Short Trip (1 day)
- Current: `Dallas, TX`
- Pickup: `Houston, TX`
- Dropoff: `Austin, TX`
- Cycle: `10`

### Medium Trip (3-4 days)
- Current: `New York, NY`
- Pickup: `Chicago, IL`
- Dropoff: `Los Angeles, CA`
- Cycle: `0`

### Long Trip with Restart (5+ days)
- Current: `Miami, FL`
- Pickup: `Boston, MA`
- Dropoff: `Seattle, WA`
- Cycle: `50` (will trigger restart)

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Need help?** Check the troubleshooting section in the main README.
