import { useState, useEffect } from 'react'
import type { DeviceModel, DeviceModelCreate, DeviceModelUpdate } from '../../types/reference'

interface DeviceModelFormProps {
  model?: DeviceModel
  onSubmit: (data: DeviceModelCreate | DeviceModelUpdate) => Promise<void>
  onCancel: () => void
}

export const DeviceModelForm = ({ model, onSubmit, onCancel }: DeviceModelFormProps) => {
  const [formData, setFormData] = useState({
    name: model?.name || '',
    description: model?.description || ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (model) {
      setFormData({
        name: model.name,
        description: model.description || ''
      })
    }
  }, [model])

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
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save device model')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{model ? 'Edit Device Model' : 'Add Device Model'}</h2>
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
                placeholder="e.g., RPi 4 Model B"
                required
                disabled={isSubmitting}
              />
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

