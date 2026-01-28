# FaceFusion API Documentation

API FastAPI để thực hiện face swap sử dụng FaceFusion Gradio server.

## Cài đặt

```bash
pip install fastapi uvicorn python-multipart requests pillow
```

## Chạy API

```bash
python facefusion_api.py
```

API sẽ chạy tại: `http://127.0.0.1:8000`

## Endpoints

### 1. POST `/face-swap`

Nhận 2 ảnh dạng base64 và trả về ảnh kết quả dạng base64.

**Request Body (JSON):**
```json
{
  "source_image": "base64_encoded_image_string",
  "target_image": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "success": true,
  "result_image": "base64_encoded_result_image",
  "processing_time": 2.45,
  "message": "Face swap thành công"
}
```

### 2. POST `/face-swap/files`

Nhận 2 file ảnh và trả về file ảnh kết quả.

**Request:** Multipart form data
- `source_image`: File ảnh source
- `target_image`: File ảnh target

**Response:** File ảnh PNG

### 3. GET `/health`

Kiểm tra trạng thái API và kết nối với FaceFusion.

**Response:**
```json
{
  "status": "healthy",
  "facefusion_url": "http://127.0.0.1:7870",
  "message": "API đang hoạt động bình thường"
}
```

## Test API

### Sử dụng Python script:

```bash
python test_api.py
```

### Sử dụng curl (Linux/Mac):

```bash
bash test_api_curl.sh
```

### Sử dụng PowerShell (Windows):

```powershell
.\test_api_curl.ps1
```

### Sử dụng curl trực tiếp:

```bash
# Chuyển đổi ảnh sang base64
SOURCE_BASE64=$(base64 -i source.jpg | tr -d '\n')
TARGET_BASE64=$(base64 -i target.jpg | tr -d '\n')

# Gửi request
curl -X POST "http://127.0.0.1:8000/face-swap" \
  -H "Content-Type: application/json" \
  -d "{\"source_image\": \"$SOURCE_BASE64\", \"target_image\": \"$TARGET_BASE64\"}"
```

### Sử dụng file JSON mẫu:

File `test_api.json` chứa cấu trúc JSON mẫu. Bạn cần thay thế giá trị base64 bằng ảnh thực tế của bạn.

```bash
# Sử dụng với curl
curl -X POST "http://127.0.0.1:8000/face-swap" \
  -H "Content-Type: application/json" \
  -d @test_api.json
```

## Lưu ý

1. Đảm bảo FaceFusion Gradio server đang chạy tại `http://127.0.0.1:7870`
2. Ảnh base64 có thể có hoặc không có prefix `data:image/jpeg;base64,`
3. API tự động cleanup các file tạm sau khi xử lý xong
4. Thời gian xử lý được tính từ lúc nhận request đến khi có kết quả
