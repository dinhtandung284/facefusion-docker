# PowerShell script để test API bằng curl
# Sử dụng: .\test_api_curl.ps1

$API_URL = "http://127.0.0.1:8000"
$SOURCE_IMAGE = "Kim-Seon-Ho.jpg"
$TARGET_IMAGE = "go-youn-jung.jpg"

# Chuyển đổi ảnh sang base64
$SOURCE_BASE64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($SOURCE_IMAGE))
$TARGET_BASE64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($TARGET_IMAGE))

# Tạo JSON payload
$JSON_PAYLOAD = @{
    source_image = $SOURCE_BASE64
    target_image = $TARGET_BASE64
} | ConvertTo-Json

# Gửi request
Write-Host "🚀 Gửi request đến $API_URL/face-swap..." -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$API_URL/face-swap" -Method Post -Body $JSON_PAYLOAD -ContentType "application/json"

# Lưu ảnh kết quả
$resultImageData = [Convert]::FromBase64String($response.result_image)
[IO.File]::WriteAllBytes("api_result.png", $resultImageData)

Write-Host "✅ Thành công!" -ForegroundColor Green
Write-Host "⏱️  Thời gian xử lý: $($response.processing_time)s" -ForegroundColor Yellow
Write-Host "💾 Đã lưu ảnh kết quả vào: api_result.png" -ForegroundColor Green
