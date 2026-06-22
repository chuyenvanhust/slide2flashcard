# ml/utils.py
import shutil
import os

def cleanup_unused_crops(pdf_hash, kept_paths):
    """
    Xóa tất cả các ảnh crop trong folder pdf_hash ngoại trừ 30 ảnh được chọn.
    """
    base_dir = os.path.join("storage/crops", pdf_hash)
    if not os.path.exists(base_dir):
        return

    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)
        if file_path not in kept_paths:
            os.remove(file_path)
    print(f"🧹 Đã dọn dẹp folder {pdf_hash}, chỉ giữ lại các ảnh flashcard.")