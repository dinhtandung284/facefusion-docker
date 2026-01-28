from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from gradio_client import Client, handle_file
import base64
import tempfile
import os
import time
from typing import Optional
from pydantic import BaseModel
import io
from PIL import Image

app = FastAPI(title="FaceFusion API", description="API wrapper for FaceFusion")

# ===== CONFIG =====
FACEFUSION_URL = "http://127.0.0.1:7870"
# ==================

# Khởi tạo client một lần khi app start
client = None

@app.on_event("startup")
async def startup_event():
    """Khởi tạo Gradio client khi app khởi động"""
    global client
    try:
        print("[INFO] Connecting to FaceFusion server...")
        client = Client(FACEFUSION_URL)
        print("[INFO] Connected to FaceFusion server")
    except Exception as e:
        print(f"[ERROR] Error connecting to FaceFusion server: {e}")
        raise


class FaceSwapRequest(BaseModel):
    """Model cho request nhận ảnh dạng base64"""
    source_image: str  # Base64 encoded image
    target_image: str  # Base64 encoded image


def decode_base64_image(base64_string: str) -> str:
    """Decode base64 string và lưu vào temp file, trả về path"""
    try:
        # Loại bỏ prefix nếu có (data:image/png;base64,...)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Tạo temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(image_data)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"[ERROR] Error decoding base64 image: {str(e)}")


def process_face_swap(source_image_path: str, target_image_path: str):
    """Xử lý face swap và trả về output path"""
    global client
    
    if client is None:
        raise HTTPException(status_code=500, detail="[ERROR] Gradio client not initialized")
    
    try:
        # 1. Upload TARGET image (dùng /update_1 cho single file)
        client.predict(
            file=handle_file(target_image_path),
            api_name="/update_1"
        )

        # 2. Upload SOURCE image (dùng /update cho list files)
        client.predict(
            files=[handle_file(source_image_path)],
            api_name="/update"
        )

        # 3. Run face swap
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

        if not output_path or not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="[ERROR] Failed to create output image")
        
        return output_path
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[ERROR] Error processing face swap: {str(e)}")


@app.post("/face-swap")
async def face_swap_endpoint(request: FaceSwapRequest):
    """
    Endpoint nhận 2 ảnh dạng base64 và trả về ảnh kết quả dạng base64
    """
    source_temp_path = None
    target_temp_path = None
    
    try:
        # Decode base64 images
        source_temp_path = decode_base64_image(request.source_image)
        target_temp_path = decode_base64_image(request.target_image)
        
        # Xử lý face swap
        start_time = time.time()
        output_path = process_face_swap(source_temp_path, target_temp_path)
        elapsed_time = time.time() - start_time
        
        # Đọc ảnh kết quả và encode thành base64
        with open(output_path, 'rb') as f:
            image_data = f.read()
            result_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Cleanup temp files
        if source_temp_path and os.path.exists(source_temp_path):
            os.unlink(source_temp_path)
        if target_temp_path and os.path.exists(target_temp_path):
            os.unlink(target_temp_path)
        
        return JSONResponse(content={
            "success": True,
            "result_image": result_base64,
            "processing_time": round(elapsed_time, 2),
            "message": "Face swap successful"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup temp files nếu có lỗi
        if source_temp_path and os.path.exists(source_temp_path):
            os.unlink(source_temp_path)
        if target_temp_path and os.path.exists(target_temp_path):
            os.unlink(target_temp_path)
        raise HTTPException(status_code=500, detail=f"[ERROR]: {str(e)}")


@app.post("/face-swap/files")
async def face_swap_files_endpoint(
    source_image: UploadFile = File(...),
    target_image: UploadFile = File(...)
):
    """
    Endpoint nhận 2 file ảnh và trả về file ảnh kết quả
    """
    source_temp_path = None
    target_temp_path = None
    
    try:
        # Lưu uploaded files vào temp
        source_temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        source_temp_path.write(await source_image.read())
        source_temp_path.close()
        
        target_temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        target_temp_path.write(await target_image.read())
        target_temp_path.close()
        
        # Xử lý face swap
        start_time = time.time()
        output_path = process_face_swap(source_temp_path.name, target_temp_path.name)
        elapsed_time = time.time() - start_time
        
        # Cleanup temp files
        if source_temp_path and os.path.exists(source_temp_path.name):
            os.unlink(source_temp_path.name)
        if target_temp_path and os.path.exists(target_temp_path.name):
            os.unlink(target_temp_path.name)
        
        # Trả về file ảnh kết quả
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="result.png",
            headers={"X-Processing-Time": str(round(elapsed_time, 2))}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup temp files nếu có lỗi
        if source_temp_path and os.path.exists(source_temp_path.name):
            os.unlink(source_temp_path.name)
        if target_temp_path and os.path.exists(target_temp_path.name):
            os.unlink(target_temp_path.name)
        raise HTTPException(status_code=500, detail=f"[ERROR]: {str(e)}")


@app.get("/health")
async def health_check():
    """Kiểm tra trạng thái API và kết nối với FaceFusion"""
    global client
    if client is None:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "[ERROR] Gradio client not initialized"}
        )
    return JSONResponse(content={
        "status": "healthy",
        "facefusion_url": FACEFUSION_URL,
        "message": "API is running normally"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
