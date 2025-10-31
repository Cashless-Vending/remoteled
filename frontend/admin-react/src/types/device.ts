export interface Device {
  id: string
  label: string
  status: string
  location: string
  model: string
  gpio_pin: number
}

export interface DeviceCreateRequest {
  label: string
  public_key: string
  model: string
  location: string
  gpio_pin: number
}

export interface DeviceUpdateRequest {
  label: string
  model: string
  location: string
  gpio_pin: number
  status: string
}

