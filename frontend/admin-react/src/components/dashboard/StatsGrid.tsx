import { Stats, Device } from '../../types'
import { formatCurrency } from '../../utils/format'
import { StatsCard } from './StatsCard'

interface StatsGridProps {
  stats: Stats | null
  devices: Device[]
}

export const StatsGrid = ({ stats, devices }: StatsGridProps) => {
  const activeDevices = devices.filter(d => d.status === 'ACTIVE').length

  return (
    <div className="stats-grid">
      <StatsCard 
        label="Total Revenue" 
        value={formatCurrency(stats?.revenue_today_cents)}
        color="blue"
      />
      <StatsCard 
        label="Active Devices" 
        value={activeDevices}
        color="green"
      />
      <StatsCard 
        label="Total Devices" 
        value={stats?.total_devices || devices.length}
        color="purple"
      />
      <StatsCard 
        label="Total Orders" 
        value={stats?.active_orders || 0}
        color="orange"
      />
    </div>
  )
}

