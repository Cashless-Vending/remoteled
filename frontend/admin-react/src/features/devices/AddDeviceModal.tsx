/**
 * Add Device Modal Component
 */
import { useState } from 'react';
import type { FormEvent } from 'react';
import { Modal } from '../../components/Modal';
import { Input } from '../../components/Input';
import { Textarea } from '../../components/Textarea';
import { Button } from '../../components/Button';
import { useApp } from '../../context/AppContext';
import { useDevices } from './useDevices';

interface AddDeviceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AddDeviceModal = ({ isOpen, onClose }: AddDeviceModalProps) => {
  const { createDevice } = useDevices();
  const { showNotification } = useApp();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    label: '',
    public_key: '',
    model: '',
    location: '',
    gpio_pin: '',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await createDevice({
        label: formData.label,
        public_key: formData.public_key,
        model: formData.model || undefined,
        location: formData.location || undefined,
        gpio_pin: formData.gpio_pin ? parseInt(formData.gpio_pin) : undefined,
      });

      showNotification('success', 'Device added successfully!');
      onClose();
      
      // Reset form
      setFormData({
        label: '',
        public_key: '',
        model: '',
        location: '',
        gpio_pin: '',
      });
    } catch (error: any) {
      showNotification('error', error.response?.data?.detail || 'Failed to add device');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add New Device"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Adding...' : 'Add Device'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Device Label"
          name="label"
          value={formData.label}
          onChange={handleChange}
          placeholder="e.g., Massage Chair #7"
          helperText="A friendly name for this device"
          required
        />

        <Textarea
          label="Public Key"
          name="public_key"
          value={formData.public_key}
          onChange={handleChange}
          placeholder="ECDSA public key"
          helperText="ECDSA public key for signature verification"
          required
        />

        <Input
          label="Model"
          name="model"
          value={formData.model}
          onChange={handleChange}
          placeholder="e.g., Raspberry Pi 4"
        />

        <Input
          label="Location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="e.g., Main Lobby"
        />

        <Input
          label="GPIO Pin"
          name="gpio_pin"
          type="number"
          value={formData.gpio_pin}
          onChange={handleChange}
          placeholder="e.g., 23"
          helperText="GPIO pin number for relay/LED control (0-40)"
          min="0"
          max="40"
        />
      </form>
    </Modal>
  );
};

