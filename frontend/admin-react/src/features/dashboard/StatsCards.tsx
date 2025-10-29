/**
 * Dashboard Statistics Cards
 */
import type { DashboardStats } from '../../core/types';
import { formatCurrency, getChangeSymbol } from '../../core/utils';

interface StatsCardsProps {
  stats: DashboardStats | null;
}

export const StatsCards = ({ stats }: StatsCardsProps) => {
  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-sm animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: 'Total Devices',
      value: stats.total_devices,
      change: stats.new_devices_this_month,
      changeText: `${getChangeSymbol(stats.new_devices_this_month)} ${stats.new_devices_this_month} this month`,
      color: 'blue',
      borderColor: 'border-blue-500',
    },
    {
      label: 'Active Orders',
      value: stats.active_orders,
      change: stats.orders_change_percent,
      changeText: `${getChangeSymbol(stats.orders_change_percent)} ${Math.abs(stats.orders_change_percent).toFixed(1)}% vs last week`,
      color: 'green',
      borderColor: 'border-green-500',
    },
    {
      label: 'Revenue Today',
      value: formatCurrency(stats.revenue_today_cents),
      change: stats.revenue_change_percent,
      changeText: `${getChangeSymbol(stats.revenue_change_percent)} ${Math.abs(stats.revenue_change_percent).toFixed(1)}% vs yesterday`,
      color: 'purple',
      borderColor: 'border-purple-500',
    },
    {
      label: 'Success Rate',
      value: `${stats.success_rate}%`,
      change: stats.success_rate_change,
      changeText: `${getChangeSymbol(stats.success_rate_change)} ${Math.abs(stats.success_rate_change).toFixed(1)}% this week`,
      color: 'orange',
      borderColor: 'border-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`bg-white rounded-xl p-6 shadow-sm border-l-4 ${card.borderColor} hover:shadow-md transition-shadow`}
        >
          <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            {card.label}
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">{card.value}</div>
          <div
            className={`text-sm ${
              card.change >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {card.changeText}
          </div>
        </div>
      ))}
    </div>
  );
};


