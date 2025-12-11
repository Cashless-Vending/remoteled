export interface Stats {
  revenue_today_cents: number
  total_devices: number
  active_orders: number
  new_devices_this_month: number
}

export interface Order {
  id: string
  device_id?: string
  device_label: string
  device_location?: string
  service_id?: string
  service_type: string
  service_price?: number
  product_type?: string  // Legacy field
  amount_cents: number
  authorized_minutes: number
  status: string
  created_at: string
  updated_at?: string
  order_category?: 'active' | 'recent_complete' | 'recent_failed' | 'historical'
}
