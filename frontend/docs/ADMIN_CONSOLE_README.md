# RemoteLED Admin Console

A real-time web dashboard for monitoring and managing RemoteLED devices, orders, and services.

## 🎯 Features

- **Real-time Statistics**: Total devices, active orders, revenue, and success rate
- **Interactive Charts**: 7-day order trends and device status distribution
- **Device Management**: View all registered devices with service counts and order stats
- **Order Tracking**: Monitor recent orders with status, amounts, and timestamps
- **Product Catalog**: Manage services/products with pricing and LED configurations
- **System Logs**: View telemetry logs with filtering options
- **Auto-refresh**: Dashboard updates every 30 seconds

## 🚀 Quick Start

### 1. Start the Database

Ensure PostgreSQL is running and the database is set up:

```bash
# If not already created
createdb remoteled
psql -d remoteled -f database/schema.sql
psql -d remoteled -f database/seed.sql  # Optional: load test data
```

### 2. Start the Backend API

```bash
cd backend
source ../.venv/bin/activate  # or activate your venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify the backend is running:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 3. Open the Admin Console

Option A - Direct file access:
```bash
open admin_console.html
```

Option B - Use a local web server (recommended):
```bash
# Python 3
python3 -m http.server 8080

# Then visit: http://localhost:8080/admin_console.html
```

## 📊 API Endpoints

The admin console uses these backend endpoints:

### Statistics & Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/stats/overview` | GET | Dashboard statistics (devices, orders, revenue, success rate) |
| `/admin/stats/orders-last-7-days` | GET | Order counts for last 7 days |
| `/admin/stats/device-status` | GET | Device status distribution |

### Data Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/devices/all` | GET | All devices with service counts and order stats |
| `/admin/orders/recent` | GET | Recent orders with device and product details |
| `/admin/services/all` | GET | All services/products with device info |
| `/admin/logs/recent` | GET | System logs with optional error filtering |

### Query Parameters

**Orders:**
- `limit` (default: 50, max: 500) - Number of orders to return

**Logs:**
- `limit` (default: 100, max: 500) - Number of logs to return
- `error_only` (default: false) - Filter to show only errors

## 🎨 Dashboard Components

### 1. Statistics Cards
- **Total Devices**: Active devices with monthly growth
- **Active Orders**: Currently running orders with weekly comparison
- **Revenue Today**: Daily revenue with yesterday's comparison
- **Success Rate**: Order completion rate with weekly trend

### 2. Charts
- **Orders Last 7 Days**: Bar chart showing daily order volume
- **Device Status**: Distribution of online/offline/maintenance devices

### 3. Device Management
- Device cards showing:
  - Device name and ID
  - Status badge (online/offline)
  - Location and GPIO pin
  - Service count
  - Order completion stats
  - Quick action buttons

### 4. Recent Orders Table
Columns: Order ID, Device, Product Type, Amount, Duration, Status, Timestamp

### 5. Product Catalog Table
Columns: Product ID, Device, Type, Price, Duration, LED Color, Status, Actions

### 6. System Logs
- Tabbed interface (All Logs / Errors Only)
- Real-time telemetry and event logs
- Color-coded log levels (INFO/ERROR)

## 🔧 Configuration

Edit `admin_console.html` to change the API endpoint:

```javascript
// Line ~548
const API_BASE_URL = 'http://localhost:8000';
```

For production, update to your production API URL:
```javascript
const API_BASE_URL = 'https://api.yourdomain.com';
```

## 🎭 Service Type Indicators

| Type | LED Color | Badge | Description |
|------|-----------|-------|-------------|
| TRIGGER | 🔵 Blue Blink | Blue | One-time activation (2 seconds) |
| FIXED | 🟢 Green Solid | Green | Fixed duration (e.g., 40 minutes) |
| VARIABLE | 🟠 Amber Solid | Amber | Pay-per-time (variable duration) |

## 📱 Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive design)

## 🔒 Security Notes

**Current Implementation (Development):**
- No authentication/authorization
- CORS enabled for all origins
- Suitable for local/development use only

**For Production:**
1. Add authentication (JWT tokens, OAuth, etc.)
2. Restrict CORS to specific domains
3. Enable HTTPS/TLS
4. Implement rate limiting
5. Add audit logging
6. Set up proper access controls

## 🐛 Troubleshooting

### Dashboard shows "Loading..." indefinitely

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check browser console for CORS errors
3. Verify database connection in backend logs

### No data displayed

**Solution:**
1. Ensure database has seed data: `psql remoteled -c "SELECT COUNT(*) FROM devices;"`
2. Check API responses in browser Network tab
3. Verify backend logs for SQL errors

### CORS errors in browser console

**Solution:**
Update `backend/app/core/config.py`:
```python
CORS_ORIGINS = "http://localhost:8080,http://127.0.0.1:8080,file://"
```

Then restart the backend.

### Chart bars not animating

**Solution:**
This is cosmetic. Ensure JavaScript is enabled and refresh the page.

## 📈 Future Enhancements

Potential improvements:
- [ ] Export data to CSV/Excel
- [ ] Advanced filtering and search
- [ ] Device configuration forms
- [ ] Real-time WebSocket updates
- [ ] Historical analytics (30/90 days)
- [ ] Alert notifications
- [ ] User management
- [ ] Dark mode toggle
- [ ] Mobile app version

## 🧪 Testing

Test the admin API endpoints:

```bash
# Get dashboard stats
curl http://localhost:8000/admin/stats/overview

# Get orders for last 7 days
curl http://localhost:8000/admin/stats/orders-last-7-days

# Get all devices
curl http://localhost:8000/admin/devices/all

# Get recent orders
curl http://localhost:8000/admin/orders/recent?limit=10

# Get all services
curl http://localhost:8000/admin/services/all

# Get recent logs
curl http://localhost:8000/admin/logs/recent?limit=20

# Get errors only
curl http://localhost:8000/admin/logs/recent?error_only=true
```

## 📝 Development Notes

The admin console uses:
- **Pure HTML/CSS/JavaScript** (no frameworks)
- **Fetch API** for HTTP requests
- **Promise.all()** for parallel data loading
- **Auto-refresh** every 30 seconds
- **Responsive grid layouts**
- **CSS gradients and animations**

Simple and maintainable per user preferences.

## 📚 Related Documentation

- [Main README](README.md) - Project overview
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Database Schema](database/README.md) - Database documentation
- [Test Report](TEST_REPORT.md) - Testing results

---

**Built with ❤️ for RemoteLED Project**

