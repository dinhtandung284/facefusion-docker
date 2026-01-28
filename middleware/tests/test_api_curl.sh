#!/bin/bash
# Script để test API bằng curl
# Sử dụng: bash test_api_curl.sh

API_URL="http://127.0.0.1:8000"
SOURCE_IMAGE="Kim-Seon-Ho.jpg"
TARGET_IMAGE="go-youn-jung.jpg"

# Chuyển đổi ảnh sang base64
SOURCE_BASE64=$(base64 -i "$SOURCE_IMAGE" | tr -d '\n')
TARGET_BASE64=$(base64 -i "$TARGET_IMAGE" | tr -d '\n')

# Tạo JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "source_image": "$SOURCE_BASE64",
  "target_image": "$TARGET_BASE64"
}
EOF
)

# Gửi request
echo "🚀 Gửi request đến $API_URL/face-swap..."
curl -X POST "$API_URL/face-swap" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" \
  -o response.json

echo ""
echo "✅ Response đã được lưu vào response.json"
echo "📝 Để xem kết quả, bạn có thể parse JSON và decode base64 image"
