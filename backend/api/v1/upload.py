import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import Optional

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


def process_pdf_and_save_to_db(task_id: str, pdf_path: str, filename: str, deck_id: Optional[int] = None):
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
        
        def on_progress(pct, msg):
            job_update = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
            if job_update:
                job_update.progress = pct
                job_update.message = msg
                db.commit()

        results = pipeline.run(pdf_path, progress_callback=on_progress)
        
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
        if deck_id:
            target_deck = db.query(Deck).filter(Deck.id == deck_id).first()
            if not target_deck:
                target_deck = Deck(name=filename)
                db.add(target_deck)
        else:
            target_deck = Deck(name=filename)
            db.add(target_deck)
            
        db.commit()
        db.refresh(target_deck)

        # Lưu từng Flashcard ML vừa tạo ra vào Deck này
        for card in results:
            relative_path = os.path.relpath(card['front'], CROPS_DIR).replace('\\', '/')
            relative_url = f"/static/crops/{relative_path}"

            new_card = Flashcard(
                deck_id=target_deck.id,
                image_path=relative_url,
                back_text=card['back_text'],
                card_type=card.get('card_type', 'diagram'),
                source_page=card['page'],
                source_file=filename,
                confidence=card.get('confidence', 0.0)
            )
            db.add(new_card)
            
        # Cập nhật tổng số lượng thẻ cho bộ bài
        target_deck.total_cards = (target_deck.total_cards or 0) + len(results)
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
        
        # --- LOGIC DỌN RÁC VẬT LÝ KHI GẶP LỖI ---
        try:
            import re, glob
            # 1. Xóa file PDF upload
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ Đã dọn dẹp file PDF lỗi: {pdf_path}")
                
            # 2. Xóa thư mục ảnh cắt dở trong crops
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            folder_name = re.sub(r'[^\w\s-]', '', base_name).strip().replace(' ', '_')
            crops_folder = os.path.join(CROPS_DIR, folder_name)
            if os.path.exists(crops_folder):
                shutil.rmtree(crops_folder, ignore_errors=True)
                print(f"🗑️ Đã dọn dẹp thư mục ảnh rác: {crops_folder}")
                
            # 3. Xóa các file tạm mắc kẹt trong ml/outputs/temp
            temp_dir = os.path.join(ROOT_DIR, "ml", "outputs", "temp")
            for tf in glob.glob(os.path.join(temp_dir, f"temp_{folder_name}_*")):
                if os.path.exists(tf):
                    os.remove(tf)
        except Exception as cleanup_error:
            print(f"⚠️ Lỗi phụ trong quá trình dọn rác: {cleanup_error}")
        # ---------------------------------------

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
    deck_id: Optional[int] = Form(None),
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
    background_tasks.add_task(process_pdf_and_save_to_db, task_id, file_path, filename, deck_id)
    
    return {"job_id": task_id, "message": "File đã được nhận."}


@router.get("/status/{task_id}")
async def get_job_status(task_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == task_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình")
    return job