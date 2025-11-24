import { Device } from '../../types'
import { DeviceCard } from './DeviceCard'

interface DeviceGridProps {
  devices: Device[]
  onEdit: (device: Device) => void
  onDelete: (id: string, label: string) => void
  onAddNew: () => void
}

export const DeviceGrid = ({ devices, onEdit, onDelete, onAddNew }: DeviceGridProps) => {
  const safeDevices = devices || []
  
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Registered Devices</div>
        <button className="btn btn-primary" onClick={onAddNew}>
          + Add New Device
        </button>
      </div>
      <div className="device-grid">
        {safeDevices.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#718096' }}>
            No devices found. Add your first device to get started.
          </div>
        ) : (
          safeDevices.map(device => (
            <DeviceCard 
              key={device.id}
              device={device}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))
        )}
      </div>
    </div>
  )
}

