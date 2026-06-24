import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.src.content.engine import CardGenerator

def test_content_module():
    # 1. Đường dẫn ảnh test
    SAMPLE_IMAGE_PATH = "C:/Users/trumx/Downloads/Screenshot 2026-05-31 195757.png"
    
    # 2. Tạo MOCK_ITEM thay vì chỉ truyền chuỗi đường dẫn
    MOCK_ITEM = {
        "crop_path": SAMPLE_IMAGE_PATH,
        "source_pdf": "HBase_Lecture.pdf",
        "page_number": 7,
        "label": "Diagram"
    }

    MOCK_CONTEXT = {
        "p1": "Hbase column family HBase data stores consist of one or more tables...",
        "p2": "Hbase column family • HBase data stores consist of one or more tables...",
        "p3": "Hbase column family"
    }

    if not os.path.exists(SAMPLE_IMAGE_PATH):
        print(f"❌ Không tìm thấy ảnh test tại {SAMPLE_IMAGE_PATH}")
        return

    print(f"🚀 Đang chạy Module 3 (VLM Content) với mô hình Ollama...")
    
    generator = CardGenerator(model_name=" qwen2.5vl:3b") 
    
    try:
        # TRUYỀN MOCK_ITEM VÀO ĐÂY
        response = generator.generate(MOCK_ITEM, MOCK_CONTEXT)
        print("\n--- NỘI DUNG MẶT SAU FLASHCARD ---")
        print(response)
    except Exception as e:
        # In chi tiết lỗi để debug nếu cần
        import traceback
        traceback.print_exc() 
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    test_content_module()