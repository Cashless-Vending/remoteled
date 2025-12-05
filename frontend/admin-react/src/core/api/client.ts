/**
 * API Client for RemoteLED Admin Console
 * Axios instance with authentication and error handling
 */
import axios from 'axios';
import type { AxiosError, AxiosInstance } from 'axios';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  Device,
  DeviceCreateRequest,
  DeviceUpdateRequest,
  Service,
  ServiceCreateRequest,
  ServiceUpdateRequest,
  Order,
  Log,
  DashboardStats,
  OrdersChartData,
  DeviceStatusData,
} from '../types';

// API Base URL - auto-detect environment
const getApiBaseUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Development: direct to backend
  if (import.meta.env.DEV) {
    return 'http://localhost:9999';
  }
  
  // Production: use nginx proxy
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Create axios instance with default configuration
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // For cookies
  });

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Token expired - clear auth and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

const apiClient = createApiClient();

// ============================================================
// Auth API
// ============================================================

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// ============================================================
// Dashboard/Stats API
// ============================================================

export const statsApi = {
  getOverview: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/admin/stats/overview');
    return response.data;
  },

  getOrdersLast7Days: async (): Promise<OrdersChartData[]> => {
    const response = await apiClient.get<OrdersChartData[]>('/admin/stats/orders-last-7-days');
    return response.data;
  },

  getDeviceStatus: async (): Promise<DeviceStatusData[]> => {
    const response = await apiClient.get<DeviceStatusData[]>('/admin/stats/device-status');
    return response.data;
  },
};

// ============================================================
// Devices API
// ============================================================

export const devicesApi = {
  getAll: async (): Promise<Device[]> => {
    const response = await apiClient.get<Device[]>('/admin/devices/all');
    return response.data;
  },

  getById: async (id: string): Promise<Device> => {
    const response = await apiClient.get<Device>(`/admin/devices/${id}`);
    return response.data;
  },

  create: async (data: DeviceCreateRequest): Promise<Device> => {
    const response = await apiClient.post<Device>('/admin/devices', data);
    return response.data;
  },

  update: async (id: string, data: DeviceUpdateRequest): Promise<Device> => {
    const response = await apiClient.put<Device>(`/admin/devices/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/devices/${id}`);
  },
};

// ============================================================
// Services/Products API
// ============================================================

export const servicesApi = {
  getAll: async (): Promise<Service[]> => {
    const response = await apiClient.get<Service[]>('/admin/services/all');
    return response.data;
  },

  getById: async (id: string): Promise<Service> => {
    const response = await apiClient.get<Service>(`/admin/services/${id}`);
    return response.data;
  },

  create: async (data: ServiceCreateRequest): Promise<Service> => {
    const response = await apiClient.post<Service>('/admin/services', data);
    return response.data;
  },

  update: async (id: string, data: ServiceUpdateRequest): Promise<Service> => {
    const response = await apiClient.put<Service>(`/admin/services/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/services/${id}`);
  },
};

// ============================================================
// Orders API
// ============================================================

export const ordersApi = {
  getRecent: async (limit = 20): Promise<Order[]> => {
    const response = await apiClient.get<Order[]>(`/admin/orders/recent?limit=${limit}`);
    return response.data;
  },

  getById: async (id: string): Promise<Order> => {
    const response = await apiClient.get<Order>(`/admin/orders/${id}`);
    return response.data;
  },
};

// ============================================================
// Logs API
// ============================================================

export const logsApi = {
  getRecent: async (errorOnly = false, limit = 50): Promise<Log[]> => {
    const response = await apiClient.get<Log[]>(
      `/admin/logs/recent?error_only=${errorOnly}&limit=${limit}`
    );
    return response.data;
  },
};

export default apiClient;

