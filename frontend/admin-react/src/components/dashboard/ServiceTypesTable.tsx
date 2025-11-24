import { useState } from 'react'
import type { ServiceType } from '../../types/reference'
import { formatDateTime } from '../../utils/format'
import { MAX_SERVICE_TYPE_COUNT } from '../../constants/serviceTypes'

interface ServiceTypesTableProps {
  serviceTypes: ServiceType[]
  onAdd: () => void
  onEdit: (serviceType: ServiceType) => void
  onDelete: (serviceTypeId: string) => void
}

export const ServiceTypesTable = ({ serviceTypes, onAdd, onEdit, onDelete }: ServiceTypesTableProps) => {
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const safeServiceTypes = serviceTypes || []
  const reachedLimit = safeServiceTypes.length >= MAX_SERVICE_TYPE_COUNT

  const handleDelete = async (serviceTypeId: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete the service type "${name}"?`)) {
      return
    }
    setDeletingId(serviceTypeId)
    try {
      await onDelete(serviceTypeId)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="card">
      <div className="card-header" style={{ gap: '0.75rem' }}>
        <div>
          <div className="card-title">Service Types</div>
          {reachedLimit && (
            <div style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.25rem' }}>
              All built-in service behaviors are already configured. Edit existing entries to update copy.
            </div>
          )}
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={onAdd}
          disabled={reachedLimit}
          title={reachedLimit ? 'All service type codes (TRIGGER/FIXED/VARIABLE) are already defined.' : undefined}
        >
          + Add Service Type
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Code</th>
            <th>Description</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {safeServiceTypes.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                No service types found. Add your first service type to get started.
              </td>
            </tr>
          ) : (
            safeServiceTypes.map(serviceType => (
              <tr key={serviceType.id}>
                <td>{serviceType.name}</td>
                <td>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: '#e6fffa',
                    color: '#047857',
                    fontSize: '0.875rem',
                    fontWeight: 500
                  }}>
                    {serviceType.code}
                  </span>
                </td>
                <td>{serviceType.description || '-'}</td>
                <td>{formatDateTime(serviceType.created_at)}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-sm"
                      onClick={() => onEdit(serviceType)}
                      disabled={deletingId === serviceType.id}
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                    >
                      ✏️ Edit
                    </button>
                    <button
                      className="btn btn-sm"
                      onClick={() => handleDelete(serviceType.id, serviceType.name)}
                      disabled={deletingId === serviceType.id}
                      style={{
                        fontSize: '0.75rem',
                        padding: '0.25rem 0.5rem',
                        background: '#ef4444',
                        color: 'white'
                      }}
                    >
                      {deletingId === serviceType.id ? 'Deleting...' : '🗑️ Delete'}
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

