import { useState } from 'react'
import type { Location } from '../../types/reference'
import { formatDateTime } from '../../utils/format'

interface LocationsTableProps {
  locations: Location[]
  onAdd: () => void
  onEdit: (location: Location) => void
  onDelete: (locationId: string) => void
}

export const LocationsTable = ({ locations, onAdd, onEdit, onDelete }: LocationsTableProps) => {
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const safeLocations = locations || []

  const handleDelete = async (locationId: string) => {
    if (!window.confirm('Are you sure you want to delete this location?')) {
      return
    }
    setDeletingId(locationId)
    try {
      await onDelete(locationId)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Locations</div>
        <button className="btn btn-primary btn-sm" onClick={onAdd}>
          + Add Location
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
          {safeLocations.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                No locations found. Add your first location to get started.
              </td>
            </tr>
          ) : (
            safeLocations.map(location => (
              <tr key={location.id}>
                <td>{location.name}</td>
                <td>{location.description || '-'}</td>
                <td>{formatDateTime(location.created_at)}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-sm"
                      onClick={() => onEdit(location)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(location.id)}
                      disabled={deletingId === location.id}
                    >
                      {deletingId === location.id ? 'Deleting...' : 'Delete'}
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

