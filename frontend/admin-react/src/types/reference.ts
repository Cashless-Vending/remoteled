/**
 * Reference Data Types
 * These types represent reference/lookup data for devices and services
 */

export interface DeviceModel {
  id: string
  name: string
  description?: string
  created_at: string
}

export interface DeviceModelCreate {
  name: string
  description?: string
}

export interface DeviceModelUpdate {
  name?: string
  description?: string
}

export interface Location {
  id: string
  name: string
  description?: string
  created_at: string
}

export interface LocationCreate {
  name: string
  description?: string
}

export interface LocationUpdate {
  name?: string
  description?: string
}

export interface ServiceType {
  id: string
  name: string
  code: string
  description?: string
  created_at: string
}

export interface ServiceTypeCreate {
  name: string
  code: string
  description?: string
}

export interface ServiceTypeUpdate {
  name?: string
  code?: string
  description?: string
}

