/**
 * Application Context Provider
 * Manages global application state (notifications, modals, etc.)
 */
import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface AppContextType {
  notifications: Notification[];
  showNotification: (type: Notification['type'], message: string) => void;
  dismissNotification: (id: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider = ({ children }: AppProviderProps) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const showNotification = useCallback((type: Notification['type'], message: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    const notification: Notification = { id, type, message };
    
    setNotifications((prev) => [...prev, notification]);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
      dismissNotification(id);
    }, 3000);
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const value = {
    notifications,
    showNotification,
    dismissNotification,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

