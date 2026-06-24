import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import cấu hình Database và các API Routers sau khi sys.path đã được thiết lập
from core.database import engine, Base
from api.v1 import upload, decks, flashcards, reviews

# ==============================================================================
# 2. KHỞI TẠO ĐƯỜNG DẪN LƯU TRỮ VÀ TỰ ĐỘNG TẠO BẢNG DATABASE
# ==============================================================================
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BACKEND_DIR)
STORAGE_DIR = os.path.join(PARENT_DIR, "storage")
CROPS_DIR = os.path.join(STORAGE_DIR, "crops")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")

# Đảm bảo các thư mục lưu trữ PDF và ảnh crop luôn tồn tại
os.makedirs(CROPS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


from models.deck import Deck
from models.flashcard import Flashcard
from models.review import Review
from models.user_progress import UserProgress
from models.processing_job import ProcessingJob
# Tự động quét các Models (Deck, Flashcard, Review...) và tạo bảng trong SQLite nếu chưa có
Base.metadata.create_all(bind=engine)

# ==============================================================================
# 3. CẤU HÌNH FASTAPI APP & MIDDLEWARE
# ==============================================================================
app = FastAPI(
    title="Slide2Flashcard API",
    description="Backend điều phối pipeline tạo flashcard tự động từ slide bài giảng PDF sử dụng YOLO và Qwen VLM.",
    version="1.0.0"
)

# Cấu hình CORS để cho phép Frontend (React/Vite chạy ở port 3000 hoặc 5173) gọi API xuống
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường sản phẩm thực tế nên giới hạn cụ thể domain của frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount thư mục static phục vụ việc hiển thị ảnh mặt trước flashcard lên trình duyệt
# URL truy cập ảnh sẽ có dạng: http://localhost:8000/static/crops/ten_file_anh.png
app.mount("/static", StaticFiles(directory=STORAGE_DIR), name="static")
app.mount("/backend/storage", StaticFiles(directory=STORAGE_DIR), name="backend_storage")
# ==============================================================================
# 4. ĐĂNG KÝ CÁC API ROUTERS V1
# ==============================================================================
app.include_router(upload.router, prefix="/api/v1")
app.include_router(decks.router, prefix="/api/v1")
app.include_router(flashcards.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root_check():
    """Endpoint kiểm tra trạng thái hoạt động của server."""
    return {
        "status": "online",
        "message": "Slide2Flashcard API đang hoạt động mượt mà!",
        "monorepo_root": ROOT_DIR
    }

# ==============================================================================
# 5. KHỞI CHẠY SERVER
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Chạy server tại port 8000, reload=True tự động khởi động lại khi bạn sửa code backend
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)