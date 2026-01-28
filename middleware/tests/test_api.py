"""
Script để test FaceFusion API
Có thể chạy: python test_api.py
"""
import requests
import base64
import json

# ===== CONFIG =====
API_URL = "http://127.0.0.1:8000"
SOURCE_IMAGE_PATH = "Kim-Seon-Ho.jpg"
TARGET_IMAGE_PATH = "go-youn-jung.jpg"
# ==================


def image_to_base64(image_path: str) -> str:
    """Chuyển đổi ảnh thành base64 string"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')


def test_face_swap_api():
    """Test API endpoint /face-swap với base64 images"""
    print("🧪 Testing FaceFusion API...")
    
    # Đọc và encode ảnh
    print(f"📖 Đọc ảnh source: {SOURCE_IMAGE_PATH}")
    print(f"📖 Đọc ảnh target: {TARGET_IMAGE_PATH}")
    
    source_base64 = image_to_base64(SOURCE_IMAGE_PATH)
    target_base64 = image_to_base64(TARGET_IMAGE_PATH)
    
    # Tạo request payload
    payload = {
        "source_image": source_base64,
        "target_image": target_base64
    }
    
    # Gửi request
    print(f"\n🚀 Gửi request đến {API_URL}/face-swap...")
    response = requests.post(f"{API_URL}/face-swap", json=payload)
    
    # Xử lý response
    if response.status_code == 200:
        result = response.json()
        print("✅ Thành công!")
        print(f"⏱️  Thời gian xử lý: {result['processing_time']}s")
        
        # Lưu ảnh kết quả
        result_base64 = result['result_image']
        result_image_data = base64.b64decode(result_base64)
        
        output_path = "api_result.png"
        with open(output_path, 'wb') as f:
            f.write(result_image_data)
        
        print(f"💾 Đã lưu ảnh kết quả vào: {output_path}")
    else:
        print(f"❌ Lỗi: {response.status_code}")
        print(f"Chi tiết: {response.text}")


def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing health check...")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   FaceFusion URL: {result['facefusion_url']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")


if __name__ == "__main__":
    # Test health check trước
    try:
        test_health_check()
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến API. Hãy chắc chắn API đang chạy!")
        print(f"   Chạy API bằng: python facefusion_api.py")
        exit(1)
    
    # Test face swap
    try:
        test_face_swap_api()
    except FileNotFoundError as e:
        print(f"❌ Không tìm thấy file ảnh: {e}")
        print("   Hãy đảm bảo các file ảnh tồn tại trong thư mục hiện tại")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
