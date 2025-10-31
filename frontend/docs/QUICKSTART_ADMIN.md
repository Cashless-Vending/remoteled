# Admin Console - Quick Start Guide

Get your admin dashboard running in 3 minutes! ⚡

---

## ✅ Prerequisites

- PostgreSQL 15+ installed and running
- Python 3.11+ with virtual environment
- Database seeded with test data
- Browser (Chrome, Firefox, Safari, or Edge)

---

## 🚀 3-Step Setup

### Step 1: Start Database
```bash
# If not running, start PostgreSQL
brew services start postgresql@15

# Verify database exists and has data
psql remoteled -c "SELECT COUNT(*) FROM devices;"
# Should return: count = 4 (or more)
```

**No data?** Load seed data:
```bash
psql -d remoteled -f database/schema.sql
psql -d remoteled -f database/seed.sql
```

---

### Step 2: Start Backend API
```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Verify it works:**
```bash
# In another terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

curl http://localhost:8000/admin/stats/overview
# Should return JSON with stats
```

---

### Step 3: Open Admin Console
```bash
# In project root (where admin_console.html is)
python3 -m http.server 8080
```

**Then open in browser:**
```
http://localhost:8080/admin_console.html
```

---

## 🎉 Success!

You should see:
- ✅ Statistics cards with numbers (not "--")
- ✅ Bar charts with data
- ✅ Device cards in grid
- ✅ Orders and services in tables
- ✅ System logs at bottom
- ✅ Auto-refresh every 30 seconds (check console)

---

## 🐛 Troubleshooting

### Problem: Dashboard shows "Loading..." forever

**Check backend:**
```bash
curl http://localhost:8000/health
```
- ❌ Connection refused? → Backend not running, go to Step 2
- ✅ Returns JSON? → Backend is fine

**Check browser console (F12):**
- ❌ CORS error? → Use HTTP server (Step 3), don't open file directly
- ❌ 404 errors? → Check API_BASE_URL in admin_console.html (line ~548)
- ❌ 500 errors? → Check backend logs for database issues

---

### Problem: No data shown (just empty tables)

**Check database:**
```bash
psql remoteled -c "SELECT COUNT(*) FROM devices;"
psql remoteled -c "SELECT COUNT(*) FROM orders;"
```
- ❌ count = 0? → Load seed data: `psql -d remoteled -f database/seed.sql`
- ✅ count > 0? → Check backend logs for SQL errors

---

### Problem: CORS errors in browser

**Solution:**
1. Don't open HTML file directly (`file://`)
2. Use HTTP server: `python3 -m http.server 8080`
3. Update backend CORS if needed: `backend/app/core/config.py`

---

### Problem: Backend won't start

**Check virtual environment:**
```bash
source .venv/bin/activate
pip list | grep fastapi
```
- ❌ Not installed? → Run: `pip install -r backend/requirements.txt`

**Check database connection:**
```bash
psql remoteled -c "SELECT 1;"
```
- ❌ Connection failed? → Check PostgreSQL is running
- ❌ Database not found? → Create: `createdb remoteled`

---

## 📋 Test Checklist

Run this test script to verify everything:
```bash
chmod +x test_admin_api.sh
./test_admin_api.sh
```

**Expected:**
```
✓ PASS (HTTP 200) - API Health
✓ PASS (HTTP 200) - Overview Stats
✓ PASS (HTTP 200) - Orders Last 7 Days
✓ PASS (HTTP 200) - Device Status Distribution
✓ PASS (HTTP 200) - All Devices
✓ PASS (HTTP 200) - Recent Orders
✓ PASS (HTTP 200) - All Services
✓ PASS (HTTP 200) - Recent Logs
```

---

## 🔗 Useful URLs

Once running:

| Service | URL |
|---------|-----|
| Admin Console | http://localhost:8080/admin_console.html |
| API Root | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Stats API | http://localhost:8000/admin/stats/overview |

---

## ⚙️ Configuration

### Change API URL
Edit `admin_console.html` line ~548:
```javascript
const API_BASE_URL = 'http://localhost:8000';
// Change to: 'http://your-server.com:8000'
```

### Change Auto-Refresh Interval
Edit `admin_console.html` line ~795:
```javascript
setInterval(function() {
    initDashboard();
}, 30000);  // Change 30000 = 30 seconds
```

### Change Table Limits
Query parameters in JavaScript:
```javascript
// Line ~710
'/admin/orders/recent?limit=20'
// Change limit=20 to limit=50
```

---

## 📚 Documentation

- **Full docs**: `ADMIN_CONSOLE_README.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **Architecture**: `ADMIN_CONSOLE_ARCHITECTURE.md`
- **Main README**: `README.md` (updated with admin section)

---

## 💡 Pro Tips

1. **Keep browser console open** (F12) to see auto-refresh logs
2. **Use Chrome DevTools Network tab** to debug API calls
3. **Check backend logs** for SQL query debugging
4. **Seed data includes 4 devices** with various orders/services
5. **Auto-refresh can be disabled** by commenting out setInterval

---

## 🎓 Next Steps

Once it's working:

1. **Explore the data**: Click through devices, orders, logs
2. **Test filtering**: Try "Errors Only" tab in logs
3. **Monitor auto-refresh**: Watch console every 30 seconds
4. **Check API docs**: Visit http://localhost:8000/docs
5. **Customize styling**: Edit CSS in admin_console.html

---

## 📞 Need Help?

Check these in order:
1. Browser console (F12) for JavaScript errors
2. Backend logs for Python errors
3. PostgreSQL logs for database errors
4. `ADMIN_CONSOLE_README.md` for detailed troubleshooting

---

**Ready to go!** 🚀

Your admin dashboard should be up and running. Enjoy monitoring your RemoteLED devices!

