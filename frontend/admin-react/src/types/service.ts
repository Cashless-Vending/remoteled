export interface Service {
  id: string
  device_id: string
  device_label: string
  type: 'TRIGGER' | 'FIXED' | 'VARIABLE'
  price_cents: number
  fixed_minutes: number | null
  minutes_per_25c: number | null
  active: boolean
}

export interface ServiceCreateRequest {
  device_id: string
  type: 'TRIGGER' | 'FIXED' | 'VARIABLE'
  price_cents: number
  fixed_minutes?: number
  minutes_per_25c?: number
  active: boolean
}

export interface ServiceUpdateRequest {
  device_id: string
  type: 'TRIGGER' | 'FIXED' | 'VARIABLE'
  price_cents: number
  fixed_minutes?: number
  minutes_per_25c?: number
  active: boolean
}

