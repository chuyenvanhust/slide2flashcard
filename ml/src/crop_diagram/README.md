# crop_diagram

Module phát hiện và cắt ảnh diagram/chart/table/formula từ slide PDF bằng YOLO object detection.

## Mục tiêu

Input là file PDF slide bài giảng. Output là danh sách các vùng ảnh đã được phát hiện và crop, kèm số trang, loại (diagram/table, confidence score, và bounding box gốc.

Đây là module duy nhất trong `ml/` có training thật — YOLO được fine-tune trên slide thật để nhận diện 4 loại nội dung trên, thay vì dùng rule cứng (kích thước, vị trí).

## Cấu trúc

```
crop_diagram/
├── configs/config.yaml      ← cấu hình model, threshold, output path
├── src/detector.py          ← DiagramDetector class — core logic
├── tests/test_manual.py     ← test CLI độc lập
└── outputs/                 ← ảnh crop + JSON kết quả (gitignored)
```

## Cài đặt

```bash
pip install ultralytics PyMuPDF Pillow PyYAML
```

Cần có file weights đã train tại `weights/best.pt`. Nếu chưa có, module tự chuyển sang **mock mode** — trả về 1 detection giả để pipeline phía sau (ocr_text, content) vẫn chạy được trong lúc YOLO chưa train xong.

## Chế độ 1 — Tích hợp với backend

```python
from crop_diagram.src.detector import load_detector

detector = load_detector("configs/config.yaml")
diagrams = detector.detect_pdf(
    pdf_path="slide.pdf",
    output_dir="storage/images/deck_001",
    deck_id="deck_001",
)
# diagrams: list[CroppedDiagram] — đưa thẳng sang module ocr_text
```

`CroppedDiagram` (định nghĩa trong `shared/schemas.py`) chứa: `image_path`, `diagram_type`, `page_num`, `confidence`, `bbox`, `card_id`, `deck_id`. Đây là interface cố định giữa `crop_diagram` và `ocr_text` — không đổi format khi swap model bên trong.

## Chế độ 2 — Test thủ công

```bash
# Detect toàn bộ PDF, lưu ảnh crop + JSON
python tests/test_manual.py --pdf path/to/slide.pdf

# Chỉ vẽ bounding box để kiểm tra bằng mắt, không lưu crop
python tests/test_manual.py --pdf slide.pdf --vis-only

# Test nhanh trên 1 ảnh trang đơn lẻ
python tests/test_manual.py --image page_05.png
```

Output test thủ công:
```
outputs/
├── images/              ← ảnh đã crop, đặt tên {deck}_{page}_{idx}_{type}.png
├── visualized/          ← slide gốc + bounding box vẽ đè lên, để review bằng mắt
└── crops.json           ← metadata đầy đủ, dùng làm input cho ocr_text test
```

## Cấu hình quan trọng (`configs/config.yaml`)

```yaml
model:
  confidence_threshold: 0.25   # detection dưới ngưỡng này bị bỏ
  iou_threshold: 0.4           # NMS — giảm nếu box bị chồng lấp nhiều
pdf:
  dpi: 150                     # tăng lên 200 nếu formula nhỏ bị mất nét
output:
  padding: 8                   # pixel đệm quanh box khi crop
```

