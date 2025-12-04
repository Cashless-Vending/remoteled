import { useState, useEffect, useCallback } from 'react'
import { statsApi, LiveOrdersResponse, RealtimeStats } from '../../api/stats'
import { Order } from '../../types'

interface LiveOrdersPanelProps {
  refreshInterval?: number // milliseconds
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'CREATED': return '#805AD5' // purple
    case 'PAID': return '#3182CE' // blue
    case 'RUNNING': return '#38A169' // green
    case 'DONE': return '#48BB78' // light green
    case 'FAILED': return '#E53E3E' // red
    default: return '#718096' // gray
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'CREATED': return '📝'
    case 'PAID': return '💳'
    case 'RUNNING': return '⚡'
    case 'DONE': return '✅'
    case 'FAILED': return '❌'
    default: return '❓'
  }
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  
  if (diffSec < 60) return `${diffSec}s ago`
  if (diffMin < 60) return `${diffMin}m ago`
  return date.toLocaleTimeString()
}

const formatCurrency = (cents: number) => {
  return `$${(cents / 100).toFixed(2)}`
}

// Order lifecycle steps
const ORDER_LIFECYCLE = [
  { key: 'order_placed', label: 'Order Placed', icon: '📝', requiredStatus: ['CREATED', 'PAID', 'RUNNING', 'DONE'] },
  { key: 'payment_processing', label: 'Payment Processing', icon: '⏳', requiredStatus: [] }, // Transient state
  { key: 'payment_received', label: 'Payment Received', icon: '💳', requiredStatus: ['PAID', 'RUNNING', 'DONE'] },
  { key: 'service_running', label: 'Service Running', icon: '⚡', requiredStatus: ['RUNNING', 'DONE'] },
  { key: 'completed', label: 'Completed', icon: '✅', requiredStatus: ['DONE'] },
]

const getLifecycleStatus = (orderStatus: string) => {
  return ORDER_LIFECYCLE.map(step => ({
    ...step,
    completed: step.requiredStatus.includes(orderStatus),
    current: (
      (step.key === 'order_placed' && orderStatus === 'CREATED') ||
      (step.key === 'payment_received' && orderStatus === 'PAID') ||
      (step.key === 'service_running' && orderStatus === 'RUNNING') ||
      (step.key === 'completed' && orderStatus === 'DONE')
    )
  }))
}

// Lifecycle Tooltip Component
const LifecycleTooltip = ({ order, onClose }: { order: Order; onClose: () => void }) => {
  const lifecycle = getLifecycleStatus(order.status)
  
  return (
    <>
      {/* Backdrop */}
      <div 
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.4)',
          zIndex: 9998
        }}
        onClick={onClose}
      />
      {/* Modal */}
      <div 
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 9999,
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          padding: '1.5rem',
          minWidth: '340px',
          maxWidth: '420px',
          maxHeight: '80vh',
          overflowY: 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
      >
      {/* Header with close hint */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1rem',
        paddingBottom: '0.75rem',
        borderBottom: '1px solid #E2E8F0'
      }}>
        <div style={{ fontWeight: 700, color: '#2D3748', fontSize: '1.125rem' }}>
          📋 Order Lifecycle
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '1.25rem',
            cursor: 'pointer',
            color: '#A0AEC0',
            padding: '0.25rem'
          }}
        >
          ✕
        </button>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {lifecycle.map((step, idx) => (
          <div 
            key={step.key}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.5rem',
              borderRadius: '6px',
              background: step.current ? 'rgba(66, 153, 225, 0.1)' : step.completed ? 'rgba(72, 187, 120, 0.1)' : '#f7fafc',
              border: step.current ? '2px solid #4299e1' : '1px solid transparent'
            }}
          >
            {/* Status indicator */}
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.875rem',
              background: step.completed ? '#48BB78' : step.current ? '#4299e1' : '#E2E8F0',
              color: step.completed || step.current ? 'white' : '#A0AEC0'
            }}>
              {step.completed ? '✓' : idx + 1}
            </div>
            
            {/* Step info */}
            <div style={{ flex: 1 }}>
              <div style={{
                fontWeight: step.current ? 600 : 400,
                color: step.completed ? '#48BB78' : step.current ? '#4299e1' : '#718096',
                fontSize: '0.875rem'
              }}>
                {step.icon} {step.label}
              </div>
            </div>
            
            {/* Status badge */}
            {step.current && (
              <span style={{
                fontSize: '0.625rem',
                padding: '0.125rem 0.375rem',
                borderRadius: '4px',
                background: '#4299e1',
                color: 'white',
                fontWeight: 600,
                textTransform: 'uppercase'
              }}>
                Current
              </span>
            )}
          </div>
        ))}
      </div>
      
      {/* Order details */}
      <div style={{ 
        marginTop: '1rem', 
        paddingTop: '0.75rem', 
        borderTop: '1px solid #E2E8F0',
        fontSize: '0.875rem',
        color: '#4A5568'
      }}>
        <div style={{ marginBottom: '0.5rem' }}>
          <strong>Order ID:</strong> {order.id.substring(0, 8)}...
        </div>
        <div style={{ marginBottom: '0.5rem' }}>
          <strong>Device:</strong> {order.device_label}
        </div>
        <div style={{ marginBottom: '0.5rem' }}>
          <strong>Service:</strong> {order.service_type}
        </div>
        <div style={{ marginBottom: '0.5rem' }}>
          <strong>Amount:</strong> {formatCurrency(order.amount_cents)}
        </div>
        {order.authorized_minutes > 0 && (
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Duration:</strong> {order.authorized_minutes} minutes
          </div>
        )}
        <div>
          <strong>Created:</strong> {new Date(order.created_at).toLocaleString()}
        </div>
      </div>

      {/* Close button */}
      <button
        onClick={onClose}
        style={{
          marginTop: '1rem',
          width: '100%',
          padding: '0.75rem',
          background: '#4299e1',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        Close
      </button>
    </div>
    </>
  )
}

export const LiveOrdersPanel = ({ refreshInterval = 3000 }: LiveOrdersPanelProps) => {
  const [liveData, setLiveData] = useState<LiveOrdersResponse | null>(null)
  const [realtimeStats, setRealtimeStats] = useState<RealtimeStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())
  const [hoveredOrderId, setHoveredOrderId] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const [orders, stats] = await Promise.all([
        statsApi.getLiveOrders(),
        statsApi.getRealtimeStats()
      ])
      setLiveData(orders)
      setRealtimeStats(stats)
      setLastRefresh(new Date())
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch live orders')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, refreshInterval)
    return () => clearInterval(interval)
  }, [fetchData, refreshInterval])

  if (loading && !liveData) {
    return (
      <div className="card" style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⏳</div>
        <div>Loading live orders...</div>
      </div>
    )
  }

  // Separate active orders from completed ones
  const activeOrders = liveData?.orders.filter(o => ['CREATED', 'PAID', 'RUNNING'].includes(o.status)) || []
  const recentlyCompleted = liveData?.orders.filter(o => ['DONE', 'FAILED'].includes(o.status)) || []

  return (
    <div className="card" style={{ overflow: 'visible' }}>
      {/* Header */}
      <div className="card-header" style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '1rem 1.5rem'
      }}>
        <div>
          <div className="card-title" style={{ color: 'white', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ 
              display: 'inline-block', 
              width: '10px', 
              height: '10px', 
              borderRadius: '50%', 
              background: '#ff4444',
              animation: 'pulse 1.5s infinite'
            }} />
            Live Orders
          </div>
          <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
            Auto-refresh every {refreshInterval / 1000}s • Last: {lastRefresh.toLocaleTimeString()}
          </div>
        </div>
        <button 
          onClick={fetchData}
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '0.875rem'
          }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* Real-time Stats */}
      {realtimeStats && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
          gap: '0.75rem',
          padding: '1rem 1.5rem',
          background: '#f7fafc',
          borderBottom: '1px solid #e2e8f0'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#805AD5' }}>
              {realtimeStats.pending}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#718096' }}>📝 Created</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#3182CE' }}>
              {realtimeStats.paid}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#718096' }}>💳 Paid</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#38A169' }}>
              {realtimeStats.running}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#718096' }}>⚡ Running</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#48BB78' }}>
              {realtimeStats.completed}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#718096' }}>✅ Done (24h)</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#2D3748' }}>
              {formatCurrency(realtimeStats.revenue_24h_cents)}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#718096' }}>💰 Revenue</div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div style={{ 
          padding: '1rem', 
          background: '#FED7D7', 
          color: '#C53030',
          borderBottom: '1px solid #FC8181'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Active Orders Section */}
      <div style={{ borderBottom: activeOrders.length > 0 ? '2px solid #e2e8f0' : 'none' }}>
        {activeOrders.length > 0 && (
          <div style={{ 
            padding: '0.5rem 1.5rem', 
            background: '#EBF8FF', 
            fontWeight: 600, 
            fontSize: '0.75rem',
            color: '#2B6CB0',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            🔵 Active Orders ({activeOrders.length})
          </div>
        )}
        
        <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
          {activeOrders.length === 0 ? (
            <div style={{ 
              padding: '2rem', 
              textAlign: 'center', 
              color: '#718096' 
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📭</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>No active orders</div>
              <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                Waiting for new orders from customers...
              </div>
            </div>
          ) : (
            activeOrders.map((order: Order) => (
              <div 
                key={order.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.75rem 1.5rem',
                  borderBottom: '1px solid #e2e8f0',
                  gap: '0.75rem',
                  transition: 'all 0.2s',
                  background: order.status === 'RUNNING' 
                    ? 'linear-gradient(90deg, rgba(56, 161, 105, 0.1) 0%, transparent 100%)' 
                    : 'transparent',
                  position: 'relative',
                  cursor: 'pointer'
                }}
                onClick={() => setHoveredOrderId(hoveredOrderId === order.id ? null : order.id)}
              >
                {/* Status Icon with pulse animation for running */}
                <div style={{ 
                  fontSize: '1.25rem',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '50%',
                  background: `${getStatusColor(order.status)}20`,
                  position: 'relative'
                }}>
                  {getStatusIcon(order.status)}
                  {order.status === 'RUNNING' && (
                    <span style={{
                      position: 'absolute',
                      top: '-2px',
                      right: '-2px',
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      background: '#38A169',
                      border: '2px solid white',
                      animation: 'pulse 1s infinite'
                    }} />
                  )}
                </div>

                {/* Order Details */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ 
                      fontWeight: 600,
                      color: '#2D3748',
                      fontSize: '0.875rem'
                    }}>
                      {order.device_label}
                    </span>
                    <span style={{
                      fontSize: '0.625rem',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '4px',
                      background: `${getStatusColor(order.status)}20`,
                      color: getStatusColor(order.status),
                      fontWeight: 600,
                      textTransform: 'uppercase'
                    }}>
                      {order.status}
                    </span>
                  </div>
                  <div style={{ 
                    fontSize: '0.75rem', 
                    color: '#718096',
                    marginTop: '0.125rem'
                  }}>
                    {order.service_type} • {order.authorized_minutes > 0 ? `${order.authorized_minutes} min` : 'Instant'}
                  </div>
                </div>

                {/* Amount & Time */}
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontWeight: 'bold', 
                    fontSize: '1rem',
                    color: '#2D3748'
                  }}>
                    {formatCurrency(order.amount_cents)}
                  </div>
                  <div style={{ 
                    fontSize: '0.625rem', 
                    color: '#A0AEC0' 
                  }}>
                    {formatTime(order.updated_at || order.created_at)}
                  </div>
                </div>

                {/* Lifecycle Tooltip on Click */}
                {hoveredOrderId === order.id && (
                  <LifecycleTooltip order={order} onClose={() => setHoveredOrderId(null)} />
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recently Completed Section */}
      {recentlyCompleted.length > 0 && (
        <div>
          <div style={{ 
            padding: '0.5rem 1.5rem', 
            background: '#F0FFF4', 
            fontWeight: 600, 
            fontSize: '0.75rem',
            color: '#276749',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            ✅ Recently Completed ({recentlyCompleted.length})
          </div>
          
          <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {recentlyCompleted.map((order: Order) => (
              <div 
                key={order.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.5rem 1.5rem',
                  borderBottom: '1px solid #e2e8f0',
                  gap: '0.75rem',
                  opacity: 0.7,
                  fontSize: '0.875rem'
                }}
              >
                <span>{order.status === 'DONE' ? '✅' : '❌'}</span>
                <span style={{ flex: 1 }}>{order.device_label}</span>
                <span style={{ color: '#718096' }}>{formatCurrency(order.amount_cents)}</span>
                <span style={{ 
                  fontSize: '0.625rem',
                  padding: '0.125rem 0.375rem',
                  borderRadius: '4px',
                  background: order.status === 'DONE' ? '#C6F6D5' : '#FED7D7',
                  color: order.status === 'DONE' ? '#276749' : '#C53030'
                }}>
                  {order.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pulse Animation CSS */}
      <style>{`
        @keyframes pulse {
          0% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.1); }
          100% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  )
}
