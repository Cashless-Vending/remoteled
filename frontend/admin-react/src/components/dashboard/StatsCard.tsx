interface StatsCardProps {
  label: string
  value: string | number
  color: 'blue' | 'green' | 'purple' | 'orange'
}

export const StatsCard = ({ label, value, color }: StatsCardProps) => {
  return (
    <div className={`stat-card ${color}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  )
}

