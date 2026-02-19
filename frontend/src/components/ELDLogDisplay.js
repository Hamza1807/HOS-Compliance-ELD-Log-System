import React, { useRef, useEffect } from 'react';

const STATUS_COLORS = {
  'OFF': '#868e96',
  'SB': '#4dabf7',
  'D': '#667eea',
  'ON': '#ffd93d'
};

const STATUS_LABELS = {
  'OFF': 'Off Duty',
  'SB': 'Sleeper Berth',
  'D': 'Driving',
  'ON': 'On Duty (Not Driving)'
};

function ELDLogDisplay({ dayLog }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current && dayLog) {
      drawELDLog(canvasRef.current, dayLog);
    }
  }, [dayLog]);

  const drawELDLog = (canvas, dayLog) => {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Configuration
    const marginLeft = 120;
    const marginRight = 50;
    const marginTop = 80;
    const graphWidth = width - marginLeft - marginRight;
    const graphHeight = 400;
    const statusHeight = graphHeight / 4;

    // Draw header
    ctx.fillStyle = '#000';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('RECORD OF DUTY STATUS', width / 2, 30);

    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Date: ${dayLog.date}`, marginLeft, 55);
    ctx.textAlign = 'right';
    ctx.fillText(`Day ${dayLog.day_number}`, width - marginRight, 55);

    // Draw grid
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;

    // Vertical hour lines
    const hourWidth = graphWidth / 24;
    for (let i = 0; i <= 24; i++) {
      const x = marginLeft + (i * hourWidth);
      
      // Bold lines every 2 hours
      if (i % 2 === 0) {
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 2;
      } else {
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1;
      }
      
      ctx.beginPath();
      ctx.moveTo(x, marginTop);
      ctx.lineTo(x, marginTop + graphHeight);
      ctx.stroke();

      // Hour labels
      if (i < 24) {
        ctx.fillStyle = '#666';
        ctx.font = '11px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(i.toString().padStart(2, '0'), x + hourWidth / 2, marginTop - 10);
      }
    }

    // Horizontal status lines
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;
    const statusOrder = ['OFF', 'SB', 'D', 'ON'];
    
    for (let i = 0; i <= 4; i++) {
      const y = marginTop + (i * statusHeight);
      
      ctx.beginPath();
      ctx.moveTo(marginLeft, y);
      ctx.lineTo(marginLeft + graphWidth, y);
      ctx.stroke();

      // Status labels
      if (i < 4) {
        const status = statusOrder[i];
        const labelY = y + (statusHeight / 2) + 5;
        ctx.fillStyle = '#000';
        ctx.font = '12px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(STATUS_LABELS[status], marginLeft - 10, labelY);
      }
    }

    // Draw status lines
    if (dayLog.log_entries && dayLog.log_entries.length > 0) {
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      const statusPositions = { 'OFF': 0, 'SB': 1, 'D': 2, 'ON': 3 };
      
      dayLog.log_entries.forEach((entry, index) => {
        const startTime = new Date(entry.start_time);
        const endTime = new Date(entry.end_time);
        const dayStart = new Date(dayLog.date + 'T00:00:00');
        
        const startHours = (startTime - dayStart) / (1000 * 60 * 60);
        const endHours = (endTime - dayStart) / (1000 * 60 * 60);
        
        // Clip to 24-hour window
        const clippedStartHours = Math.max(0, Math.min(24, startHours));
        const clippedEndHours = Math.max(0, Math.min(24, endHours));
        
        const x1 = marginLeft + (clippedStartHours * hourWidth);
        const x2 = marginLeft + (clippedEndHours * hourWidth);
        
        const statusIndex = statusPositions[entry.status] || 0;
        const y = marginTop + (statusIndex * statusHeight) + (statusHeight / 2);
        
        ctx.strokeStyle = STATUS_COLORS[entry.status] || '#000';
        
        // Draw vertical connector if status changed
        if (index > 0) {
          const prevEntry = dayLog.log_entries[index - 1];
          const prevStatusIndex = statusPositions[prevEntry.status] || 0;
          const prevY = marginTop + (prevStatusIndex * statusHeight) + (statusHeight / 2);
          
          if (entry.status !== prevEntry.status) {
            ctx.beginPath();
            ctx.moveTo(x1, prevY);
            ctx.lineTo(x1, y);
            ctx.stroke();
          }
        }
        
        // Draw horizontal line
        ctx.beginPath();
        ctx.moveTo(x1, y);
        ctx.lineTo(x2, y);
        ctx.stroke();
      });
    }

    // Draw summary
    const summaryY = marginTop + graphHeight + 40;
    ctx.fillStyle = '#000';
    ctx.font = '13px Arial';
    ctx.textAlign = 'left';
    
    ctx.fillText(
      `Total Driving: ${dayLog.total_driving_hours?.toFixed(2) || 0} hrs`, 
      marginLeft, 
      summaryY
    );
    ctx.fillText(
      `Total On Duty: ${dayLog.total_on_duty_hours?.toFixed(2) || 0} hrs`, 
      marginLeft + 220, 
      summaryY
    );
    ctx.fillText(
      `Cycle Remaining: ${dayLog.cycle_hours_remaining?.toFixed(2) || 0} hrs`, 
      marginLeft + 440, 
      summaryY
    );
    
    ctx.font = '11px Arial';
    ctx.fillText(
      `Drive Time Remaining: ${dayLog.remaining_drive_time?.toFixed(2) || 0} hrs`, 
      marginLeft, 
      summaryY + 20
    );
    ctx.fillText(
      `On Duty Remaining: ${dayLog.remaining_on_duty_time?.toFixed(2) || 0} hrs`, 
      marginLeft + 250, 
      summaryY + 20
    );
  };

  return (
    <div style={{ 
      border: '2px solid rgba(102, 126, 234, 0.2)', 
      borderRadius: '16px', 
      padding: '1.5rem',
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
    }}>
      <h3 style={{ 
        marginBottom: '1.5rem', 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        fontWeight: '700',
        fontSize: '1.3rem'
      }}>
        📅 Day {dayLog.day_number} - {dayLog.date}
      </h3>
      <canvas 
        ref={canvasRef} 
        width={1200} 
        height={600}
        style={{ 
          width: '100%', 
          height: 'auto',
          border: '2px solid #e2e8f0',
          borderRadius: '12px',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)'
        }}
      />
    </div>
  );
}

export default ELDLogDisplay;
