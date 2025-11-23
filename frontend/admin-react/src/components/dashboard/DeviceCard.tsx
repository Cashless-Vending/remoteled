import { useState, useEffect, memo } from 'react'
import { Device, Service } from '../../types'
import { servicesApi } from '../../api'

interface DeviceCardProps {
  device: Device
  onEdit: (device: Device) => void
  onDelete: (id: string, label: string) => void
}

const DeviceCardComponent = ({ device, onEdit, onDelete }: DeviceCardProps) => {
  const [services, setServices] = useState<Service[]>([])
  const [loadingServices, setLoadingServices] = useState(false)
  const [servicesFetched, setServicesFetched] = useState(false)

  useEffect(() => {
    // Only fetch once per device
    if (servicesFetched) return
    
    const fetchServices = async () => {
      setLoadingServices(true)
      try {
        const deviceServices = await servicesApi.getDeviceServices(device.id)
        setServices(deviceServices)
        setServicesFetched(true)
      } catch (error) {
        console.error('Failed to load device services:', error)
      } finally {
        setLoadingServices(false)
      }
    }
    
    fetchServices()
  }, [device.id, servicesFetched])

  return (
    <div className="device-card">
      <div className="device-header">
        <div>
          <div className="device-name">{device.label}</div>
          <div className="device-id">{device.id.substring(0, 8)}...</div>
        </div>
        <span className={`badge ${device.status}`}>{device.status}</span>
      </div>
      <div className="device-info">📍 {device.location}</div>
      <div className="device-info">📦 {device.model}</div>
      
      <div style={{ marginTop: '0.75rem', marginBottom: '0.75rem' }}>
        <div style={{ fontSize: '0.75rem', color: '#718096', marginBottom: '0.375rem' }}>
          Services:
        </div>
        {loadingServices ? (
          <div style={{ fontSize: '0.75rem', color: '#a0aec0' }}>Loading...</div>
        ) : services.length === 0 ? (
          <div style={{ fontSize: '0.75rem', color: '#a0aec0' }}>No services assigned</div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
            {services.map(service => (
              <span 
                key={service.id}
                style={{
                  fontSize: '0.75rem',
                  padding: '0.125rem 0.5rem',
                  borderRadius: '9999px',
                  backgroundColor: service.active ? '#e6fffa' : '#f7fafc',
                  color: service.active ? '#047857' : '#718096',
                  border: `1px solid ${service.active ? '#10b981' : '#cbd5e0'}`
                }}
              >
                {service.type}
              </span>
            ))}
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        <button 
          className="btn btn-sm" 
          onClick={() => onEdit(device)}
          style={{ flex: 1, fontSize: '0.875rem', padding: '0.375rem 0.75rem' }}
        >
          ✏️ Edit
        </button>
        <button 
          className="btn btn-sm" 
          onClick={() => onDelete(device.id, device.label)}
          style={{ flex: 1, fontSize: '0.875rem', padding: '0.375rem 0.75rem', background: '#ef4444', color: 'white' }}
        >
          🗑️ Delete
        </button>
      </div>
    </div>
  )
}

// Memoize to prevent unnecessary re-renders
export const DeviceCard = memo(DeviceCardComponent)

