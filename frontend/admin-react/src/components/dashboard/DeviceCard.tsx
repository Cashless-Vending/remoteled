import { Device } from '../../types'

interface DeviceCardProps {
  device: Device
  onEdit: (device: Device) => void
  onDelete: (id: string, label: string) => void
}

export const DeviceCard = ({ device, onEdit, onDelete }: DeviceCardProps) => {
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

