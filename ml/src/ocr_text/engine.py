import fitz

class PriorityExtractor:
    def get_context(self, pdf_path, item):
        doc = fitz.open(pdf_path)
        # item['page_number'] là số trang từ 1 -> index = page_number - 1
        page = doc[item['page_number'] - 1]
        page_width = page.rect.width
        # Chuyển tọa độ từ ảnh 2x (YOLO) về tọa độ PDF gốc (1x)
        pdf_bbox = [c/2 for c in item['bbox']]
        
        # P1: Text lân cận (Mở rộng vùng chọn ra 60 pixel để bắt Caption)
        rect_p1 = fitz.Rect(
            0,                      # X_min: Bắt đầu từ lề trái slide
            pdf_bbox[1] - 60,       # Y_min: Mở rộng lên trên 60 pixel
            page_width,             # X_max: Hết lề phải slide
            pdf_bbox[3] + 60        # Y_max: Mở rộng xuống dưới 60 pixel
        )
        p1_text = page.get_text("text", clip=rect_p1).strip()
        
        # P2: Nội dung toàn bộ trang slide
        p2_text = page.get_text("text").strip()
        
        # P3: Tiêu đề trang (Block đầu tiên)
        blocks = page.get_text("blocks")
        p3_text = blocks[0][4].strip() if blocks else "N/A"
        
        doc.close()
        return {
            "p1": p1_text if p1_text else "N/A",
            "p2": p2_text,
            "p3": p3_text
        }