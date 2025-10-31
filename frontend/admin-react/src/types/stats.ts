export interface Stats {
  revenue_today_cents: number
  total_devices: number
  active_orders: number
  new_devices_this_month: number
}

export interface Order {
  id: string
  device_label: string
  product_type: string
  amount_cents: number
  status: string
  created_at: string
}

