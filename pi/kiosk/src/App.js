import React, { useEffect, useState } from 'react'
import QRCode from 'react-qr-code'
import './App.css'

const POLL_INTERVAL_MS = 1000

const defaultMessages = {
  LOADING: 'Loading status...',
  QR: 'Scan QR Code',
  SCANNED: 'Scan detected, connecting...',
  CONNECTED: 'Connected! Waiting for BLE to start service...',
  RUNNING: 'Service Active',
  IDLE: 'Waiting for BLE update...',
  ERROR: 'Unable to load kiosk state'
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const computeRemainingSeconds = (data) => {
  if (!data || !data.duration_seconds) return null
  const startedAt = data.started_at ? new Date(data.started_at).getTime() : Date.now()
  const elapsed = Math.max(Math.floor((Date.now() - startedAt) / 1000), 0)
  return Math.max(data.duration_seconds - elapsed, 0)
}

function App() {
  const [uiState, setUiState] = useState({
    status: 'LOADING',
    qrUrl: '',
    message: defaultMessages.LOADING,
    remaining: null,
    error: ''
  })

  useEffect(() => {
    let isMounted = true

    const pollState = async () => {
      try {
        const res = await fetch('/state.json?t=' + Date.now())
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }

        const data = await res.json()
        const normalizedStatus = (data.status || (data.qr_url ? 'QR' : 'IDLE')).toUpperCase()
        const remainingSeconds = computeRemainingSeconds(data)
        const message = data.message || defaultMessages[normalizedStatus] || defaultMessages.IDLE

        if (!isMounted) return

        setUiState({
          status: normalizedStatus,
          qrUrl: data.qr_url || '',
          message,
          remaining: remainingSeconds,
          error: ''
        })
      } catch (err) {
        if (!isMounted) return
        setUiState((prev) => ({
          ...prev,
          status: 'ERROR',
          message: defaultMessages.ERROR,
          error: err?.message || 'Failed to fetch state.json',
          remaining: null
        }))
      }
    }

    pollState()
    const intervalId = setInterval(pollState, POLL_INTERVAL_MS)

    return () => {
      isMounted = false
      clearInterval(intervalId)
    }
  }, [])

  const { status, qrUrl, message, remaining, error } = uiState

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

        {(status === 'SCANNED' || status === 'CONNECTED') && (
          <div className="status-text">
            <p>BLE reported a scan. Waiting for service...</p>
          </div>
        )}

        {status === 'RUNNING' && (
          <div className="timer-container">
            {typeof remaining === 'number' ? (
              <div className="countdown">{formatTime(remaining)}</div>
            ) : (
              <p className="status-text">Service Active</p>
            )}
            <p className="status-text">BLE will update the state when finished.</p>
          </div>
        )}

        {status === 'ERROR' && (
          <div className="status-text error">
            <p>{error}</p>
            <p>Waiting for next BLE update...</p>
          </div>
        )}

        {status === 'IDLE' && (
          <div className="status-text">
            <p>Waiting for BLE update...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
