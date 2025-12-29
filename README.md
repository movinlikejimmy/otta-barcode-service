# Barcode Detection Service

High-performance barcode and QR code detection service using **pyzbar**.

## Features

✅ Detects all major barcode formats (QR, Code128, Code39, PDF417, etc.)
✅ Automatically crops and extracts barcode regions
✅ Supports both images and PDFs (first 3 pages)
✅ Returns barcode location on page (top-left, bottom-right, etc.)
✅ Base64 encoded cropped barcode images
✅ Decodes barcode data
✅ High-quality output with padding

## Local Development

### Prerequisites
- Python 3.11+
- libzbar (for pyzbar)
- poppler-utils (for PDF support)

### Install System Dependencies

**macOS:**
```bash
brew install zbar poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libzbar0 poppler-utils
```

**Windows:**
```bash
# Install via chocolatey
choco install zbar poppler
```

### Setup

```bash
cd barcode-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Locally

```bash
python main.py
```

Server runs on: `http://localhost:8000`

API docs available at: `http://localhost:8000/docs`

### Test with Docker

```bash
docker-compose up --build
```

## API Usage

### Detect Barcodes

**Endpoint:** `POST /detect`

**Request:**
```bash
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@booking.pdf"
```

**Response:**
```json
{
  "detected": true,
  "count": 2,
  "barcodes": [
    {
      "index": 0,
      "type": "QRCODE",
      "data": "https://checkin.airline.com/ABC123",
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

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8000/health
```

## Deployment

### Option 1: Render.com (Recommended - Free Tier Available)

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Web Service
4. Connect your repo
5. Settings:
   - **Environment**: Docker
   - **Region**: Choose closest to your users
   - **Instance Type**: Free (or Starter for production)
6. Deploy!

Your service URL: `https://your-service.onrender.com`

### Option 2: Railway.app

1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Select your repo
5. Railway auto-detects Dockerfile
6. Deploy!

### Option 3: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
cd barcode-service
flyctl launch
flyctl deploy
```

### Option 4: Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/barcode-service

# Deploy
gcloud run deploy barcode-service \
  --image gcr.io/PROJECT_ID/barcode-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Integration with Supabase

Once deployed, update your Supabase Edge Function:

```typescript
// supabase/functions/parse-booking/index.ts
const BARCODE_SERVICE_URL = 'https://your-service.onrender.com';

// After file upload, detect barcodes
const formData = new FormData();
formData.append('file', pdfBlob);

const barcodeResponse = await fetch(`${BARCODE_SERVICE_URL}/detect`, {
  method: 'POST',
  body: formData
});

const barcodeData = await barcodeResponse.json();

if (barcodeData.detected) {
  // Upload cropped barcode to Supabase Storage
  const barcode = barcodeData.barcodes[0];
  const barcodeBuffer = Buffer.from(barcode.image_base64, 'base64');
  
  const { data: barcodeUpload } = await supabase.storage
    .from('bookings')
    .upload(`barcodes/${fileName}-barcode.png`, barcodeBuffer);
}
```

## Supported Barcode Types

- QR Code
- Code 128
- Code 39
- Code 93
- EAN-8 / EAN-13
- UPC-A / UPC-E
- PDF417
- Aztec Code
- Data Matrix
- And more...

## Performance

- **Images**: ~100-200ms per image
- **PDFs**: ~300-500ms per page
- **Memory**: ~200MB baseline
- **Concurrent**: Handles 10+ simultaneous requests

## Environment Variables

```bash
# Optional: Configure max file size (default: 10MB)
MAX_FILE_SIZE=10485760

# Optional: Max pages to scan in PDFs (default: 3)
MAX_PDF_PAGES=3
```

## Troubleshooting

### "Cannot find libzbar"
Install system dependencies (see above)

### "PDF processing failed"
Ensure poppler-utils is installed

### Low detection rate
- Increase image DPI (currently 300)
- Try preprocessing (contrast, brightness)
- Ensure barcode is clear and unobstructed

## Security

- CORS enabled for Supabase domains only (update in production)
- No data persistence (stateless service)
- Rate limiting recommended for production
- Add authentication for production use

## License

MIT

