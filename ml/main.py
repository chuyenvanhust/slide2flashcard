#ml\main.py
import os
import uuid
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import pipeline đã viết ở các bước trước
from ml.pipeline import FlashcardPipeline

app = FastAPI(title="Slide2Flashcard API")

# 1. Cấu hình lưu trữ và phục vụ file tĩnh
# Folder này sẽ chứa các ảnh đã crop để hiển thị lên Web
STORAGE_DIR = "storage"
CROPS_DIR = os.path.join(STORAGE_DIR, "crops")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")

os.makedirs(CROPS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount thư mục static để có thể truy cập ảnh qua URL: http://localhost:8000/static/...
app.mount("/static", StaticFiles(directory=STORAGE_DIR), name="static")

# Biến tạm để lưu trạng thái xử lý (Trong thực tế nên dùng Redis hoặc Database)
tasks_status = {}

class TaskResponse(BaseModel):
    task_id: str
    message: str

class Flashcard(BaseModel):
    id: str
    front_url: str
    back_text: str
    page: int

# --- LOGIC XỬ LÝ NGẦM (ĐÃ SỬA) ---
def background_process_pdf(task_id: str, pdf_path: str):
    try:
        tasks_status[task_id] = {"status": "processing", "progress": 10}
        
        # Sửa lỗi 1: Ép Pipeline lưu vào đúng folder mà FastAPI đang phục vụ
        # Giả sử bạn cập nhật class Pipeline để nhận output_dir
        pipeline = FlashcardPipeline(limit=30)
        
        # Đảm bảo hàm run nhận thêm output_base_dir nếu cần, 
        # hoặc mặc định trong engine.py đã sửa thành STORAGE_DIR
        results = pipeline.run(pdf_path)
        
        final_cards = []
        for card in results:
            # Sửa lỗi 2 & 3: Lấy tên file và folder an toàn hơn
            # card['front'] thường là: storage/crops/ten_slide/anh.png
            parts = card['front'].replace('\\', '/').split('/crops/')
            relative_path = parts[-1] if len(parts) > 1 else os.path.basename(card['front'])

            final_cards.append({
                "id": card['id'],
                "front_url": f"/static/crops/{relative_path}", # URL chuẩn để Web hiển thị
                "back_text": card['back'],
                "page": card['page'] # Đồng bộ với key từ Pipeline
            })
            
        tasks_status[task_id] = {
            "status": "completed", 
            "progress": 100, 
            "cards": final_cards
        }
        
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # In lỗi chi tiết ra terminal để debug
        tasks_status[task_id] = {"status": "failed", "error": str(e)}

@app.post("/upload", response_model=TaskResponse)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
    
    # Tạo định danh duy nhất cho tác vụ
    task_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOADS_DIR, f"{task_id}_{file.filename}")
    
    # Lưu file PDF người dùng gửi lên
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Thêm tác vụ vào hàng đợi chạy ngầm
    tasks_status[task_id] = {"status": "pending", "progress": 0}
    background_tasks.add_task(background_process_pdf, task_id, file_path)
    
    return {
        "task_id": task_id, 
        "message": "File đã nhận. Đang tiến hành phân tích slide (500 trang mất khoảng 4-5 phút)..."
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = tasks_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Không tìm thấy Task ID")
    return status

@app.get("/results/{task_id}", response_model=List[Flashcard])
async def get_results(task_id: str):
    task = tasks_status.get(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Tác vụ chưa hoàn thành hoặc không tồn tại")
    return task["cards"]

if __name__ == "__main__":
    import uvicorn
    # Chạy server tại port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)