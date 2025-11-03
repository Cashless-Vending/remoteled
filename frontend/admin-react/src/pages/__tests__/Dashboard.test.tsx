import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { Dashboard } from '../Dashboard'

const sampleDevice = {
  id: 'device-1',
  label: 'Lobby Display',
  status: 'ACTIVE',
  location: 'Lobby',
  model: 'RPi 4 Model B',
  gpio_pin: 17
}

const sampleService = {
  id: 'service-1',
  device_id: 'device-1',
  device_label: 'Lobby Display',
  type: 'TRIGGER' as const,
  price_cents: 100,
  fixed_minutes: null,
  minutes_per_25c: null,
  active: true
}

const sampleStats = {
  revenue_today_cents: 1250,
  total_devices: 4,
  active_orders: 2,
  new_devices_this_month: 1
}

const sampleOrder = {
  id: 'order-1',
  device_label: 'Lobby Display',
  product_type: 'TRIGGER',
  amount_cents: 250,
  status: 'PAID',
  created_at: new Date().toISOString()
}

const sampleLogs = [
  {
    id: 'log-1',
    direction: 'IN',
    ok: true,
    details: 'Device heartbeat received',
    created_at: new Date().toISOString(),
    device_id: 'device-1',
    device_label: 'Lobby Display'
  }
]

const createDeviceMock = vi.fn()
const updateDeviceMock = vi.fn()
const deleteDeviceMock = vi.fn()
const createServiceMock = vi.fn()
const updateServiceMock = vi.fn()
const deleteServiceMock = vi.fn()
const refreshLogsMock = vi.fn()

const logoutMock = vi.fn()

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { email: 'admin@example.com' },
    logout: logoutMock,
    loading: false
  })
}))

vi.mock('../../hooks', () => ({
  useDevices: () => ({
    devices: [sampleDevice],
    loading: false,
    createDevice: createDeviceMock,
    updateDevice: updateDeviceMock,
    deleteDevice: deleteDeviceMock,
    error: null
  }),
  useServices: () => ({
    services: [sampleService],
    loading: false,
    createService: createServiceMock,
    updateService: updateServiceMock,
    deleteService: deleteServiceMock,
    error: null
  }),
  useStats: () => ({
    stats: sampleStats,
    orders: [sampleOrder],
    loading: false,
    error: null
  }),
  useLogs: () => ({
    logs: sampleLogs,
    loading: false,
    error: null,
    refetch: refreshLogsMock
  })
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    createDeviceMock.mockImplementation(async (payload) => ({
      id: 'device-2',
      label: payload.label,
      status: 'ACTIVE',
      location: payload.location,
      model: payload.model,
      gpio_pin: payload.gpio_pin
    }))
  })

  it('renders overview by default and switches views', async () => {
    const user = userEvent.setup()

    render(<Dashboard />)

    expect(screen.getByRole('button', { name: /Overview/i })).toHaveClass('is-active')
    expect(screen.getByText('Registered Devices')).toBeInTheDocument()
    expect(screen.queryByText('Product Catalog')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Products/i }))
    expect(screen.getByText('Product Catalog')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Logs/i }))
    expect(screen.getByText('System Logs')).toBeInTheDocument()
  })

  it('submits new device and shows success feedback', async () => {
    const user = userEvent.setup()

    render(<Dashboard />)

    await user.click(screen.getByRole('button', { name: /Devices/i }))
    await user.click(screen.getByRole('button', { name: /\+ Add New Device/i }))

    const labelInput = screen.getByLabelText('Device Label *')
    await user.clear(labelInput)
    await user.type(labelInput, 'Test Suite Device')

    const publicKeyInput = screen.getByLabelText('Public Key *')
    await user.clear(publicKeyInput)
    await user.type(publicKeyInput, 'TEST-KEY')

    await user.click(screen.getByRole('button', { name: /Create Device/i }))

    await waitFor(() => expect(createDeviceMock).toHaveBeenCalled())
    expect(createDeviceMock).toHaveBeenCalledWith({
      label: 'Test Suite Device',
      public_key: 'TEST-KEY',
      model: 'RPi 4 Model B',
      location: 'Building 1',
      gpio_pin: 17
    })

    await waitFor(() => expect(screen.getByText('Device "Test Suite Device" created.')).toBeInTheDocument())
    expect(refreshLogsMock).toHaveBeenCalled()
  })
})


