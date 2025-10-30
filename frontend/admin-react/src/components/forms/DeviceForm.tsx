import { useState, FormEvent, useEffect } from 'react'
import { Modal } from '../common/Modal'
import { Device, DeviceCreateRequest, DeviceUpdateRequest } from '../../types'

interface DeviceFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (device: DeviceCreateRequest | DeviceUpdateRequest) => Promise<void>
  editingDevice?: Device | null
}

export const DeviceForm = ({ isOpen, onClose, onSubmit, editingDevice }: DeviceFormProps) => {
  const [formData, setFormData] = useState({
    label: '',
    public_key: '',
    model: 'RPi 4 Model B',
    location: '',
    gpio_pin: 17
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (editingDevice) {
      setFormData({
        label: editingDevice.label,
        public_key: '',
        model: editingDevice.model,
        location: editingDevice.location,
        gpio_pin: editingDevice.gpio_pin
      })
    } else {
      setFormData({
        label: 'New Device',
        public_key: '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----',
        model: 'RPi 4 Model B',
        location: 'Building 1',
        gpio_pin: 17
      })
    }
  }, [editingDevice, isOpen])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit(formData as any)
      onClose()
    } catch (error: any) {
      alert(`Failed to ${editingDevice ? 'update' : 'create'} device:\n\n${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    onClose()
    setFormData({
      label: '',
      public_key: '',
      model: 'RPi 4 Model B',
      location: '',
      gpio_pin: 17
    })
  }

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={editingDevice ? 'Edit Device' : 'Add New Device'}
    >
      <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Device Label *
          </label>
          <input
            type="text"
            required
            value={formData.label}
            onChange={(e) => setFormData({ ...formData, label: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        {!editingDevice && (
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Public Key *
            </label>
            <textarea
              required
              value={formData.public_key}
              onChange={(e) => setFormData({ ...formData, public_key: e.target.value })}
              rows={4}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
            />
          </div>
        )}

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Model
          </label>
          <input
            type="text"
            value={formData.model}
            onChange={(e) => setFormData({ ...formData, model: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            GPIO Pin
          </label>
          <input
            type="number"
            min="0"
            max="40"
            value={formData.gpio_pin}
            onChange={(e) => setFormData({ ...formData, gpio_pin: Number(e.target.value) })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
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

