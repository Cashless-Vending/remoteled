import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'
import DeviceForm from './pages/DeviceForm'
import ServiceForm from './pages/ServiceForm'

// TypeScript interfaces
interface Stats {
  total_devices: number
  new_devices_this_month: number
  active_orders: number
  orders_change_percent: number
  revenue_today_cents: number
  revenue_change_percent: number
  success_rate: number
  success_rate_change: number
}

interface OrderChartData {
  day_name: string
  order_count: number
}

interface DeviceStatusData {
  status: string
  count: number
}

interface Device {
  id: string
  label: string
  model: string | null
  location: string | null
  gpio_pin: number | null
  status: string
  created_at: string
  service_count: number
  active_service_count: number
  total_orders: number
  completed_orders: number
}

interface Order {
  id: string
  device_label: string
  product_type: string
  amount_cents: number
  authorized_minutes: number
  status: string
  created_at: string
}

interface Service {
  id: string
  device_label: string
  device_id: string
  type: string
  price_cents: number
  fixed_minutes: number | null
  minutes_per_25c: number | null
  active: boolean
  created_at: string
}

interface Log {
  id: string
  device_label: string
  device_id: string
  direction: string
  ok: boolean
  details: string
  created_at: string
}

function Dashboard() {
  const navigate = useNavigate()
  
  // State
  const [stats, setStats] = useState<Stats | null>(null)
  const [ordersChart, setOrdersChart] = useState<OrderChartData[]>([])
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatusData[]>([])
  const [devices, setDevices] = useState<Device[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [services, setServices] = useState<Service[]>([])
  const [logs, setLogs] = useState<Log[]>([])
  const [showErrorsOnly, setShowErrorsOnly] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Utility functions
  const formatCurrency = (cents: number) => `$${(cents / 100).toFixed(2)}`
  
  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
  
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
  
  const truncateId = (id: string, length = 12) => id.substring(0, length)
  
  const getChangeClass = (value: number) => value >= 0 ? 'positive' : 'negative'
  
  const getChangeSymbol = (value: number) => value >= 0 ? '↑' : '↓'
  
  const getLedColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'TRIGGER': '🔵 Blue Blink',
      'FIXED': '🟢 Green Solid',
      'VARIABLE': '🟠 Amber Solid'
    }
    return colorMap[type] || '⚪ Default'
  }
  
  const getDurationText = (type: string, fixedMinutes: number | null, minutesPer25c: number | null) => {
    if (type === 'TRIGGER') return '2 seconds'
    if (type === 'FIXED') return `${fixedMinutes} minutes`
    if (type === 'VARIABLE') return 'Variable duration'
    return 'N/A'
  }

  // CSV Export function
  const exportToCSV = () => {
    const headers = ['Order ID', 'Device', 'Product Type', 'Amount', 'Duration', 'Status', 'Timestamp']
    const rows = orders.map(order => [
      order.id,
      order.device_label,
      order.product_type,
      formatCurrency(order.amount_cents),
      order.authorized_minutes > 0 ? `${order.authorized_minutes} min` : '2 sec',
      order.status,
      formatDateTime(order.created_at)
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `orders-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // API fetch function
  const fetchData = async (endpoint: string) => {
    try {
      const response = await fetch(`/api${endpoint}`)
      if (!response.ok) throw new Error('Network response was not ok')
      return await response.json()
    } catch (err: any) {
      console.error(`Error fetching ${endpoint}:`, err)
      setError(err.message)
      return null
    }
  }

  // Load all dashboard data
  const loadDashboard = async () => {
    try {
      const [
        statsData,
        ordersChartData,
        deviceStatusData,
        devicesData,
        ordersData,
        servicesData,
        logsData
      ] = await Promise.all([
        fetchData('/admin/stats/overview'),
        fetchData('/admin/stats/orders-last-7-days'),
        fetchData('/admin/stats/device-status'),
        fetchData('/admin/devices/all'),
        fetchData('/admin/orders/recent?limit=20'),
        fetchData('/admin/services/all'),
        fetchData(`/admin/logs/recent?limit=50${showErrorsOnly ? '&error_only=true' : ''}`)
      ])

      if (statsData) setStats(statsData)
      if (ordersChartData) setOrdersChart(ordersChartData)
      if (deviceStatusData) setDeviceStatus(deviceStatusData)
      if (devicesData) setDevices(devicesData)
      if (ordersData) setOrders(ordersData)
      if (servicesData) setServices(servicesData)
      if (logsData) setLogs(logsData)
    } catch (err: any) {
      setError(err.message)
    }
  }

  // Load logs separately when filter changes
  const loadLogs = async () => {
    const logsData = await fetchData(`/admin/logs/recent?limit=50${showErrorsOnly ? '&error_only=true' : ''}`)
    if (logsData) setLogs(logsData)
  }

  // Initial load
  useEffect(() => {
    loadDashboard()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadDashboard, 30000)
    return () => clearInterval(interval)
  }, [])

  // Reload logs when filter changes
  useEffect(() => {
    loadLogs()
  }, [showErrorsOnly])

  return (
    <div>
      {/* Header */}
      <div className="header">
        <h1>🏪 RemoteLED Admin Console</h1>
        <p>Monitor and manage your cashless vending devices</p>
      </div>

      <div className="container">
        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {/* Statistics Overview */}
        {stats && (
          <div className="stats-grid">
            <div className="stat-card blue">
              <div className="stat-label">Total Devices</div>
              <div className="stat-value">{stats.total_devices}</div>
              <div className={`stat-change ${getChangeClass(stats.new_devices_this_month)}`}>
                {getChangeSymbol(stats.new_devices_this_month)} {stats.new_devices_this_month} this month
              </div>
            </div>

            <div className="stat-card green">
              <div className="stat-label">Active Orders</div>
              <div className="stat-value">{stats.active_orders}</div>
              <div className={`stat-change ${getChangeClass(stats.orders_change_percent)}`}>
                {getChangeSymbol(stats.orders_change_percent)} {Math.abs(stats.orders_change_percent).toFixed(1)}% vs last week
              </div>
            </div>

            <div className="stat-card purple">
              <div className="stat-label">Revenue Today</div>
              <div className="stat-value">{formatCurrency(stats.revenue_today_cents)}</div>
              <div className={`stat-change ${getChangeClass(stats.revenue_change_percent)}`}>
                {getChangeSymbol(stats.revenue_change_percent)} {Math.abs(stats.revenue_change_percent).toFixed(1)}% vs yesterday
              </div>
            </div>

            <div className="stat-card orange">
              <div className="stat-label">Success Rate</div>
              <div className="stat-value">{stats.success_rate}%</div>
              <div className={`stat-change ${getChangeClass(stats.success_rate_change)}`}>
                {getChangeSymbol(stats.success_rate_change)} {Math.abs(stats.success_rate_change).toFixed(1)}% this week
              </div>
            </div>
          </div>
        )}

        {/* Charts Row */}
        <div className="grid-2">
          {/* Orders Chart */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Orders Last 7 Days</div>
            </div>
            <div className="chart-container">
              {ordersChart.length > 0 ? (
                ordersChart.map((day, idx) => {
                  const maxCount = Math.max(...ordersChart.map(d => d.order_count), 1)
                  const height = (day.order_count / maxCount * 100)
                  return (
                    <div key={idx} className="bar" style={{ height: `${height}%` }}>
                      <div className="bar-value">{day.order_count}</div>
                      <div className="bar-label">{day.day_name}</div>
                    </div>
                  )
                })
              ) : (
                <div className="loading"></div>
              )}
            </div>
          </div>

          {/* Device Status Chart */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Device Status Distribution</div>
            </div>
            <div className="chart-container">
              {deviceStatus.length > 0 ? (
                deviceStatus.map((item, idx) => {
                  const maxCount = Math.max(...deviceStatus.map(d => d.count), 1)
                  const height = (item.count / maxCount * 100)
                  const colorMap: Record<string, string> = {
                    'ACTIVE': 'linear-gradient(to top, #48bb78, #38a169)',
                    'OFFLINE': 'linear-gradient(to top, #f56565, #e53e3e)',
                    'MAINTENANCE': 'linear-gradient(to top, #ed8936, #dd6b20)',
                    'DEACTIVATED': 'linear-gradient(to top, #718096, #4a5568)'
                  }
                  return (
                    <div 
                      key={idx} 
                      className="bar" 
                      style={{ 
                        height: `${Math.max(height, 15)}%`,
                        background: colorMap[item.status] || colorMap['OFFLINE']
                      }}
                    >
                      <div className="bar-value">{item.count}</div>
                      <div className="bar-label">{item.status}</div>
                    </div>
                  )
                })
              ) : (
                <div className="loading"></div>
              )}
            </div>
          </div>
        </div>

        {/* Devices Management */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Registered Devices</div>
            <button className="btn btn-primary" onClick={() => navigate('/device/new')}>+ Add New Device</button>
          </div>
          <div className="device-grid">
            {devices.length > 0 ? (
              devices.map(device => (
                <div key={device.id} className="device-card">
                  <div className="device-header">
                    <div>
                      <div className="device-name">{device.label}</div>
                      <div className="device-id">Device ID: {truncateId(device.id)}</div>
                    </div>
                    <span className={`badge ${device.status}`}>{device.status}</span>
                  </div>
                  <div className="device-info">📍 {device.location || 'No location set'}</div>
                  <div className="device-info">🔧 GPIO Pin: {device.gpio_pin || 'Not configured'}</div>
                  <div className="device-info">
                    📊 {device.active_service_count} Active Products ({device.service_count} total)
                  </div>
                  <div className="device-info">
                    ✅ {device.completed_orders} / {device.total_orders} orders completed
                  </div>
                  <div className="device-actions">
                    <button className="btn btn-primary btn-sm" onClick={() => navigate(`/device/edit/${device.id}`)}>Configure</button>
                    <button className={`btn ${device.status === 'ACTIVE' ? 'btn-success' : 'btn-danger'} btn-sm`}>
                      {device.status === 'ACTIVE' ? 'Test Cycle' : 'Troubleshoot'}
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="loading"></div>
            )}
          </div>
        </div>

        {/* Recent Orders */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Recent Orders</div>
            <button className="btn btn-primary btn-sm" onClick={exportToCSV}>Export CSV</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Device</th>
                <th>Product Type</th>
                <th>Amount</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {orders.length > 0 ? (
                orders.map(order => (
                  <tr key={order.id}>
                    <td>{truncateId(order.id)}</td>
                    <td>{order.device_label}</td>
                    <td>{order.product_type}</td>
                    <td>{formatCurrency(order.amount_cents)}</td>
                    <td>{order.authorized_minutes > 0 ? `${order.authorized_minutes} min` : '2 sec'}</td>
                    <td><span className={`badge ${order.status}`}>{order.status}</span></td>
                    <td>{formatDateTime(order.created_at)}</td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan={7} style={{ textAlign: 'center' }}>Loading...</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Products Configuration */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Product Catalog</div>
            <button className="btn btn-primary" onClick={() => navigate('/service/new')}>+ Add Product</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Device</th>
                <th>Type</th>
                <th>Price</th>
                <th>Duration/Action</th>
                <th>LED Color</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {services.length > 0 ? (
                services.map(service => {
                  const priceText = service.type === 'VARIABLE' 
                    ? `${formatCurrency(25)} / ${service.minutes_per_25c}min`
                    : formatCurrency(service.price_cents)
                  
                  return (
                    <tr key={service.id}>
                      <td>{truncateId(service.id)}</td>
                      <td>{service.device_label}</td>
                      <td>{service.type}</td>
                      <td>{priceText}</td>
                      <td>{getDurationText(service.type, service.fixed_minutes, service.minutes_per_25c)}</td>
                      <td>{getLedColor(service.type)}</td>
                      <td>
                        <span className={`badge ${service.active ? 'active' : 'offline'}`}>
                          {service.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td><button className="btn btn-primary btn-sm">Edit</button></td>
                    </tr>
                  )
                })
              ) : (
                <tr><td colSpan={8} style={{ textAlign: 'center' }}>Loading...</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* System Logs */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">System Logs & Telemetry</div>
          </div>
          <div className="tabs">
            <div 
              className={`tab ${!showErrorsOnly ? 'active' : ''}`}
              onClick={() => setShowErrorsOnly(false)}
            >
              All Logs
            </div>
            <div 
              className={`tab ${showErrorsOnly ? 'active' : ''}`}
              onClick={() => setShowErrorsOnly(true)}
            >
              Errors Only
            </div>
          </div>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {logs.length > 0 ? (
              logs.map(log => {
                const levelClass = log.ok ? 'success' : 'error'
                const levelText = log.ok ? 'INFO' : 'ERROR'
                
                return (
                  <div key={log.id} className="log-entry">
                    <span className="log-time">{formatTime(log.created_at)}</span>
                    <span className={`log-level ${levelClass}`}>[{levelText}]</span>
                    <span>Device {log.device_label} - {log.details}</span>
                  </div>
                )
              })
            ) : (
              <div className="empty-state">No logs found</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/device/new" element={<DeviceForm />} />
      <Route path="/device/edit/:id" element={<DeviceForm />} />
      <Route path="/service/new" element={<ServiceForm />} />
    </Routes>
  )
}

export default App
