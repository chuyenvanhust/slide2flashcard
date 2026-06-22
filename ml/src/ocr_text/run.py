import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.src.ocr_text.engine import PriorityExtractor

def test_ocr_module():
    PDF_TEST = "C:/Users/trumx/Downloads/Thầy Trần Việt Trung-20260311T032147Z-3-001/Thầy Trần Việt Trung/4.5_hbase.pdf"
    extractor = PriorityExtractor()

    # Giả lập một item mà YOLO trả về (ví dụ: một sơ đồ ở giữa trang 0)
    mock_item = {
        "page_number": 7,
        "bbox": [100, 100, 500, 400], # [x1, y1, x2, y2] tọa độ trên ảnh render 2x
        "label": "diagram"
    }

    if not os.path.exists(PDF_TEST):
        print("❌ Vui lòng để file PDF test vào ml/data/test_slide.pdf")
        return

    print(f"🚀 Đang chạy Module 2 (OCR Priority) cho Trang {mock_item['page_number']}...")
    context = extractor.get_context(PDF_TEST, mock_item)

    print("\n--- KẾT QUẢ TRÍCH XUẤT TEXT ---")
    print(f"📍 [P1 - Lân cận]: {context['p1']}")
    print(f"📄 [P2 - Nội dung slide]: {context['p2']}")
    print(f"🔝 [P3 - Tiêu đề]: {context['p3']}")

if __name__ == "__main__":
    test_ocr_module()