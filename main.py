"""
Barcode Detection & Extraction Service
Uses pyzbar for reliable barcode/QR code detection
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pyzbar import pyzbar
from PIL import Image
import io
import base64
import pdf2image
import numpy as np

app = FastAPI(title="Barcode Detection Service")

# Enable CORS for Supabase Edge Functions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_barcodes_in_image(image: Image.Image):
    """Detect all barcodes in an image using pyzbar"""
    # Convert to grayscale for better detection
    gray_image = image.convert('L')
    
    # Detect barcodes
    barcodes = pyzbar.decode(gray_image)
    
    # Deduplicate by barcode data (same QR code shown twice)
    seen_data = set()
    unique_barcodes = []
    
    for barcode in barcodes:
        try:
            barcode_data = barcode.data.decode("utf-8")
        except:
            barcode_data = str(barcode.data)
        
        # Skip if we've seen this exact data before
        if barcode_data in seen_data:
            continue
        
        seen_data.add(barcode_data)
        unique_barcodes.append(barcode)
    
    results = []
    for idx, barcode in enumerate(unique_barcodes):
        # Get barcode rectangle
        x, y, w, h = barcode.rect
        
        # Add padding around barcode (10% on each side)
        padding = int(min(w, h) * 0.1)
        x_padded = max(0, x - padding)
        y_padded = max(0, y - padding)
        w_padded = min(image.width - x_padded, w + 2 * padding)
        h_padded = min(image.height - y_padded, h + 2 * padding)
        
        # Crop barcode from original image (with padding)
        barcode_crop = image.crop((
            x_padded,
            y_padded,
            x_padded + w_padded,
            y_padded + h_padded
        ))
        
        # Convert to base64
        buffer = io.BytesIO()
        barcode_crop.save(buffer, format="PNG", optimize=True, quality=95)
        barcode_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Decode barcode data
        try:
            barcode_data = barcode.data.decode("utf-8")
        except:
            barcode_data = str(barcode.data)
        
        # Determine location on page
        img_width, img_height = image.size
        location = get_barcode_location(x, y, w, h, img_width, img_height)
        
        results.append({
            "index": idx,
            "type": barcode.type,
            "data": barcode_data,
            "rect": {
                "x": x,
                "y": y,
                "width": w,
                "height": h
            },
            "location": location,
            "image_base64": barcode_base64,
            "quality": barcode.quality if hasattr(barcode, 'quality') else None
        })
    
    return results

def get_barcode_location(x, y, w, h, img_width, img_height):
    """Determine barcode location on page (top-left, bottom-right, etc.)"""
    # Calculate center point
    center_x = x + w / 2
    center_y = y + h / 2
    
    # Divide page into 9 regions
    third_width = img_width / 3
    third_height = img_height / 3
    
    # Horizontal position
    if center_x < third_width:
        h_pos = "left"
    elif center_x < 2 * third_width:
        h_pos = "center"
    else:
        h_pos = "right"
    
    # Vertical position
    if center_y < third_height:
        v_pos = "top"
    elif center_y < 2 * third_height:
        v_pos = "middle"
    else:
        v_pos = "bottom"
    
    return f"{v_pos}-{h_pos}"

@app.post("/detect")
async def detect_barcodes(file: UploadFile = File(...)):
    """
    Detect barcodes in uploaded image or PDF
    Returns: List of detected barcodes with cropped images
    """
    try:
        file_bytes = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if file.filename else 'unknown'
        
        all_barcodes = []
        
        if file_extension == 'pdf':
            # Convert PDF pages to images
            try:
                images = pdf2image.convert_from_bytes(file_bytes, dpi=300)
                
                for page_num, image in enumerate(images):
                    barcodes = detect_barcodes_in_image(image)
                    
                    # Add page number to each barcode
                    for barcode in barcodes:
                        barcode['page'] = page_num + 1
                        all_barcodes.append(barcode)
                    
                    # Only scan first 3 pages for performance
                    if page_num >= 2:
                        break
                        
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"PDF processing error: {str(e)}")
        
        else:
            # Process as image
            try:
                image = Image.open(io.BytesIO(file_bytes))
                all_barcodes = detect_barcodes_in_image(image)
                
                # Add page number (always 1 for images)
                for barcode in all_barcodes:
                    barcode['page'] = 1
                    
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")
        
        if not all_barcodes:
            return {
                "detected": False,
                "count": 0,
                "barcodes": []
            }
        
        return {
            "detected": True,
            "count": len(all_barcodes),
            "barcodes": all_barcodes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "barcode-detection"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

