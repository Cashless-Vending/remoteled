export interface Service {
  id: string
  type: 'TRIGGER' | 'FIXED' | 'VARIABLE'
  price_cents: number
  fixed_minutes: number | null
  minutes_per_25c: number | null
  active: boolean
  assigned_device_count?: number
  device_labels?: string[]
}

export interface ServiceCreateRequest {
  type: 'TRIGGER' | 'FIXED' | 'VARIABLE'
  price_cents: number
  fixed_minutes?: number
  minutes_per_25c?: number
  active: boolean
}

export interface ServiceUpdateRequest {
  price_cents?: number
  fixed_minutes?: number
  minutes_per_25c?: number
  active?: boolean
}

