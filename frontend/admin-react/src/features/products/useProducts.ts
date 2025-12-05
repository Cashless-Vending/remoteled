/**
 * Custom hook for service management
 */
import { useState, useCallback } from 'react';
import { servicesApi } from '../../core/api/client';
import type { Service, ServiceCreateRequest, ServiceUpdateRequest } from '../../core/types';

export const useProducts = () => {
  const [products, setProducts] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await servicesApi.getAll();
      setProducts(data);
    } catch (err: any) {
      console.error('Error fetching products:', err);
      setError(err.response?.data?.detail || 'Failed to load products');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createProduct = useCallback(async (data: ServiceCreateRequest): Promise<Service> => {
    const service = await servicesApi.create(data);
    await fetchProducts();
    return service;
  }, [fetchProducts]);

  const updateProduct = useCallback(async (id: string, data: ServiceUpdateRequest): Promise<Service> => {
    const service = await servicesApi.update(id, data);
    await fetchProducts();
    return service;
  }, [fetchProducts]);

  const deleteProduct = useCallback(async (id: string): Promise<void> => {
    await servicesApi.delete(id);
    await fetchProducts();
  }, [fetchProducts]);

  return {
    products,
    isLoading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
  };
};


