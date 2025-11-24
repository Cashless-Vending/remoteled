import { useState, useEffect } from 'react'
import type { ServiceType, ServiceTypeCreate, ServiceTypeUpdate } from '../../types/reference'
import { SERVICE_TYPE_CODES } from '../../constants/serviceTypes'

interface ServiceTypeFormProps {
  serviceType?: ServiceType
  onSubmit: (data: ServiceTypeCreate | ServiceTypeUpdate) => Promise<void>
  onCancel: () => void
  existingCodes: string[]
}

export const ServiceTypeForm = ({
  serviceType,
  onSubmit,
  onCancel,
  existingCodes
}: ServiceTypeFormProps) => {
  const availableCodeOptions = SERVICE_TYPE_CODES.filter(option => {
    if (serviceType?.code === option.value) {
      return true
    }
    return !existingCodes?.includes(option.value)
  })

  const initialCode =
    serviceType?.code ||
    availableCodeOptions[0]?.value ||
    SERVICE_TYPE_CODES.find(option => !existingCodes?.includes(option.value))?.value ||
    SERVICE_TYPE_CODES[0].value

  const [formData, setFormData] = useState({
    name: serviceType?.name || '',
    code: initialCode,
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

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
      onCancel()
    } catch (err: any) {
      setError(err?.message || 'Failed to save service type')
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
              <select
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                required
                disabled={isSubmitting || availableCodeOptions.length === 0}
              >
                {SERVICE_TYPE_CODES.map(option => {
                  const inUse = existingCodes?.includes(option.value)
                  const disabled =
                    serviceType?.code === option.value ? false : inUse
                  return (
                    <option key={option.value} value={option.value} disabled={disabled}>
                      {option.label} ({option.value})
                    </option>
                  )
                })}
              </select>
              <small style={{ color: '#718096', fontSize: '0.875rem' }}>
                Code must map to one of the built-in service behaviors (Trigger, Fixed, Variable).
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

