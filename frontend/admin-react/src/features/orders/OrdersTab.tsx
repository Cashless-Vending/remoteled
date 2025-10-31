/**
 * Orders Management Tab
 */
import { useEffect } from 'react';
import { Button } from '../../components/Button';
import { Badge } from '../../components/Badge';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { useOrders } from './useOrders';
import { useApp } from '../../context/AppContext';
import { formatCurrency, truncateId, formatDateTime, exportToCSV } from '../../core/utils';

export const OrdersTab = () => {
  const { orders, isLoading, fetchOrders } = useOrders();
  const { showNotification } = useApp();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleExportCSV = () => {
    const csvData = orders.map((order) => ({
      'Order ID': order.id,
      Device: order.device_label || 'N/A',
      'Product Type': order.product_type || 'N/A',
      Amount: formatCurrency(order.amount_cents),
      Duration: order.authorized_minutes > 0 ? `${order.authorized_minutes} min` : '2 sec',
      Status: order.status,
      Timestamp: formatDateTime(order.created_at),
    }));

    exportToCSV(csvData, 'orders');
    showNotification('success', 'CSV exported successfully!');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Recent Orders</h2>
          <p className="text-gray-600 mt-1">View order history and export data</p>
        </div>
        <Button variant="primary" size="sm" onClick={handleExportCSV}>
          Export CSV
        </Button>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {orders.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-400 text-lg">No orders found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Order ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Device
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Product Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {truncateId(order.id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.device_label || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.product_type || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(order.amount_cents)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.authorized_minutes > 0 ? `${order.authorized_minutes} min` : '2 sec'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={order.status}>{order.status}</Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDateTime(order.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};


