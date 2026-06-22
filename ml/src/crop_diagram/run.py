import os
import sys

# Thêm thư mục gốc vào path để import được module ml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.src.crop_diagram.engine import DiagramCropper

def test_crop_module():
    # 1. Cấu hình file test - Kiểm tra kỹ đường dẫn này
    PDF_TEST = "C:/Users/trumx/Downloads/Thầy Trần Việt Trung-20260311T032147Z-3-001/Thầy Trần Việt Trung/4.6_presto.pdf"
    OUTPUT_DIR = "ml/outputs/test_crops"
    # Cập nhật đường dẫn model mới
    MODEL_PATH = "ml/src/crop_diagram/models/best.pt" 
    
    if not os.path.exists(PDF_TEST):
        print(f"❌ Không tìm thấy file test tại: {PDF_TEST}")
        return

    print(f"🚀 Đang chạy Module 1 (Crop) trên file: {PDF_TEST}")
    
    # Khởi tạo với đường dẫn model chính xác
    cropper = DiagramCropper(model_path=MODEL_PATH)
    
    # Sửa tham số: class DiagramCropper dùng 'output_base_dir', không phải 'output_dir'
    results = cropper.run(PDF_TEST, output_base_dir=OUTPUT_DIR)
    
    print("\n" + "="*30)
    print("--- KẾT QUẢ CROP ---")
    print(f"✅ Đã tìm thấy {len(results)} đối tượng.")
    
    for idx, item in enumerate(results):
        # Lưu ý: Class mới trả về 'page_number', bạn đang gọi 'page_id' (sẽ lỗi nếu không sửa)
        print(f"[{idx+1}] Loại: {item['label']} | Trang: {item['page_number']} | Đường dẫn: {item['crop_path']}")
    print("="*30)

if __name__ == "__main__":
    test_crop_module()