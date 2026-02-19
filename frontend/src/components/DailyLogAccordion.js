import React, { useState } from 'react';

const STATUS_LABELS = {
  'OFF': 'Off Duty',
  'SB': 'Sleeper Berth',
  'D': 'Driving',
  'ON': 'On Duty (Not Driving)'
};

const STATUS_ICONS = {
  'OFF': '😴',
  'SB': '🛏️',
  'D': '🚛',
  'ON': '📋'
};

function DailyLogAccordion({ dayLog, onSelect }) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleAccordion = () => {
    setIsOpen(!isOpen);
    if (!isOpen && onSelect) {
      onSelect();
    }
  };

  const formatTime = (timeStr) => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return timeStr;
    }
  };

  const isRestart = dayLog.is_restart || false;

  return (
    <div className="accordion">
      <div className="accordion-header" onClick={toggleAccordion}>
        <h3>
          {isRestart ? '🔄' : '📅'} Day {dayLog.day_number} - {dayLog.date}
          {isRestart && ' (34-Hour Restart)'}
        </h3>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem', color: '#666' }}>
            Drive: {dayLog.total_driving_hours?.toFixed(1)}h | 
            On Duty: {dayLog.total_on_duty_hours?.toFixed(1)}h | 
            Cycle: {dayLog.cycle_hours_remaining?.toFixed(1)}h remaining
          </span>
          <span style={{ fontSize: '1.2rem' }}>
            {isOpen ? '▼' : '▶'}
          </span>
        </div>
      </div>
      
      {isOpen && (
        <div className="accordion-content">
          {isRestart ? (
            <div style={{ padding: '1rem', background: '#fff3cd', borderRadius: '4px' }}>
              <h4 style={{ marginBottom: '0.5rem', color: '#856404' }}>
                🔄 34-Hour Restart Period
              </h4>
              <p style={{ color: '#856404' }}>
                This is a mandatory 34-hour off-duty period to reset your 70-hour cycle.
                You must remain off-duty for the entire duration.
              </p>
            </div>
          ) : (
            <>
              {/* Timeline */}
              <div className="timeline">
                {dayLog.log_entries?.map((entry, index) => (
                  <div 
                    key={index} 
                    className={`timeline-item status-${entry.status}`}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ 
                          display: 'inline-block',
                          padding: '0.5rem 1rem',
                          background: getStatusColor(entry.status),
                          color: 'white',
                          borderRadius: '8px',
                          fontSize: '0.9rem',
                          fontWeight: '700',
                          marginBottom: '0.75rem',
                          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                        }}>
                          {STATUS_ICONS[entry.status]} {STATUS_LABELS[entry.status]}
                        </div>
                        <div style={{ fontSize: '0.95rem', color: '#4a5568', marginTop: '0.5rem' }}>
                          <strong>Time:</strong> {formatTime(entry.start_time_str || entry.start_time)} - {formatTime(entry.end_time_str || entry.end_time)}
                        </div>
                        <div style={{ fontSize: '0.95rem', color: '#4a5568' }}>
                          <strong>Duration:</strong> {entry.duration?.toFixed(2)} hours
                        </div>
                        {entry.notes && (
                          <div style={{ 
                            fontSize: '0.9rem', 
                            color: '#718096', 
                            marginTop: '0.5rem', 
                            fontStyle: 'italic',
                            padding: '0.5rem',
                            background: 'rgba(102, 126, 234, 0.05)',
                            borderRadius: '6px',
                            borderLeft: '3px solid #667eea'
                          }}>
                            💬 {entry.notes}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Summary Stats */}
              <div style={{ 
                marginTop: '2rem', 
                padding: '1.5rem', 
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)', 
                borderRadius: '12px',
                border: '1px solid rgba(102, 126, 234, 0.1)',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.5rem'
              }}>
                <div>
                  <div style={{ fontSize: '0.9rem', color: '#718096', marginBottom: '0.5rem', fontWeight: '600' }}>
                    🚛 Total Driving
                  </div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '800',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>
                    {dayLog.total_driving_hours?.toFixed(2)} hrs
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', color: '#718096', marginBottom: '0.5rem', fontWeight: '600' }}>
                    📋 Total On Duty
                  </div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '800',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>
                    {dayLog.total_on_duty_hours?.toFixed(2)} hrs
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', color: '#718096', marginBottom: '0.5rem', fontWeight: '600' }}>
                    ⏰ Drive Remaining
                  </div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '800',
                    background: 'linear-gradient(135deg, #51cf66 0%, #37b24d 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>
                    {dayLog.remaining_drive_time?.toFixed(2)} hrs
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', color: '#718096', marginBottom: '0.5rem', fontWeight: '600' }}>
                    🔄 Cycle Remaining
                  </div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '800',
                    background: 'linear-gradient(135deg, #51cf66 0%, #37b24d 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>
                    {dayLog.cycle_hours_remaining?.toFixed(2)} hrs
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function getStatusColor(status) {
  const colors = {
    'OFF': 'linear-gradient(135deg, #868e96, #495057)',
    'SB': 'linear-gradient(135deg, #4dabf7, #228be6)',
    'D': 'linear-gradient(135deg, #667eea, #764ba2)',
    'ON': 'linear-gradient(135deg, #ffd93d, #f77f00)'
  };
  return colors[status] || '#6c757d';
}

export default DailyLogAccordion;
