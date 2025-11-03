import { useState } from 'react'
import { useDevices, useServices, useStats, useLogs } from '../hooks'
import {
  Device,
  Service,
  DeviceCreateRequest,
  DeviceUpdateRequest,
  ServiceCreateRequest,
  ServiceUpdateRequest
} from '../types'
import { Header } from '../components/layout/Header'
import { DashboardLayout } from '../components/layout/DashboardLayout'
import { StatsGrid, DeviceGrid, OrdersTable, ServicesTable, LogsTable } from '../components/dashboard'
import { DeviceForm, ServiceForm } from '../components/forms'
import { exportToCSV } from '../utils/format'
import { AUTO_REFRESH_INTERVAL } from '../config/constants'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'devices', label: 'Devices', icon: '💡' },
  { id: 'products', label: 'Products', icon: '🛒' },
  { id: 'orders', label: 'Orders', icon: '📦' },
  { id: 'logs', label: 'Logs', icon: '📜' }
] as const

type NavItemId = typeof NAV_ITEMS[number]['id']

type FeedbackMessage = {
  type: 'success' | 'error'
  message: string
}

export const Dashboard = () => {
  const [activeView, setActiveView] = useState<NavItemId>('overview')
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null)

  const {
    devices,
    loading: devicesLoading,
    createDevice,
    updateDevice,
    deleteDevice,
    error: devicesError
  } = useDevices(true, AUTO_REFRESH_INTERVAL)

  const {
    services,
    loading: servicesLoading,
    createService,
    updateService,
    deleteService,
    error: servicesError
  } = useServices(true, AUTO_REFRESH_INTERVAL)

  const {
    stats,
    orders,
    loading: statsLoading,
    error: statsError
  } = useStats(true, AUTO_REFRESH_INTERVAL)

  const {
    logs,
    loading: logsLoading,
    error: logsError,
    refetch: refreshLogs
  } = useLogs(true, AUTO_REFRESH_INTERVAL)

  const [showDeviceForm, setShowDeviceForm] = useState(false)
  const [showServiceForm, setShowServiceForm] = useState(false)
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)
  const [editingService, setEditingService] = useState<Service | null>(null)

  const isInitialLoading = devicesLoading || servicesLoading || statsLoading
  const fetchErrors = [devicesError, servicesError, statsError].filter(Boolean) as string[]

  const showFeedback = (type: FeedbackMessage['type'], message: string) => {
    setFeedback({ type, message })
  }

  const dismissFeedback = () => setFeedback(null)

  const messageFromError = (error: any, fallback: string) => {
    if (error?.message) {
      return error.message
    }
    return fallback
  }

  // Device handlers
  const handleAddDevice = () => {
    setEditingDevice(null)
    setShowDeviceForm(true)
  }

  const handleEditDevice = (device: Device) => {
    setEditingDevice(device)
    setShowDeviceForm(true)
  }

  const handleSubmitDevice = async (device: DeviceCreateRequest | DeviceUpdateRequest) => {
    try {
      if (editingDevice) {
        await updateDevice(editingDevice.id, {
          ...(device as DeviceUpdateRequest),
          status: 'ACTIVE'
        })
        showFeedback('success', 'Device updated successfully.')
      } else {
        const newDevice = await createDevice(device as DeviceCreateRequest)
        showFeedback('success', `Device "${newDevice.label}" created.`)
      }
      setShowDeviceForm(false)
      setEditingDevice(null)
      refreshLogs()
    } catch (error: any) {
      const message = messageFromError(error, 'Unable to save device.')
      showFeedback('error', message)
      throw new Error(message)
    }
  }

  const handleDeleteDevice = async (id: string, label: string) => {
    if (!confirm(`Are you sure you want to delete device "${label}"?\n\nThis will also delete all associated products.`)) {
      return
    }
    try {
      await deleteDevice(id)
      showFeedback('success', `Device "${label}" deleted.`)
      refreshLogs()
    } catch (error: any) {
      showFeedback('error', messageFromError(error, 'Failed to delete device.'))
    }
  }

  // Service handlers
  const handleAddService = () => {
    setEditingService(null)
    setShowServiceForm(true)
  }

  const handleEditService = (service: Service) => {
    setEditingService(service)
    setShowServiceForm(true)
  }

  const handleSubmitService = async (service: ServiceCreateRequest | ServiceUpdateRequest) => {
    try {
      if (editingService) {
        await updateService(editingService.id, service as ServiceUpdateRequest)
        showFeedback('success', 'Product updated successfully.')
      } else {
        const newService = await createService(service as ServiceCreateRequest)
        showFeedback('success', `Product "${newService.type}" created.`)
      }
      setShowServiceForm(false)
      setEditingService(null)
      refreshLogs()
    } catch (error: any) {
      const message = messageFromError(error, 'Unable to save product.')
      showFeedback('error', message)
      throw new Error(message)
    }
  }

  const handleDeleteService = async (id: string, type: string) => {
    if (!confirm(`Are you sure you want to delete this ${type} product?`)) {
      return
    }
    try {
      await deleteService(id)
      showFeedback('success', `Product "${type}" deleted.`)
      refreshLogs()
    } catch (error: any) {
      showFeedback('error', messageFromError(error, 'Failed to delete product.'))
    }
  }

  // Export CSV
  const handleExportCSV = () => {
    const csvData = orders.map(order => ({
      'Order ID': order.id,
      Device: order.device_label,
      'Product Type': order.product_type,
      Amount: `$${(order.amount_cents / 100).toFixed(2)}`,
      Status: order.status,
      Created: new Date(order.created_at).toLocaleString()
    }))
    exportToCSV(csvData, `orders-${new Date().toISOString().split('T')[0]}.csv`)
  }

  const renderActiveView = () => {
    switch (activeView) {
      case 'devices':
        return (
          <DeviceGrid
            devices={devices}
            onEdit={handleEditDevice}
            onDelete={handleDeleteDevice}
            onAddNew={handleAddDevice}
          />
        )
      case 'products':
        return (
          <ServicesTable
            services={services}
            onEdit={handleEditService}
            onDelete={handleDeleteService}
            onAddNew={handleAddService}
          />
        )
      case 'orders':
        return <OrdersTable orders={orders} onExportCSV={handleExportCSV} />
      case 'logs':
        return (
          <LogsTable
            logs={logs}
            loading={logsLoading}
            error={logsError}
            onRefresh={refreshLogs}
          />
        )
      case 'overview':
      default:
        return (
          <div className="overview-stack">
            {stats ? <StatsGrid stats={stats} devices={devices} /> : null}
            <DeviceGrid
              devices={devices}
              onEdit={handleEditDevice}
              onDelete={handleDeleteDevice}
              onAddNew={handleAddDevice}
            />
            <OrdersTable orders={orders} onExportCSV={handleExportCSV} />
          </div>
        )
    }
  }

  if (isInitialLoading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <>
      <DashboardLayout
        title="RemoteLED Admin"
        subtitle="Control Center"
        navItems={NAV_ITEMS}
        activeItem={activeView}
        onSelect={setActiveView}
        headerSlot={<Header />}
      >
        {feedback ? (
          <div className={`status-banner status-${feedback.type}`}>
            <span>{feedback.message}</span>
            <button type="button" onClick={dismissFeedback} aria-label="Dismiss message">
              ×
            </button>
          </div>
        ) : null}

        {fetchErrors.map((errorMessage, idx) => (
          <div key={`fetch-error-${idx}`} className="status-banner status-error">
            <span>{errorMessage}</span>
          </div>
        ))}

        {renderActiveView()}
      </DashboardLayout>

      <DeviceForm
        isOpen={showDeviceForm}
        onClose={() => {
          setShowDeviceForm(false)
          setEditingDevice(null)
        }}
        onSubmit={handleSubmitDevice}
        editingDevice={editingDevice}
      />

      <ServiceForm
        isOpen={showServiceForm}
        onClose={() => {
          setShowServiceForm(false)
          setEditingService(null)
        }}
        onSubmit={handleSubmitService}
        devices={devices}
        editingService={editingService}
      />
    </>
  )
}

