import { useState, FormEvent, useEffect, useId } from 'react'
import { Modal } from '../common/Modal'
import { Device, Service, ServiceCreateRequest, ServiceUpdateRequest } from '../../types'

interface ServiceFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (service: ServiceCreateRequest | ServiceUpdateRequest) => Promise<void>
  devices: Device[]
  editingService?: Service | null
}

export const ServiceForm = ({ isOpen, onClose, onSubmit, devices, editingService }: ServiceFormProps) => {
  const formId = useId()
  const deviceId = `${formId}-device`
  const typeId = `${formId}-type`
  const priceId = `${formId}-price`
  const fixedId = `${formId}-fixed`
  const variableId = `${formId}-variable`

  const [formData, setFormData] = useState({
    device_id: '',
    type: 'TRIGGER' as 'TRIGGER' | 'FIXED' | 'VARIABLE',
    price_cents: 100,
    fixed_minutes: 30,
    minutes_per_25c: 15,
    active: true
  })
  const [loading, setLoading] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (editingService) {
      setFormData({
        device_id: editingService.device_id,
        type: editingService.type,
        price_cents: editingService.price_cents,
        fixed_minutes: editingService.fixed_minutes || 30,
        minutes_per_25c: editingService.minutes_per_25c || 15,
        active: editingService.active
      })
    } else if (devices.length > 0) {
      setFormData(prev => ({
        ...prev,
        device_id: devices[0].id
      }))
    }
  }, [editingService, devices, isOpen])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFormError(null)
    try {
      const payload: any = {
        device_id: formData.device_id,
        type: formData.type,
        price_cents: formData.price_cents,
        active: formData.active
      }

      if (formData.type === 'FIXED') {
        payload.fixed_minutes = formData.fixed_minutes
      } else if (formData.type === 'VARIABLE') {
        payload.minutes_per_25c = formData.minutes_per_25c
      }

      await onSubmit(payload)
      onClose()
    } catch (error: any) {
      setFormError(error?.message || `Failed to ${editingService ? 'update' : 'create'} product.`)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    onClose()
    setFormData({
      device_id: devices[0]?.id || '',
      type: 'TRIGGER',
      price_cents: 100,
      fixed_minutes: 30,
      minutes_per_25c: 15,
      active: true
    })
    setFormError(null)
  }

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={editingService ? 'Edit Product' : 'Add New Product'}
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
          <label htmlFor={deviceId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Device *
          </label>
          <select
            id={deviceId}
            required
            value={formData.device_id}
            onChange={(e) => setFormData({ ...formData, device_id: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          >
            {devices.map(device => (
              <option key={device.id} value={device.id}>{device.label}</option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={typeId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Type *
          </label>
          <select
            id={typeId}
            required
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          >
            <option value="TRIGGER">TRIGGER (2 seconds)</option>
            <option value="FIXED">FIXED (fixed duration)</option>
            <option value="VARIABLE">VARIABLE (pay per minute)</option>
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor={priceId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Price (cents) *
          </label>
          <input
            id={priceId}
            type="number"
            required
            min="0"
            value={formData.price_cents}
            onChange={(e) => setFormData({ ...formData, price_cents: Number(e.target.value) })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        {formData.type === 'FIXED' && (
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor={fixedId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Fixed Minutes *
            </label>
            <input
              id={fixedId}
              type="number"
              required
              min="1"
              value={formData.fixed_minutes}
              onChange={(e) => setFormData({ ...formData, fixed_minutes: Number(e.target.value) })}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
            />
          </div>
        )}

        {formData.type === 'VARIABLE' && (
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor={variableId} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Minutes per $0.25 *
            </label>
            <input
              id={variableId}
              type="number"
              required
              min="1"
              value={formData.minutes_per_25c}
              onChange={(e) => setFormData({ ...formData, minutes_per_25c: Number(e.target.value) })}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
            />
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button type="button" className="btn" onClick={handleClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : (editingService ? 'Update Product' : 'Create Product')}
          </button>
        </div>
      </form>
    </Modal>
  )
}

