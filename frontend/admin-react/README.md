# RemoteLED Admin Console (React)

Modern React + TypeScript admin console for managing RemoteLED cashless vending devices.

## Features

- 🔐 JWT + Session Cookie Authentication
- 📊 Real-time Dashboard with Statistics
- 🖥️ Device Management (CRUD operations)
- 🏷️ Product Catalog Management
- 📦 Order History & CSV Export
- 📝 System Logs & Telemetry
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive Design

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI
- **Charts**: Recharts
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Routing**: React Router v6

## Architecture

```
src/
├── core/              # Core utilities, API client, types
│   ├── api/          # API client and endpoints
│   ├── types/        # TypeScript interfaces
│   └── utils/        # Helper functions
├── hooks/            # Custom React hooks
├── features/         # Feature-based modules
│   ├── auth/         # Login, authentication
│   ├── dashboard/    # Statistics & charts
│   ├── devices/      # Device management
│   ├── orders/       # Order history
│   ├── products/     # Product catalog
│   └── logs/         # System logs
├── components/       # Shared UI components
├── context/          # React Context providers
└── App.tsx           # Main app with routing
```

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env.development` file:

```
VITE_API_URL=http://localhost:8000
```

For production (with nginx proxy), the API URL defaults to `/api`.

## API Integration

The admin console connects to the FastAPI backend at:
- **Development**: `http://localhost:8000`
- **Production**: `/api` (nginx proxy)

### Authentication

- Login endpoint: `POST /auth/login`
- Returns JWT access token (stored in localStorage)
- Refresh token stored in httpOnly cookie

### Protected Endpoints

All `/admin/*` endpoints require authentication via Bearer token.

## Deployment

### Docker

The app is built and served using the `Dockerfile.frontend.react`:

```bash
docker build -f Dockerfile.frontend.react -t remoteled-frontend .
docker run -p 80:80 remoteled-frontend
```

Access at: `http://localhost/admin`

### Manual Deployment

```bash
# Build
npm run build

# Output directory: dist/
# Serve with any static file server
```

## Features

### Dashboard
- 4 stat cards (devices, orders, revenue, success rate)
- Orders chart (last 7 days)
- Device status distribution chart
- Auto-refresh every 30 seconds

### Devices
- Grid view of all devices
- Add new devices with modal
- Test cycle / troubleshoot actions
- Status badges

### Products
- Table view of all products/services
- Support for TRIGGER, FIXED, VARIABLE types
- Edit product pricing and settings
- LED color indicators

### Orders
- Recent order history
- CSV export functionality
- Status badges
- Timestamp display

### Logs
- All logs / Errors only filter
- Real-time telemetry display
- Device-specific logs

## Contributing

1. Follow TypeScript best practices
2. Use provided components from `/components`
3. Create custom hooks for data fetching
4. Add types to `/core/types/index.ts`
5. Follow feature-based structure

## License

Part of the RemoteLED project.
