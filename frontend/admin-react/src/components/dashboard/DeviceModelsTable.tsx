import { useState } from 'react'
import type { DeviceModel } from '../../types/reference'
import { formatDateTime } from '../../utils/format'

interface DeviceModelsTableProps {
  models: DeviceModel[]
  onAdd: () => void
  onEdit: (model: DeviceModel) => void
  onDelete: (modelId: string) => void
}

export const DeviceModelsTable = ({ models, onAdd, onEdit, onDelete }: DeviceModelsTableProps) => {
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const safeModels = models || []

  const handleDelete = async (modelId: string) => {
    if (!window.confirm('Are you sure you want to delete this device model?')) {
      return
    }
    setDeletingId(modelId)
    try {
      await onDelete(modelId)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Device Models</div>
        <button className="btn btn-primary btn-sm" onClick={onAdd}>
          + Add Model
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {safeModels.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                No device models found. Add your first model to get started.
              </td>
            </tr>
          ) : (
            safeModels.map(model => (
              <tr key={model.id}>
                <td>{model.name}</td>
                <td>{model.description || '-'}</td>
                <td>{formatDateTime(model.created_at)}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-sm"
                      onClick={() => onEdit(model)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(model.id)}
                      disabled={deletingId === model.id}
                    >
                      {deletingId === model.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

