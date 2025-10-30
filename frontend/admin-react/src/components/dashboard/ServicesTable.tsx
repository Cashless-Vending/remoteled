import { Service } from '../../types'
import { formatCurrency } from '../../utils/format'

interface ServicesTableProps {
  services: Service[]
  onEdit: (service: Service) => void
  onDelete: (id: string, type: string) => void
  onAddNew: () => void
}

export const ServicesTable = ({ services, onEdit, onDelete, onAddNew }: ServicesTableProps) => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Product Catalog</div>
        <button className="btn btn-primary" onClick={onAddNew}>
          + Add Product
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Device</th>
            <th>Type</th>
            <th>Price</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {services.map(service => (
            <tr key={service.id}>
              <td>{service.device_label}</td>
              <td>{service.type}</td>
              <td>{formatCurrency(service.price_cents)}</td>
              <td>
                {service.fixed_minutes 
                  ? `${service.fixed_minutes} min` 
                  : (service.minutes_per_25c 
                      ? `${service.minutes_per_25c} min/$0.25` 
                      : '2 sec')}
              </td>
              <td>
                <span className={`badge ${service.active ? 'ACTIVE' : 'OFFLINE'}`}>
                  {service.active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    className="btn btn-sm" 
                    onClick={() => onEdit(service)}
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                  >
                    ✏️ Edit
                  </button>
                  <button 
                    className="btn btn-sm" 
                    onClick={() => onDelete(service.id, service.type)}
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', background: '#ef4444', color: 'white' }}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

