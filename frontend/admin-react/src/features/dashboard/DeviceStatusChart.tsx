/**
 * Device Status Distribution Chart Component
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { DeviceStatusData } from '../../core/types';

interface DeviceStatusChartProps {
  data: DeviceStatusData[];
}

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: '#48bb78',
  OFFLINE: '#f56565',
  MAINTENANCE: '#ed8936',
  DEACTIVATED: '#718096',
};

export const DeviceStatusChart = ({ data }: DeviceStatusChartProps) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="status" 
          stroke="#6b7280" 
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#6b7280" 
          style={{ fontSize: '12px' }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Bar dataKey="count" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.status] || '#718096'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};


