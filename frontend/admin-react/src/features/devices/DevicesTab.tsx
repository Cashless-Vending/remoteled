/**
 * Devices Management Tab
 */
import { useEffect, useState } from 'react';
import { Button } from '../../components/Button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { useApp } from '../../context/AppContext';
import { useDevices } from './useDevices';
import { DeviceCard } from './DeviceCard';
import { AddDeviceModal } from './AddDeviceModal';
import { truncateId } from '../../core/utils';

export const DevicesTab = () => {
  const { devices, isLoading, fetchDevices } = useDevices();
  const { showNotification } = useApp();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const handleTestCycle = (id: string) => {
    showNotification('success', `Test cycle initiated for device ${truncateId(id)}`);
  };

  const handleTroubleshoot = (id: string) => {
    showNotification('info', `Troubleshooting mode for device ${truncateId(id)}`);
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
          <h2 className="text-2xl font-bold text-gray-900">Registered Devices</h2>
          <p className="text-gray-600 mt-1">Manage your IoT devices and their configurations</p>
        </div>
        <Button variant="primary" onClick={() => setIsAddModalOpen(true)}>
          + Add New Device
        </Button>
      </div>

      {/* Device Grid */}
      {devices.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <p className="text-gray-400 text-lg">No devices found</p>
          <p className="text-gray-500 text-sm mt-2">Add your first device to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device) => (
            <DeviceCard
              key={device.id}
              device={device}
              onTestCycle={handleTestCycle}
              onTroubleshoot={handleTroubleshoot}
            />
          ))}
        </div>
      )}

      {/* Add Device Modal */}
      <AddDeviceModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />
    </div>
  );
};


