import { useMemo, memo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Order } from '../../types'

interface OrderTrendsChartProps {
  orders: Order[]
}

interface ChartDataPoint {
  date: string
  total: number
  done: number
  paid: number
  running: number
  failed: number
}

const OrderTrendsChartComponent = ({ orders }: OrderTrendsChartProps) => {
  const safeOrders = orders || []
  
  const chartData = useMemo(() => {
    // Group orders by hour
    const groupedByHour: Record<string, { total: number; done: number; paid: number; running: number; failed: number; timestamp: number }> = {}

    safeOrders.forEach(order => {
      const orderDate = new Date(order.created_at)
      // Format as "Nov 3, 10:00 AM"
      const hourKey = orderDate.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        hour12: true
      })
      
      if (!groupedByHour[hourKey]) {
        groupedByHour[hourKey] = { 
          total: 0, 
          done: 0, 
          paid: 0, 
          running: 0, 
          failed: 0,
          timestamp: orderDate.getTime()
        }
      }
      
      groupedByHour[hourKey].total += 1
      
      const status = order.status.toLowerCase()
      if (status === 'done') {
        groupedByHour[hourKey].done += 1
      } else if (status === 'paid') {
        groupedByHour[hourKey].paid += 1
      } else if (status === 'running') {
        groupedByHour[hourKey].running += 1
      } else if (status === 'failed') {
        groupedByHour[hourKey].failed += 1
      }
    })

    // Convert to array and sort by timestamp
    const dataPoints: ChartDataPoint[] = Object.entries(groupedByHour).map(([date, counts]) => ({
      date,
      total: counts.total,
      done: counts.done,
      paid: counts.paid,
      running: counts.running,
      failed: counts.failed
    }))

    // Sort by timestamp
    return dataPoints.sort((a, b) => {
      const timestampA = groupedByHour[a.date].timestamp
      const timestampB = groupedByHour[b.date].timestamp
      return timestampA - timestampB
    })
  }, [safeOrders])

  if (safeOrders.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-title">Order Trends</div>
        </div>
        <div style={{ padding: '3rem', textAlign: 'center', color: '#718096' }}>
          No order data available yet.
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Order Trends</div>
        <p style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.25rem' }}>
          Order volume by date and status
        </p>
      </div>
      <div style={{ padding: '1.5rem' }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="date" 
              stroke="#718096"
              style={{ fontSize: '0.75rem' }}
            />
            <YAxis 
              stroke="#718096"
              style={{ fontSize: '0.75rem' }}
              allowDecimals={false}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '0.875rem' }}
            />
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#4299e1" 
              strokeWidth={2}
              name="Total Orders"
              dot={{ fill: '#4299e1', r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="done" 
              stroke="#48bb78" 
              strokeWidth={2}
              name="Completed"
              dot={{ fill: '#48bb78', r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="paid" 
              stroke="#9f7aea" 
              strokeWidth={2}
              name="Paid"
              dot={{ fill: '#9f7aea', r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="running" 
              stroke="#ed8936" 
              strokeWidth={2}
              name="Running"
              dot={{ fill: '#ed8936', r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Memoize to prevent unnecessary re-renders
export const OrderTrendsChart = memo(OrderTrendsChartComponent)

