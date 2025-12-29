#!/bin/bash
# Test script for barcode detection service

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_URL="${1:-http://localhost:8000}"
TEST_FILE="${2:-test-booking.pdf}"

echo -e "${BLUE}🧪 Testing Barcode Detection Service${NC}"
echo -e "${BLUE}Service URL: ${SERVICE_URL}${NC}"
echo ""

# Test 1: Health check
echo -e "${BLUE}Test 1: Health Check${NC}"
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health")
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | grep -o '"status":"healthy"')

if [ -n "$HEALTH_STATUS" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test 2: Barcode detection (if test file exists)
if [ -f "$TEST_FILE" ]; then
    echo -e "${BLUE}Test 2: Barcode Detection${NC}"
    echo "Uploading: $TEST_FILE"
    
    DETECT_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/detect" \
        -F "file=@${TEST_FILE}")
    
    DETECTED=$(echo $DETECT_RESPONSE | grep -o '"detected":true')
    
    if [ -n "$DETECTED" ]; then
        echo -e "${GREEN}✅ Barcode detected!${NC}"
        
        # Extract barcode count
        COUNT=$(echo $DETECT_RESPONSE | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
        echo "Barcodes found: $COUNT"
        
        # Extract barcode type
        TYPE=$(echo $DETECT_RESPONSE | grep -o '"type":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Type: $TYPE"
        
        # Extract barcode location
        LOCATION=$(echo $DETECT_RESPONSE | grep -o '"location":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Location: $LOCATION"
        
        echo ""
        echo "Full response (truncated):"
        echo $DETECT_RESPONSE | jq -r '.barcodes[0] | del(.image_base64)' 2>/dev/null || echo $DETECT_RESPONSE | head -c 500
    else
        echo -e "${RED}❌ No barcodes detected${NC}"
        echo "Response: $DETECT_RESPONSE"
    fi
else
    echo -e "${BLUE}Test 2: Skipped (no test file found)${NC}"
    echo "To test barcode detection, run:"
    echo "  ./test_service.sh $SERVICE_URL path/to/booking.pdf"
fi
echo ""

# Test 3: Error handling (invalid file)
echo -e "${BLUE}Test 3: Error Handling${NC}"
ERROR_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/detect" \
    -F "file=@main.py")

ERROR_CHECK=$(echo $ERROR_RESPONSE | grep -o '"detail"')

if [ -n "$ERROR_CHECK" ]; then
    echo -e "${GREEN}✅ Error handling works${NC}"
    echo "Service correctly rejected invalid file"
else
    echo -e "${RED}⚠️  Unexpected response for invalid file${NC}"
    echo "Response: $ERROR_RESPONSE"
fi
echo ""

echo -e "${GREEN}🎉 Testing complete!${NC}"

