import { Order } from '../../types'
import { formatCurrency, formatDateTime } from '../../utils/format'

interface OrdersTableProps {
  orders: Order[]
  onExportCSV: () => void
}

export const OrdersTable = ({ orders, onExportCSV }: OrdersTableProps) => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Recent Orders</div>
        <button className="btn btn-primary btn-sm" onClick={onExportCSV}>
          Export CSV
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Device</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => (
            <tr key={order.id}>
              <td>{order.id.substring(0, 8)}...</td>
              <td>{order.device_label}</td>
              <td>{order.product_type}</td>
              <td>{formatCurrency(order.amount_cents)}</td>
              <td>
                <span className={`badge ${order.status}`}>{order.status}</span>
              </td>
              <td>{formatDateTime(order.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

