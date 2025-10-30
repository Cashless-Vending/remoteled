/**
 * Custom hook for orders management
 */
import { useState, useCallback } from 'react';
import { ordersApi } from '../../core/api/client';
import type { Order } from '../../core/types';

export const useOrders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async (limit = 20) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await ordersApi.getRecent(limit);
      setOrders(data);
    } catch (err: any) {
      console.error('Error fetching orders:', err);
      setError(err.response?.data?.detail || 'Failed to load orders');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    orders,
    isLoading,
    error,
    fetchOrders,
  };
};


