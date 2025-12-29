# Quick Start Guide - Barcode Detection

## 🚀 Local Testing (5 minutes)

### 1. Install Dependencies

**macOS:**
```bash
brew install zbar poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libzbar0 poppler-utils
```

### 2. Setup Python Environment

```bash
cd barcode-service
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Service

```bash
python main.py
```

Service is now running at: `http://localhost:8000`

### 4. Test It

Open http://localhost:8000/docs in your browser to see the interactive API docs.

Or use the test script:
```bash
./test_service.sh
```

Or test with curl:
```bash
# Health check
curl http://localhost:8000/health

# Detect barcodes (replace with your file path)
curl -X POST "http://localhost:8000/detect" \
  -F "file=@/path/to/booking.pdf"
```

---

## ☁️ Deploy to Production (10 minutes)

### Option 1: Render.com (Free Tier) ⭐ Recommended

1. **Push to GitHub:**
   ```bash
   cd barcode-service
   git init
   git add .
   git commit -m "Initial barcode service"
   git remote add origin https://github.com/yourusername/barcode-service.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Click **New** → **Web Service**
   - Connect your GitHub repo
   - Settings:
     - **Name**: `otta-barcode-service`
     - **Environment**: Docker
     - **Region**: Choose closest region
     - **Instance Type**: Free
   - Click **Create Web Service**

3. **Copy your service URL:**
   ```
   https://otta-barcode-service.onrender.com
   ```

### Option 2: Railway.app (Also Free)

1. Push to GitHub (same as above)
2. Go to [railway.app](https://railway.app)
3. **New Project** → **Deploy from GitHub**
4. Select your repo
5. Railway auto-detects Dockerfile and deploys
6. Copy your service URL from the dashboard

### Option 3: Docker Compose (Local/VPS)

```bash
cd barcode-service
docker-compose up -d
```

Service runs at: `http://localhost:8000`

For VPS deployment, expose port 8000 or use a reverse proxy (nginx).

---

## 🔗 Connect to Supabase

### 1. Set Environment Variable

```bash
cd /path/to/otta-native

# Set your barcode service URL
npx supabase secrets set BARCODE_SERVICE_URL=https://otta-barcode-service.onrender.com

# Redeploy Edge Function
npx supabase functions deploy parse-booking
```

### 2. Verify Integration

Upload a booking PDF/image in your app and watch the console logs:

```
🔍 Detecting barcodes...
✅ Detected 1 barcode(s)
📊 Barcode type: QRCODE
📍 Barcode location: top-right
📤 Uploading barcode image...
✅ Barcode uploaded
```

### 3. Check Database

```sql
SELECT id, title, barcode_detected, barcode_type, barcode_data 
FROM bookings 
WHERE barcode_detected = true 
LIMIT 5;
```

---

## 🧪 Testing

### Test with Sample Files

Download test bookings with barcodes:
- [Sample Flight Ticket](https://www.qrcode-generator.com)
- [Sample Event Ticket](https://barcode.tec-it.com/en)

### Test API Directly

```bash
# Test with your service URL
curl -X POST "https://your-service.onrender.com/detect" \
  -F "file=@booking.pdf" \
  | jq '.'
```

### Expected Response

```json
{
  "detected": true,
  "count": 1,
  "barcodes": [
    {
      "index": 0,
      "type": "QRCODE",
      "data": "https://checkin.example.com/ABC123",
      "rect": {
        "x": 450,
        "y": 120,
        "width": 150,
        "height": 150
      },
      "location": "top-right",
      "page": 1,
      "image_base64": "iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}
```

---

## 🐛 Troubleshooting

### "Cannot find libzbar"
Install system dependencies (see step 1 above)

### "PDF processing failed"
Ensure poppler-utils is installed

### "Service returns 500"
- Check service logs on deployment platform
- Restart the service
- Verify all dependencies are installed

### "No barcodes detected"
- Check if your test file actually has a barcode
- Try with a clearer/higher resolution image
- Check service logs for errors

### Barcode service is slow
- **Cold starts**: Free tier services sleep after 15min idle (first request takes ~30s)
- **Solution**: Upgrade to paid tier ($7/mo) for instant responses
- **Workaround**: Ping service every 10min to keep it warm

---

## 📊 Monitor Performance

### Check Service Uptime

Add to your monitoring (e.g., UptimeRobot):
```
https://your-service.onrender.com/health
```

### View Service Logs

**Render.com:**
- Dashboard → Your Service → Logs tab

**Railway.app:**
- Project → Deployments → View Logs

### Analytics Queries

```sql
-- Detection rate
SELECT 
  COUNT(*) as total_bookings,
  SUM(CASE WHEN barcode_detected THEN 1 ELSE 0 END) as with_barcode,
  ROUND(100.0 * SUM(CASE WHEN barcode_detected THEN 1 ELSE 0 END) / COUNT(*), 2) as detection_rate
FROM bookings;

-- Most common barcode types
SELECT barcode_type, COUNT(*) 
FROM bookings 
WHERE barcode_detected = true 
GROUP BY barcode_type 
ORDER BY COUNT(*) DESC;
```

---

## 🔐 Production Checklist

Before going live:

- [ ] Service deployed and accessible
- [ ] `BARCODE_SERVICE_URL` set in Supabase
- [ ] Edge Function redeployed
- [ ] Tested with real bookings
- [ ] Monitoring/uptime checks configured
- [ ] Consider adding API key authentication (see main docs)
- [ ] Consider rate limiting (see main docs)
- [ ] Set up error alerting (Sentry, etc.)

---

## 🎉 Done!

Your app now has automatic barcode detection!

- Upload any booking → barcode is detected & cropped
- Barcode stored separately in database
- Accessible via `booking.barcodeUrl`

**Next Steps:**
- Display barcodes in UI (see `IMPLEMENTING_BARCODE_DETECTION.md`)
- Monitor detection rates
- Improve accuracy with preprocessing (see advanced docs)

**Support:** Check `IMPLEMENTING_BARCODE_DETECTION.md` for detailed docs and troubleshooting.

