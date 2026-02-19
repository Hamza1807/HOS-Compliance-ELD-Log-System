import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RouteMap from '../components/RouteMap';
import ELDLogDisplay from '../components/ELDLogDisplay';
import DailyLogAccordion from '../components/DailyLogAccordion';

function ResultsPage({ tripData }) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!tripData) {
      navigate('/');
    }
  }, [tripData, navigate]);

  if (!tripData) {
    return null;
  }

  const { route, trip_plan, summary } = tripData;

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem', animation: 'fadeIn 0.5s ease-out' }}>
        <button 
          className="btn btn-secondary" 
          onClick={() => navigate('/')}
        >
          ← New Trip
        </button>
      </div>

      {/* Trip Summary */}
      <div className="card" style={{ animation: 'cardSlideUp 0.6s ease-out' }}>
        <h2>📊 Trip Summary</h2>
        <div className="summary-grid">
          <div className="summary-item">
            <h3>🛣️ Total Distance</h3>
            <p>{summary.total_miles} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>mi</span></p>
          </div>
          <div className="summary-item">
            <h3>🚛 Driving Time</h3>
            <p>{summary.total_driving_hours} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>hrs</span></p>
          </div>
          <div className="summary-item">
            <h3>📅 Trip Duration</h3>
            <p>{summary.total_days} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>days</span></p>
          </div>
          <div className="summary-item">
            <h3>⏰ Cycle Before</h3>
            <p>{summary.cycle_before} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>hrs</span></p>
          </div>
          <div className="summary-item">
            <h3>⏱️ Cycle After</h3>
            <p>{summary.cycle_after} <span style={{ fontSize: '1rem', fontWeight: 'normal' }}>hrs</span></p>
          </div>
          <div className="summary-item">
            <h3>🔄 34-hr Restart</h3>
            <p>{summary.restart_needed ? '✓ Yes' : '✗ No'}</p>
          </div>
        </div>
        
        {summary.restart_needed && (
          <div className="success">
            <div>
              <strong>Notice:</strong> A 34-hour restart is required during this trip to reset your 70-hour cycle.
            </div>
          </div>
        )}
      </div>

      {/* Route Map */}
      <div className="card" style={{ animation: 'cardSlideUp 0.7s ease-out' }}>
        <h2>🗺️ Route Map</h2>
        <RouteMap route={route} />
      </div>

      {/* Daily Breakdown */}
      <div className="card" style={{ animation: 'cardSlideUp 0.8s ease-out' }}>
        <h2>📅 Daily Breakdown</h2>
        <p style={{ marginBottom: '2rem', color: '#718096', fontSize: '1.05rem' }}>
          Click on any day to view detailed timeline and ELD log
        </p>
        
        {trip_plan.daily_logs.map((dayLog, index) => (
          <DailyLogAccordion
            key={index}
            dayLog={dayLog}
          />
        ))}
      </div>

      {/* ELD Logs */}
      <div className="card" style={{ animation: 'cardSlideUp 0.9s ease-out' }}>
        <h2>📋 ELD Logs (FMCSA Compliant)</h2>
        <p style={{ marginBottom: '2rem', color: '#718096', fontSize: '1.05rem' }}>
          Electronic Logging Device records following FMCSA graph grid format
        </p>
        
        {trip_plan.daily_logs.map((dayLog, index) => (
          <div key={index} style={{ marginBottom: '3rem' }}>
            <ELDLogDisplay dayLog={dayLog} />
          </div>
        ))}
      </div>

      {/* Download Section */}
      <div className="card" style={{ animation: 'cardSlideUp 1s ease-out' }}>
        <h2>💾 Download Logs</h2>
        <p style={{ marginBottom: '1.5rem', color: '#718096', fontSize: '1.05rem' }}>
          Download your complete ELD logs for compliance records
        </p>
        <button 
          className="btn btn-success btn-lg"
          onClick={() => {
            alert('Download functionality: In production, this would download a PDF or ZIP file with all ELD logs.');
          }}
        >
          📥 Download All Logs
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;
