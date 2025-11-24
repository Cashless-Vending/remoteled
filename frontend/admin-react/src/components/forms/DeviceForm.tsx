import { useState, FormEvent, useEffect, useId } from 'react'
import { Modal } from '../common/Modal'
import { Device, DeviceCreateRequest, DeviceUpdateRequest, Service } from '../../types'
import { servicesApi } from '../../api'
import { useDeviceModels } from '../../hooks/useDeviceModels'
import { useLocations } from '../../hooks/useLocations'

interface DeviceFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (device: DeviceCreateRequest | DeviceUpdateRequest, serviceIds?: string[]) => Promise<void>
  editingDevice?: Device | null
}

export const DeviceForm = ({ isOpen, onClose, onSubmit, editingDevice }: DeviceFormProps) => {
  const formId = useId()
  const labelId = `${formId}-label`
  const publicKeyId = `${formId}-public-key`
  const modelId = `${formId}-model`
  const locationId = `${formId}-location`
  const gpioId = `${formId}-gpio`

  const [formData, setFormData] = useState({
    label: '',
    public_key: '',
    model: 'RPi 4 Model B',
    location: '',
    model_id: '',
    location_id: '',
    gpio_pin: 17,
    status: 'ACTIVE' as 'ACTIVE' | 'OFFLINE' | 'MAINTENANCE' | 'DEACTIVATED'
  })
  const [loading, setLoading] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [availableServices, setAvailableServices] = useState<Service[]>([])
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [loadingServices, setLoadingServices] = useState(false)

  const { models = [] } = useDeviceModels() || {}
  const { locations = [] } = useLocations() || {}

  // Load available services when modal opens
  useEffect(() => {
    if (isOpen) {
      setLoadingServices(true)
      servicesApi.getAll()
        .then(services => {
          setAvailableServices(services)
        })
        .catch(err => {
          console.error('Failed to load services:', err)
        })
        .finally(() => {
          setLoadingServices(false)
        })
    }
  }, [isOpen])

  // Load device data and assigned services when editing
  useEffect(() => {
    if (editingDevice) {
      setFormData({
        label: editingDevice.label,
        public_key: '',
        model: editingDevice.model,
        location: editingDevice.location,
        gpio_pin: editingDevice.gpio_pin,
        status: editingDevice.status as 'ACTIVE' | 'OFFLINE' | 'MAINTENANCE' | 'DEACTIVATED'
      })
      
      // Load assigned services for this device
      if (isOpen) {
        servicesApi.getDeviceServices(editingDevice.id)
          .then(services => {
            setSelectedServices(services.map(s => s.id))
          })
          .catch(err => {
            console.error('Failed to load device services:', err)
          })
      }
    } else {
      setFormData({
        label: 'New Device',
        public_key: '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----',
        model: 'RPi 4 Model B',
        location: 'Building 1',
        gpio_pin: 17,
        status: 'ACTIVE'
      })
      setSelectedServices([])
    }
  }, [editingDevice, isOpen])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFormError(null)
    try {
      await onSubmit(formData as any, selectedServices)
      onClose()
    } catch (error: any) {
      setFormError(error?.message || `Failed to ${editingDevice ? 'update' : 'create'} device.`)
    } finally {
      setLoading(false)
    }
  }

  const toggleService = (serviceId: string) => {
    setSelectedServices(prev =>
      prev.includes(serviceId)
        ? prev.filter(id => id !== serviceId)
        : [...prev, serviceId]
    )
  }

  const handleClose = () => {
    onClose()
    setFormData({
      label: '',
      public_key: '',
      model: 'RPi 4 Model B',
      location: '',
      gpio_pin: 17,
      status: 'ACTIVE'
    })
    setFormError(null)
  }

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={editingDevice ? 'Edit Device' : 'Add New Device'}
    >
      <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
        {formError ? (
          <div className="status-banner status-error" style={{ marginBottom: '1rem' }}>
            <span>{formError}</span>
            <button type="button" onClick={() => setFormError(null)} aria-label="Clear error">
              ×
            </button>
          </div>
        ) : null}

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={labelId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Device Label *
          </label>
          <input
            id={labelId}
            type="text"
            required
            value={formData.label}
            onChange={(e) => setFormData({ ...formData, label: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        {!editingDevice && (
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor={publicKeyId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Public Key *
            </label>
            <textarea
              id={publicKeyId}
              required
              value={formData.public_key}
              onChange={(e) => setFormData({ ...formData, public_key: e.target.value })}
              rows={4}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
            />
          </div>
        )}

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={modelId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Model
          </label>
          <select
            id={modelId}
            value={formData.model_id}
            onChange={(e) => {
              const selectedModel = models.find(m => m.id === e.target.value)
              setFormData({ 
                ...formData, 
                model_id: e.target.value,
                model: selectedModel?.name || ''
              })
            }}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          >
            <option value="">Select a model</option>
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={locationId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Location
          </label>
          <select
            id={locationId}
            value={formData.location_id}
            onChange={(e) => {
              const selectedLocation = locations.find(l => l.id === e.target.value)
              setFormData({ 
                ...formData, 
                location_id: e.target.value,
                location: selectedLocation?.name || ''
              })
            }}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          >
            <option value="">Select a location</option>
            {locations.map(location => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={gpioId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            GPIO Pin
          </label>
          <input
            id={gpioId}
            type="number"
            min="0"
            max="40"
            value={formData.gpio_pin}
            onChange={(e) => setFormData({ ...formData, gpio_pin: Number(e.target.value) })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={`${formId}-status`} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Status
          </label>
          <select
            id={`${formId}-status`}
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value as 'ACTIVE' | 'OFFLINE' | 'MAINTENANCE' | 'DEACTIVATED' })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          >
            <option value="ACTIVE">Active</option>
            <option value="OFFLINE">Offline</option>
            <option value="MAINTENANCE">Maintenance</option>
            <option value="DEACTIVATED">Deactivated</option>
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Assigned Services
          </label>
          {loadingServices ? (
            <p style={{ fontSize: '0.875rem', color: '#718096' }}>Loading services...</p>
          ) : availableServices.length === 0 ? (
            <p style={{ fontSize: '0.875rem', color: '#718096' }}>No services available. Create services first.</p>
          ) : (
            <div style={{ 
              border: '1px solid #e2e8f0', 
              borderRadius: '4px', 
              padding: '0.75rem',
              maxHeight: '200px',
              overflowY: 'auto'
            }}>
              {availableServices.map(service => (
                <label 
                  key={service.id} 
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    padding: '0.5rem',
                    cursor: 'pointer',
                    borderRadius: '4px',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f7fafc'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <input
                    type="checkbox"
                    checked={selectedServices.includes(service.id)}
                    onChange={() => toggleService(service.id)}
                    style={{ marginRight: '0.75rem', cursor: 'pointer' }}
                  />
                  <span style={{ flex: 1 }}>
                    <strong>{service.type}</strong> - ${(service.price_cents / 100).toFixed(2)}
                    {service.fixed_minutes && ` (${service.fixed_minutes} min)`}
                    {service.minutes_per_25c && ` (${service.minutes_per_25c} min/$0.25)`}
                  </span>
                  {!service.active && (
                    <span style={{ fontSize: '0.75rem', color: '#e53e3e', marginLeft: '0.5rem' }}>
                      (Inactive)
                    </span>
                  )}
                </label>
              ))}
            </div>
          )}
          <p style={{ fontSize: '0.75rem', color: '#718096', marginTop: '0.5rem' }}>
            Select which services this device can provide to customers
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button type="button" className="btn" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : (editingDevice ? 'Update Device' : 'Create Device')}
          </button>
        </div>
      </form>
    </Modal>
  )
}

