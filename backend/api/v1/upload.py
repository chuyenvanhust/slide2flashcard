import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session

# Import công cụ Database và Model
from core.database import SessionLocal
from core.dependencies import get_db
from models.deck import Deck
from models.flashcard import Flashcard
from models.processing_job import ProcessingJob

# Import Pipeline ML của bạn
from ml.pipeline import FlashcardPipeline

router = APIRouter(prefix="/upload", tags=["Upload & Process"])

# Setup absolute paths relative to backend package
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
STORAGE_DIR = os.path.join(ROOT_DIR, "storage")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
CROPS_DIR = os.path.join(STORAGE_DIR, "crops")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CROPS_DIR, exist_ok=True)


def process_pdf_and_save_to_db(task_id: str, pdf_path: str, filename: str):
    db = SessionLocal()
    try:
        # 1. CẬP NHẬT TRẠNG THÁI TIẾN TRÌNH
        job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
        if job:
            job.status = "processing"
            job.progress = 10
            job.message = "Đang quét PDF..."
            db.commit()
        
        # Gọi ML XỬ LÝ
        pipeline = FlashcardPipeline(limit=30)
        results = pipeline.run(pdf_path, output_base_dir=CROPS_DIR)
        
        # Lấy lại bản ghi job để cập nhật tiếp
        job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()

        if not results:
            if job:
                job.status = "failed"
                job.error = "Không tìm thấy sơ đồ nào trong file PDF."
                db.commit()
            return
            
        if job:
            job.progress = 80
            job.message = "Đang lưu vào Database..."
            db.commit()
        
        # 2. LƯU VÀO DATABASE
        new_deck = Deck(name=filename, source_file=pdf_path)
        db.add(new_deck)
        db.commit()
        db.refresh(new_deck)

        # Lưu từng Flashcard ML vừa tạo ra vào Deck này
        for card in results:
            relative_path = os.path.relpath(card['front'], CROPS_DIR).replace('\\', '/')
            relative_url = f"/static/crops/{relative_path}"

            new_card = Flashcard(
                deck_id=new_deck.id,
                image_path=relative_url,
                back_text=card['back_text'],
                card_type=card.get('card_type', 'diagram'),
                source_page=card['page']
            )
            db.add(new_card)
            
        # Cập nhật tổng số lượng thẻ cho bộ bài
        new_deck.total_cards = len(results)
        db.commit()
        
        # 3. BÁO CÁO HOÀN THÀNH
        job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
        if job:
            job.status = "done"
            job.progress = 100
            job.message = f"Hoàn thành! Đã tạo {len(results)} thẻ."
            db.commit()
            
        print(f"✅ Đã xử lý xong {filename} và lưu {len(results)} thẻ vào Database!")

    except Exception as e:
        db.rollback()
        job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            db.commit()
        print(f"❌ Lỗi khi xử lý ML: {e}")
    finally:
        db.close()


@router.post("/")
async def upload_pdf(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
    
    # Lưu file PDF tạm thời
    task_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOADS_DIR, f"{task_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Khởi tạo trạng thái ban đầu trong DB
    job = ProcessingJob(
        id=task_id,
        status="pending",
        progress=0,
        message="Đang chuẩn bị xử lý..."
    )
    db.add(job)
    db.commit()
    
    filename = file.filename or "uploaded_file.pdf"
    # Đẩy việc gọi ML và lưu Database vào chạy ngầm (KHÔNG truyền db request vào)
    background_tasks.add_task(process_pdf_and_save_to_db, task_id, file_path, filename)
    
    return {"job_id": task_id, "message": "File đã được nhận."}


@router.get("/status/{task_id}")
async def get_job_status(task_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình")
    return job