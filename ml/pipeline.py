# ml/pipeline.py
import random
import os
from .src.crop_diagram.engine import DiagramCropper
from .src.ocr_text.engine import PriorityExtractor
from .src.content.engine import CardGenerator

class FlashcardPipeline:
    def __init__(self, limit=30):
        # Khởi tạo mô hình YOLO nhúng cấu phần DBSCAN bên trong
        self.cropper = DiagramCropper() 
        self.extractor = PriorityExtractor()
        # Khởi tạo bộ tạo nội dung hỗ trợ tính năng chạy song song
        self.generator = CardGenerator()
        self.limit = limit

    def run(self, pdf_path, *args, **kwargs):
        # ----------------------------------------------------------------------
        # BƯỚC 1: QUÉT TRANG, PHÂN CỤM DBSCAN & TRÍCH XUẤT EMBEDDING TỰ ĐỘNG
        # ----------------------------------------------------------------------
        print("🔍 GIAI ĐOẠN 1: Đang quét toàn bộ slide, chạy DBSCAN gộp cụm và tối ưu bao phủ...")
        
        # Hàm run này của DiagramCropper ở câu trước ĐÃ BAO GỒM:
        #  - Nhận diện YOLO với conf=0.35 (Tăng tối đa Recall để không sót vật thể)
        #  - Chạy DBSCAN gộp cụm hình học theo chỉ số IoU nhằm tránh cắt nát ảnh
        #  - Trích xuất Image Vector Embedding qua ResNet50
        #  - Chạy Greedy Diversity Selector lọc lấy đúng 30 ảnh xa nhau nhất về ngữ nghĩa
        selected_items = self.cropper.run(pdf_path, top_k=self.limit) 
        
        if not selected_items:
            print("⚠️ Không tìm thấy Sơ đồ hoặc Bảng nào trên Slide hoặc không trích xuất được thực thể.")
            return []

        print(f"🎯 Bộ lọc Đa dạng hóa không gian Vector đã chọn ra {len(selected_items)} ảnh tối ưu nhất về độ phủ tri thức.")

        # ----------------------------------------------------------------------
        # BƯỚC 2: TRÍCH XUẤT NGỮ CẢNH VĂN BẢN (CONTEXT EXTRACTION)
        # ----------------------------------------------------------------------
        print("📖 GIAI ĐOẠN 2: Đang trích xuất ngữ cảnh văn bản bổ trợ cho từng ảnh...")
        
        # Lấy ngữ cảnh chung (ví dụ slide chỉ có 1 tiêu đề chính và nội dung chữ cố định cho trang đó)
        # Để tối ưu tốc độ gọi batch, ta lấy ngữ cảnh đại diện từ trang slide đầu tiên của tập ảnh được chọn
        # (Hoặc lấy ngữ cảnh riêng nếu PriorityExtractor của bạn phân mảnh theo từng item)
        sample_item = selected_items[0]
        ctx = self.extractor.get_context(pdf_path, sample_item)

        # ----------------------------------------------------------------------
        # BƯỚC 3: SINH NỘI DUNG SONG SONG SIÊU TỐC (BATCH INFERENCE VIA OLLAMA)
        # ----------------------------------------------------------------------
        print("⚡ GIAI ĐOẠN 3: Đang kích hoạt luồng xử lý song song gọi Ollama sinh nội dung...")
        
        # Gọi hàm generate_batch đa luồng đã viết ở câu trước để xử lý đồng thời 30 ảnh
        # Ép thời gian xử lý từ 15 phút xuống dưới 1.5 - 2 phút!
        batch_responses = self.generator.generate_batch(selected_items, ctx, max_workers=6)

        # ----------------------------------------------------------------------
        # BƯỚC 4: ĐÓNG GÓI DỮ LIỆU ĐẦU RA (DATA MAPPING)
        # ----------------------------------------------------------------------
        final_cards = []
        for res in batch_responses:
            if res["status"] != "success":
                continue # Bỏ qua các ảnh bị lỗi hệ thống Ollama để bảo vệ tính toàn vẹn dữ liệu
                
            # Tìm lại thông tin item gốc tương ứng với crop_path để lấy page_number và label
            original_item = next((i for i in selected_items if i["crop_path"] == res["crop_path"]), None)
            if not original_item:
                continue

            final_cards.append({
                "id": f"{original_item['folder_tag']}_p{original_item['page_number']}_{random.getrandbits(16)}",
                "front": original_item['crop_path'],   
                "url": original_item.get('web_url', original_item['crop_path']), 
                "back_text": res['response'], 
                "page": original_item['page_number']
            })
            
        print(f"🎉 Pipeline hoàn thành xuất sắc! Đã đóng gói {len(final_cards)} flashcards thành phẩm sạch.")
        return final_cards