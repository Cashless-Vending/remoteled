import { useState } from 'react'
import { useDevices, useServices, useStats } from '../hooks'
import { Device, Service, DeviceCreateRequest, DeviceUpdateRequest, ServiceCreateRequest, ServiceUpdateRequest } from '../types'
import { Header } from '../components/layout/Header'
import { StatsGrid, DeviceGrid, OrdersTable, ServicesTable } from '../components/dashboard'
import { DeviceForm, ServiceForm } from '../components/forms'
import { exportToCSV } from '../utils/format'
import { AUTO_REFRESH_INTERVAL } from '../config/constants'

export const Dashboard = () => {
  const { devices, loading: devicesLoading, createDevice, updateDevice, deleteDevice } = useDevices(true, AUTO_REFRESH_INTERVAL)
  const { services, loading: servicesLoading, createService, updateService, deleteService } = useServices(true, AUTO_REFRESH_INTERVAL)
  const { stats, orders, loading: statsLoading } = useStats(true, AUTO_REFRESH_INTERVAL)

  const [showDeviceForm, setShowDeviceForm] = useState(false)
  const [showServiceForm, setShowServiceForm] = useState(false)
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)
  const [editingService, setEditingService] = useState<Service | null>(null)

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
    if (editingDevice) {
      await updateDevice(editingDevice.id, {
        ...device as DeviceUpdateRequest,
        status: 'ACTIVE'
      })
      alert(`Device updated successfully!`)
    } else {
      const newDevice = await createDevice(device as DeviceCreateRequest)
      alert(`Device created successfully!\nID: ${newDevice.id}\nLabel: ${newDevice.label}`)
    }
    setShowDeviceForm(false)
    setEditingDevice(null)
  }

  const handleDeleteDevice = async (id: string, label: string) => {
    if (!confirm(`Are you sure you want to delete device "${label}"?\n\nThis will also delete all associated products.`)) {
      return
    }
    try {
      await deleteDevice(id)
      alert(`Device "${label}" deleted successfully!`)
    } catch (error: any) {
      alert(`Failed to delete device:\n\n${error.message}`)
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
    if (editingService) {
      await updateService(editingService.id, service as ServiceUpdateRequest)
      alert(`Product updated successfully!`)
    } else {
      const newService = await createService(service as ServiceCreateRequest)
      alert(`Product created successfully!\nID: ${newService.id}\nType: ${newService.type}`)
    }
    setShowServiceForm(false)
    setEditingService(null)
  }

  const handleDeleteService = async (id: string, type: string) => {
    if (!confirm(`Are you sure you want to delete this ${type} product?`)) {
      return
    }
    try {
      await deleteService(id)
      alert(`Product deleted successfully!`)
    } catch (error: any) {
      alert(`Failed to delete product:\n\n${error.message}`)
    }
  }

  // Export CSV
  const handleExportCSV = () => {
    const csvData = orders.map(order => ({
      'Order ID': order.id,
      'Device': order.device_label,
      'Product Type': order.product_type,
      'Amount': `$${(order.amount_cents / 100).toFixed(2)}`,
      'Status': order.status,
      'Created': new Date(order.created_at).toLocaleString()
    }))
    exportToCSV(csvData, `orders-${new Date().toISOString().split('T')[0]}.csv`)
  }

  if (devicesLoading || servicesLoading || statsLoading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <>
      <Header />
      <div className="container">
        <StatsGrid stats={stats} devices={devices} />
        <DeviceGrid 
          devices={devices}
          onEdit={handleEditDevice}
          onDelete={handleDeleteDevice}
          onAddNew={handleAddDevice}
        />
        <OrdersTable 
          orders={orders}
          onExportCSV={handleExportCSV}
        />
        <ServicesTable 
          services={services}
          onEdit={handleEditService}
          onDelete={handleDeleteService}
          onAddNew={handleAddService}
        />

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
      </div>
    </>
  )
}

