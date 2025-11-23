import { useState, useEffect } from 'react'
import type { ServiceType, ServiceTypeCreate, ServiceTypeUpdate } from '../../types/reference'

interface ServiceTypeFormProps {
  serviceType?: ServiceType
  onSubmit: (data: ServiceTypeCreate | ServiceTypeUpdate) => Promise<void>
  onCancel: () => void
}

export const ServiceTypeForm = ({ serviceType, onSubmit, onCancel }: ServiceTypeFormProps) => {
  const [formData, setFormData] = useState({
    name: serviceType?.name || '',
    code: serviceType?.code || '',
    description: serviceType?.description || ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (serviceType) {
      setFormData({
        name: serviceType.name,
        code: serviceType.code,
        description: serviceType.description || ''
      })
    }
  }, [serviceType])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim()) {
      setError('Name is required')
      return
    }

    if (!formData.code.trim()) {
      setError('Code is required')
      return
    }

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save service type')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{serviceType ? 'Edit Service Type' : 'Add Service Type'}</h2>
          <button className="btn-close" onClick={onCancel}>×</button>
        </div>

        {error && (
          <div className="alert alert-error" style={{ margin: '1rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label htmlFor="name">Name *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Trigger Service, Fixed Duration"
                required
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="code">Code *</label>
              <input
                id="code"
                type="text"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                placeholder="e.g., TRIGGER, FIXED, VARIABLE"
                required
                disabled={isSubmitting}
                style={{ textTransform: 'uppercase' }}
              />
              <small style={{ color: '#718096', fontSize: '0.875rem' }}>
                Service type code (all caps, used in services)
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description"
                rows={3}
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

