/**
 * Main Dashboard Page with Tabs
 */
import { useState } from 'react';
import { Tab } from '@headlessui/react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/Button';
import { StatsCards } from './StatsCards';
import { OrdersChart } from './OrdersChart';
import { DeviceStatusChart } from './DeviceStatusChart';
import { useDashboard } from './useDashboard';
import { DevicesTab } from '../devices/DevicesTab';
import { ProductsTab } from '../products/ProductsTab';
import { OrdersTab } from '../orders/OrdersTab';
import { LogsTab } from '../logs/LogsTab';

export const DashboardPage = () => {
  const { user, logout } = useAuth();
  const { stats, ordersChart, deviceStatus, isLoading } = useDashboard();
  const [selectedIndex, setSelectedIndex] = useState(0);

  const tabs = [
    { name: 'Dashboard', component: null },
    { name: 'Devices', component: DevicesTab },
    { name: 'Products', component: ProductsTab },
    { name: 'Orders', component: OrdersTab },
    { name: 'Logs', component: LogsTab },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">RemoteLED Admin Console</h1>
              <p className="text-sm opacity-90 mt-1">Monitor and manage your cashless vending devices</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm opacity-90">Logged in as</p>
                <p className="font-medium">{user?.email}</p>
              </div>
              <Button
                onClick={logout}
                variant="secondary"
                size="sm"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
          {/* Tab Navigation */}
          <Tab.List className="flex space-x-1 bg-white rounded-xl p-1 shadow-sm mb-8">
            {tabs.map((tab) => (
              <Tab
                key={tab.name}
                className={({ selected }) =>
                  `w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all
                  ${
                    selected
                      ? 'bg-primary-500 text-white shadow'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                {tab.name}
              </Tab>
            ))}
          </Tab.List>

          {/* Tab Panels */}
          <Tab.Panels>
            {/* Dashboard Overview Tab */}
            <Tab.Panel>
              <StatsCards stats={stats} />
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Orders Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Orders Last 7 Days
                  </h3>
                  {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                    </div>
                  ) : (
                    <OrdersChart data={ordersChart} />
                  )}
                </div>

                {/* Device Status Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Device Status Distribution
                  </h3>
                  {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                    </div>
                  ) : (
                    <DeviceStatusChart data={deviceStatus} />
                  )}
                </div>
              </div>
            </Tab.Panel>

            {/* Other Tabs */}
            {tabs.slice(1).map((tab) => (
              <Tab.Panel key={tab.name}>
                {tab.component && <tab.component />}
              </Tab.Panel>
            ))}
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
};


