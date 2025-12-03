import React, { useState, useEffect } from 'react';
import QRCode from 'react-qr-code';
import './App.css';

function App() {
  const [qrUrl, setQrUrl] = useState('');
  const [status, setStatus] = useState('IDLE');
  const [countdown, setCountdown] = useState(0);
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    // Poll state.json every second
    const interval = setInterval(() => {
      fetch('/state.json?t=' + Date.now())
        .then(res => res.json())
        .then(data => {
          if (data.qr_url) {
            setQrUrl(data.qr_url);
            setStatus('QR');
            setMessage('Scan QR Code');
          } else if (data.status === 'CONNECTED') {
            setStatus('CONNECTED');
            setMessage('Connected!');
          } else if (data.status === 'RUNNING' && data.duration_seconds) {
            setStatus('RUNNING');
            setCountdown(data.duration_seconds);
          }
        })
        .catch(err => console.log('Error fetching state:', err));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Countdown timer
  useEffect(() => {
    if (status === 'RUNNING' && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(prev => {
          const next = prev - 1;
          if (next <= 0) {
            setStatus('QR'); // Go back to QR when done
          }
          return next;
        });
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [status, countdown]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="App">
      <div className="background">
        <div className="shape shape1"></div>
        <div className="shape shape2"></div>
      </div>

      <div className="container">
        <h1 className="heading">{message}</h1>

        {status === 'QR' && qrUrl && (
          <div className="qr-container">
            <QRCode value={qrUrl} size={256} />
          </div>
        )}

        {status === 'CONNECTED' && (
          <div className="status-text">
            <p>Please wait...</p>
          </div>
        )}

        {status === 'RUNNING' && (
          <div className="timer-container">
            <div className="countdown">{formatTime(countdown)}</div>
            <p className="status-text">Service Active</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
