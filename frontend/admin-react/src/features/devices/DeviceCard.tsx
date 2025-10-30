/**
 * Device Card Component
 */
import { Badge } from '../../components/Badge';
import { Button } from '../../components/Button';
import { truncateId } from '../../core/utils';
import type { Device } from '../../core/types';

interface DeviceCardProps {
  device: Device;
  onTestCycle?: (id: string) => void;
  onTroubleshoot?: (id: string) => void;
}

export const DeviceCard = ({ device, onTestCycle, onTroubleshoot }: DeviceCardProps) => {
  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-5 hover:border-primary-500 hover:shadow-lg transition-all">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg">{device.label}</h3>
          <p className="text-xs text-gray-500 mt-1">ID: {truncateId(device.id)}</p>
        </div>
        <Badge variant={device.status}>{device.status}</Badge>
      </div>

      {/* Device Info */}
      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <p>📍 {device.location || 'No location set'}</p>
        <p>🔧 GPIO Pin: {device.gpio_pin ?? 'Not configured'}</p>
        <p>
          📊 {device.active_service_count || 0} Active Products ({device.service_count || 0} total)
        </p>
        <p>
          ✅ {device.completed_orders || 0} / {device.total_orders || 0} orders completed
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {device.status === 'ACTIVE' ? (
          <Button
            size="sm"
            variant="success"
            onClick={() => onTestCycle?.(device.id)}
            className="flex-1"
          >
            Test Cycle
          </Button>
        ) : (
          <Button
            size="sm"
            variant="danger"
            onClick={() => onTroubleshoot?.(device.id)}
            className="flex-1"
          >
            Troubleshoot
          </Button>
        )}
      </div>
    </div>
  );
};


