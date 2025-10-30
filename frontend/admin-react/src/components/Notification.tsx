/**
 * Toast Notification Component
 */
import { useEffect } from 'react';
import { Transition } from '@headlessui/react';
import type { Notification as NotificationType } from '../context/AppContext';

interface NotificationProps {
  notification: NotificationType;
  onDismiss: (id: string) => void;
}

export const Notification = ({ notification, onDismiss }: NotificationProps) => {
  const { id, type, message } = notification;

  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(id);
    }, 3000);

    return () => clearTimeout(timer);
  }, [id, onDismiss]);

  const typeStyles = {
    success: 'bg-green-50 border-green-500 text-green-800',
    error: 'bg-red-50 border-red-500 text-red-800',
    warning: 'bg-orange-50 border-orange-500 text-orange-800',
    info: 'bg-blue-50 border-blue-500 text-blue-800',
  };

  const icons = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <Transition
      appear
      show={true}
      enter="transition-all duration-300 ease-out"
      enterFrom="transform translate-x-full opacity-0"
      enterTo="transform translate-x-0 opacity-100"
      leave="transition-all duration-200 ease-in"
      leaveFrom="transform translate-x-0 opacity-100"
      leaveTo="transform translate-x-full opacity-0"
    >
      <div
        className={`flex items-center gap-3 p-4 mb-3 rounded-lg shadow-lg border-l-4 ${typeStyles[type]}`}
        role="alert"
      >
        <div className="flex-shrink-0 text-xl">{icons[type]}</div>
        <div className="flex-1 text-sm font-medium">{message}</div>
        <button
          onClick={() => onDismiss(id)}
          className="flex-shrink-0 text-xl opacity-50 hover:opacity-100 focus:outline-none"
        >
          &times;
        </button>
      </div>
    </Transition>
  );
};

/**
 * Container for all notifications
 */
interface NotificationContainerProps {
  notifications: NotificationType[];
  onDismiss: (id: string) => void;
}

export const NotificationContainer = ({
  notifications,
  onDismiss,
}: NotificationContainerProps) => {
  return (
    <div className="fixed top-5 right-5 z-50 w-96 max-w-full">
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
};

