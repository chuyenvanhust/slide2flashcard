# ml/src/content/engine.py
import ollama
import os
from concurrent.futures import ThreadPoolExecutor

class CardGenerator:
    def __init__(self, model_name="qwen2.5vl:3b"):
        self.model_name = model_name

    def generate(self, item, context):
        # GIỮ NGUYÊN HOÀN TOÀN PROMPT GỐC CỦST BẠN
        prompt = f"""
        Bạn là AI tạo flashcard học tập.

        Thông tin slide:
        Tiêu đề: {context['p3']}

        Nội dung:
        {context['p1']}

        Nhiệm vụ:
        Giải thích NGẮN GỌN ý nghĩa kiến thức trong hình bằng 2 câu.

        QUAN TRỌNG:
        - KHÔNG chép lại nguyên văn slide
        - KHÔNG OCR
        - KHÔNG liệt kê bullet
        - Chỉ tóm tắt bản chất kiến thức

        Yêu cầu:
        - Tiếng Việt
        - Tối đa 25 từ
        - 1 câu duy nhất
        - Dễ hiểu cho sinh viên

        Chỉ trả về nội dung lời giải thích.
        """
        
        with open(item['crop_path'], 'rb') as f:
            img_data = f.read()
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                images=[img_data]
            )
        return response['response']

    def _worker_job(self, item, context):
        """Hàm công nhân xử lý an toàn cho từng luồng (Thread)"""
        try:
            if not os.path.exists(item['crop_path']):
                return {
                    "crop_path": item['crop_path'],
                    "status": "error",
                    "response": "❌ Lỗi: Không tìm thấy file ảnh"
                }
            
            # Gọi lại chính hàm generate gốc để đảm bảo tính đồng nhất về prompt và logic xử lý
            res_content = self.generate(item, context)
            
            return {
                "crop_path": item['crop_path'],
                "status": "success",
                "response": res_content
            }
        except Exception as e:
            return {
                "crop_path": item['crop_path'],
                "status": "error",
                "response": f"❌ Lỗi Ollama Thread: {str(e)}"
            }

    def generate_batch(self, final_items, context, max_workers=2, progress_callback=None):
        """
        [HÀM BỔ SUNG] 
        Xử lý đa luồng song song hàng loạt cho danh sách ảnh đã lọc.
        - final_items: Danh sách 30 ảnh đã qua bộ lọc tối ưu bao phủ.
        - context: Dictionary chứa 'p1' và 'p3' của slide.
        - max_workers: Số ảnh được gửi lên Ollama xử lý cùng một lúc (Mặc định: 6).
        """
        import concurrent.futures
        if not final_items:
            return []
            
        print(f"⚡ Đang gửi đồng thời {len(final_items)} ảnh lên Ollama bằng {max_workers} luồng...")
        
        batch_results = []
        # Kích hoạt ThreadPoolExecutor để chạy song song I/O
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Phân phối 30 job vào các luồng độc lập
            futures = [
                executor.submit(self._worker_job, item, context)
                for item in final_items
            ]
            
            total = len(futures)
            # Thu hồi kết quả ngay khi một luồng xử lý xong
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                batch_results.append(future.result())
                if progress_callback:
                    # Trải đều tiến độ từ mốc 40% (Bắt đầu sinh) đến 75% (để nhường 80% cho bước lưu DB)
                    pct = 40 + int(35 * (i + 1) / total)
                    progress_callback(pct, f"Đã sinh xong nội dung cho thẻ {i+1}/{total}...")
                
        print("✅ Đã xử lý đa luồng xong toàn bộ danh sách ảnh thành công!")
        return batch_results