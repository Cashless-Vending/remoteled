/**
 * TypeScript types and interfaces for RemoteLED Admin Console
 */

// ============================================================
// Auth Types
// ============================================================

export interface User {
  id: string;
  email: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ============================================================
// Device Types
// ============================================================

export type DeviceStatus = 'ACTIVE' | 'OFFLINE' | 'MAINTENANCE' | 'DEACTIVATED';

export interface Device {
  id: string;
  label: string;
  public_key: string;
  model?: string;
  location?: string;
  gpio_pin?: number;
  status: DeviceStatus;
  created_at: string;
  updated_at: string;
  service_count?: number;
  active_service_count?: number;
  total_orders?: number;
  completed_orders?: number;
}

export interface DeviceCreateRequest {
  label: string;
  public_key: string;
  model?: string;
  location?: string;
  gpio_pin?: number;
}

export interface DeviceUpdateRequest {
  label?: string;
  location?: string;
  gpio_pin?: number;
  status?: DeviceStatus;
}

// ============================================================
// Service/Product Types
// ============================================================

export type ServiceType = 'TRIGGER' | 'FIXED' | 'VARIABLE';

export interface Service {
  id: string;
  device_id: string;
  device_label?: string;
  type: ServiceType;
  price_cents: number;
  fixed_minutes?: number;
  minutes_per_25c?: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceCreateRequest {
  device_id: string;
  type: ServiceType;
  price_cents: number;
  fixed_minutes?: number;
  minutes_per_25c?: number;
  active?: boolean;
}

export interface ServiceUpdateRequest {
  price_cents?: number;
  fixed_minutes?: number;
  minutes_per_25c?: number;
  active?: boolean;
}

// ============================================================
// Order Types
// ============================================================

export type OrderStatus = 'CREATED' | 'PAID' | 'RUNNING' | 'DONE' | 'FAILED';

export interface Order {
  id: string;
  device_id: string;
  device_label?: string;
  product_id: string;
  product_type?: ServiceType;
  amount_cents: number;
  authorized_minutes: number;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
}

// ============================================================
// Log Types
// ============================================================

export type LogDirection = 'PI_TO_SRV' | 'SRV_TO_PI';

export interface Log {
  id: string;
  device_id: string;
  device_label?: string;
  direction: LogDirection;
  payload_hash?: string;
  ok: boolean;
  details?: string;
  created_at: string;
}

// ============================================================
// Stats Types
// ============================================================

export interface DashboardStats {
  total_devices: number;
  new_devices_this_month: number;
  active_orders: number;
  orders_change_percent: number;
  revenue_today_cents: number;
  revenue_change_percent: number;
  success_rate: number;
  success_rate_change: number;
}

export interface OrdersChartData {
  day_name: string;
  order_count: number;
}

export interface DeviceStatusData {
  status: DeviceStatus;
  count: number;
}

// ============================================================
// API Response Types
// ============================================================

export interface ApiError {
  detail: string;
  status_code?: number;
}

