from gradio_client import Client, handle_file
import shutil
import time

# ===== CONFIG =====
FACEFUSION_URL = "http://127.0.0.1:7870"
SOURCE_IMAGE = "Kim-Seon-Ho.jpg"
TARGET_IMAGE = "go-youn-jung.jpg"
OUTPUT_IMAGE = "result.png"
NUM_RUNS = 10  # Số lần chạy
# ==================

def process_single_face_swap(client, source_image, target_image, run_number=None):
    """Xử lý một lần face swap và trả về thời gian thực thi"""
    start_time = time.time()
    
    # 1. Upload SOURCE image (dùng /update_1 cho single file)
    if run_number:
        print(f"[Lần {run_number}] 📤 Uploading SOURCE image...")
    else:
        print("📤 Uploading SOURCE image...")
    client.predict(
        file=handle_file(target_image),
        api_name="/update_1"
    )

    # 2. Upload TARGET image (dùng /update cho list files)
    if run_number:
        print(f"[Lần {run_number}] 📤 Uploading TARGET image...")
    else:
        print("📤 Uploading TARGET image...")
    client.predict(
        files=[handle_file(source_image)],
        api_name="/update"
    )

    # 3. Run face swap
    if run_number:
        print(f"[Lần {run_number}] ⚙️ Running face swap...")
    else:
        print("⚙️ Running face swap...")
    image_output, video_output = client.predict(api_name="/run")

    # Lấy output path
    output_path = None
    if image_output:
        if isinstance(image_output, dict) and image_output.get("value"):
            output_path = image_output["value"]
        elif isinstance(image_output, dict) and image_output.get("path"):
            output_path = image_output["path"]
        elif isinstance(image_output, str):
            output_path = image_output

    elapsed_time = time.time() - start_time
    
    if output_path:
        if run_number:
            print(f"[Lần {run_number}] ✅ Hoàn thành trong {elapsed_time:.2f}s")
        else:
            print(f"✅ Hoàn thành trong {elapsed_time:.2f}s")
    else:
        print(f"❌ Không có kết quả!")
    
    return elapsed_time, output_path


def main():
    print("🔌 Connecting to FaceFusion server...")
    client = Client(FACEFUSION_URL)

    # Clear một lần duy nhất ở đầu (để giữ model trong VRAM, có thể comment dòng này)
    print("🧹 Clearing previous session (chỉ một lần)...")
    client.predict(api_name="/clear")
    print("✅ Model đã được load vào VRAM, sẽ không reset lại giữa các lần chạy\n")

    # Chạy nhiều lần
    times = []
    total_start_time = time.time()
    
    print(f"🚀 Bắt đầu chạy {NUM_RUNS} lần...\n")
    
    for i in range(1, NUM_RUNS + 1):
        elapsed_time, output_path = process_single_face_swap(
            client, SOURCE_IMAGE, TARGET_IMAGE, run_number=i
        )
        times.append(elapsed_time)
        
        # Lưu kết quả lần đầu tiên
        if i == 1 and output_path:
            try:
                shutil.copy(output_path, OUTPUT_IMAGE)
                print(f"💾 Đã lưu ảnh kết quả đầu tiên vào: {OUTPUT_IMAGE}\n")
            except Exception as e:
                print(f"❌ Lỗi khi copy file: {e}\n")
        else:
            print()  # Xuống dòng
    
    total_elapsed_time = time.time() - total_start_time
    
    # In kết quả thống kê
    print("=" * 60)
    print("📊 KẾT QUẢ THỐNG KÊ")
    print("=" * 60)
    print(f"Tổng số lần chạy: {NUM_RUNS}")
    print(f"Tổng thời gian: {total_elapsed_time:.2f}s")
    print(f"Thời gian trung bình mỗi lần: {sum(times) / len(times):.2f}s")
    print(f"\nThời gian từng lần:")
    for i, t in enumerate(times, 1):
        print(f"  Lần {i:2d}: {t:.2f}s")
    print(f"\nThời gian nhanh nhất: {min(times):.2f}s")
    print(f"Thời gian chậm nhất: {max(times):.2f}s")
    print("=" * 60)
    print("🎉 Hoàn thành!")


if __name__ == "__main__":
    main()
