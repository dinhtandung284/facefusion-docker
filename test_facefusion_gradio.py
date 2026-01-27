from gradio_client import Client, file
import shutil

# ===== CONFIG =====
FACEFUSION_URL = "http://127.0.0.1:7870"
SOURCE_IMAGE = "source.jpg"
TARGET_IMAGE = "target.jpg"
OUTPUT_IMAGE = "result.png"
# ==================

def main():
    print("🔌 Connecting to FaceFusion server...")
    client = Client(FACEFUSION_URL)

    # 0. Clear old state
    print("🧹 Clearing previous session...")
    client.predict(api_name="/clear")

    # 1. Upload SOURCE image (PHẢI dùng file())
    print("📤 Uploading SOURCE image...")
    client.predict(
        file=file(SOURCE_IMAGE),
        api_name="/update_1"
    )

    # 2. Upload TARGET image
    print("📤 Uploading TARGET image...")
    client.predict(
        file=file(TARGET_IMAGE),
        api_name="/update_1"
    )

    print("✅ Both images uploaded.")

    # 3. Start processing
    print("▶️ Starting process...")
    client.predict(api_name="/start")

    # 4. Run face swap
    print("⚙️ Running face swap...")
    image_output, video_output = client.predict(api_name="/run")

    if image_output and image_output.get("path"):
        output_path = image_output["path"]
        print(f"🖼 Result image generated at: {output_path}")

        shutil.copy(output_path, OUTPUT_IMAGE)
        print(f"💾 Saved final image to: {OUTPUT_IMAGE}")
    else:
        print("❌ No image result returned!")
        print("Image output:", image_output)
        print("Video output:", video_output)

    print("🎉 Done.")


if __name__ == "__main__":
    main()
