/**
 * Orders Last 7 Days Chart Component
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { OrdersChartData } from '../../core/types';

interface OrdersChartProps {
  data: OrdersChartData[];
}

export const OrdersChart = ({ data }: OrdersChartProps) => {
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
          dataKey="day_name" 
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
        <Bar 
          dataKey="order_count" 
          fill="url(#colorGradient)" 
          radius={[8, 8, 0, 0]}
        />
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#667eea" stopOpacity={1} />
            <stop offset="100%" stopColor="#764ba2" stopOpacity={1} />
          </linearGradient>
        </defs>
      </BarChart>
    </ResponsiveContainer>
  );
};


