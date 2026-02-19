import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TripInputPage from './pages/TripInputPage';
import ResultsPage from './pages/ResultsPage';
import './App.css';

function App() {
  const [tripData, setTripData] = useState(null);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <header className="app-header">
          <h1>🚛 HOS Compliance & ELD Log System</h1>
          <p>Hours of Service Management for Property Carrying Vehicles</p>
        </header>
        
        <Routes>
          <Route 
            path="/" 
            element={<TripInputPage onTripCalculated={setTripData} />} 
          />
          <Route 
            path="/results" 
            element={<ResultsPage tripData={tripData} />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
