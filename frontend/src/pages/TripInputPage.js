import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function TripInputPage({ onTripCalculated }) {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_used: 0
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'current_cycle_used' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/calculate-trip/', formData);
      onTripCalculated(response.data);
      navigate('/results');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate trip. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ animation: 'cardSlideUp 0.6s ease-out' }}>
        <h2>📍 Trip Information</h2>
        
        {error && (
          <div className="error">
            <div>
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="current_location">
              📍 Current Location
            </label>
            <input
              type="text"
              id="current_location"
              name="current_location"
              value={formData.current_location}
              onChange={handleChange}
              placeholder="e.g., New York, NY"
              required
            />
            <small>Your current starting position</small>
          </div>

          <div className="form-group">
            <label htmlFor="pickup_location">
              📦 Pickup Location
            </label>
            <input
              type="text"
              id="pickup_location"
              name="pickup_location"
              value={formData.pickup_location}
              onChange={handleChange}
              placeholder="e.g., Chicago, IL"
              required
            />
            <small>Where you will pick up the load</small>
          </div>

          <div className="form-group">
            <label htmlFor="dropoff_location">
              🎯 Dropoff Location
            </label>
            <input
              type="text"
              id="dropoff_location"
              name="dropoff_location"
              value={formData.dropoff_location}
              onChange={handleChange}
              placeholder="e.g., Los Angeles, CA"
              required
            />
            <small>Final destination for delivery</small>
          </div>

          <div className="form-group">
            <label htmlFor="current_cycle_used">
              ⏱️ Current Cycle Used (Hours)
            </label>
            <input
              type="number"
              id="current_cycle_used"
              name="current_cycle_used"
              value={formData.current_cycle_used}
              onChange={handleChange}
              min="0"
              max="70"
              step="0.5"
              required
            />
            <small>Hours already used out of 70 in the rolling 8-day cycle (0-70)</small>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-lg"
            disabled={loading}
            style={{ width: '100%', marginTop: '1rem' }}
          >
            {loading ? '⏳ Calculating...' : '🚀 Calculate Trip & Generate Logs'}
          </button>
        </form>
      </div>

      <div className="card" style={{ animation: 'cardSlideUp 0.8s ease-out' }}>
        <h2>ℹ️ About This System</h2>
        <p style={{ lineHeight: '1.8', color: '#4a5568', marginBottom: '1.5rem' }}>
          This system calculates HOS-compliant trip plans following FMCSA regulations:
        </p>
        <ul className="info-list" style={{ lineHeight: '2', color: '#4a5568' }}>
          <li>✅ 11-hour daily driving limit</li>
          <li>✅ 14-hour on-duty window</li>
          <li>✅ 30-minute break after 8 cumulative driving hours</li>
          <li>✅ 70-hour/8-day cycle management</li>
          <li>✅ 10-hour off-duty reset</li>
          <li>✅ 34-hour restart when needed</li>
          <li>✅ Automatic fuel stops every 1,000 miles</li>
          <li>✅ 1-hour pickup and dropoff time</li>
        </ul>
      </div>
    </div>
  );
}

export default TripInputPage;
