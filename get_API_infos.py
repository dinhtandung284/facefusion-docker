from gradio_client import Client
import sys

client = Client("http://127.0.0.1:7870")

# Mở file để ghi
with open("facefusion_api.txt", "w", encoding="utf-8") as f:
    # Chuyển hướng stdout vào file để bắt nội dung từ client.view_api()
    sys.stdout = f
    client.view_api()
    # Trả stdout về lại bình thường
    sys.stdout = sys.__stdout__

print("Xong! Bạn có thể mở file facefusion_api.txt để soi rồi đó.")

# Lệnh này sẽ in ra danh sách tất cả các hàm (endpoints), 
# tham số đầu vào và kiểu dữ liệu trả về của FaceFusion
# client.view_api()