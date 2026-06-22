# Slide2Flashcard — Cấu trúc dự án

## Tổng quan

Pipeline tự động tạo flashcard từ slide bài giảng (PDF) sử dụng các công nghệ Trí tuệ Nhân tạo hiện đại:
- **Mặt trước:** Hình ảnh của Sơ đồ (Diagram) / Biểu đồ (Chart) / Bảng (Table) / Công thức (Formula) được tự động phát hiện và cắt ra từ slide.
- **Mặt sau:** Câu giải thích ngắn gọn, súc tích (dưới 25 từ) về ý nghĩa của hình ảnh đó, do Vision-Language Model (VLM) tổng hợp từ ảnh và nội dung text xung quanh.
- **App:** Ứng dụng ôn tập Flashcard hỗ trợ lặp lại ngắt quãng (Spaced Repetition - SM-2).

---

## Cấu trúc thư mục hiện tại

```text
slide2flashcard/
│
├── ml/                            ← Toàn bộ ML code và Pipeline (Độc lập)
│   ├── config.yaml                ← File cấu hình (đường dẫn model, settings)
│   ├── main.py                    ← FastAPI Server xử lý ML ngầm (BackgroundTasks)
│   ├── pipeline.py                ← Lớp điều phối FlashcardPipeline (Orchestrator)
│   ├── run_pipeline.py            ← Script chạy test pipeline trực tiếp không cần server
│   ├── data/                      ← File dữ liệu mẫu để test (.pdf)
│   ├── outputs/                   ← Folder chứa file tạm (temp_pdf_imgs)
│   ├── storage/                   ← Chứa file upload và ảnh đã crop để host static
│   │   ├── crops/                 ← Ảnh mặt trước thẻ nhớ
│   │   └── uploads/               ← File PDF tải lên
│   └── src/                       ← Các Engine xử lý lõi
│       ├── crop_diagram/          ← Bước 1: Phát hiện & Cắt ảnh (YOLO)
│       ├── ocr_text/              ← Bước 2: Trích xuất ngữ cảnh chữ (PyMuPDF)
│       ├── content/               ← Bước 3: AI sinh câu giải thích (Ollama VLM)
│       └── common/                ← Các hàm tiện ích dùng chung (Utility)
│
├── backend/                       ← FastAPI (Chính) quản lý User, Deck, Review (SM-2)
└── frontend/                      ← React + Vite (Giao diện hiển thị và ôn tập)
```

---

## Chi tiết Pipeline ML (`ml/`)

Kiến trúc ML được chia làm 3 bước nối tiếp nhau thông qua `pipeline.py`.

### Bước 1: `ml/src/crop_diagram/` — Phát hiện và cắt đối tượng
**Mô hình:** YOLO (Fine-tuned, mặc định `yolo11n.pt` hoặc `prod_best.pt`)
**Thư viện:** `ultralytics`, `PyMuPDF` (`fitz`), `OpenCV`

- **Nhiệm vụ:** Tìm và cắt các khu vực có chứa hình ảnh quan trọng trên slide.
- **Hoạt động:**
  - `PyMuPDF` chuyển đổi trang PDF thành hình ảnh (nhân đôi độ phân giải để YOLO nhìn rõ hơn).
  - YOLO quét và phát hiện các đối tượng.
  - **Logic gộp ranh giới (Bounding Box Merging):** Gom các hộp đè lên nhau hoặc nằm cạnh nhau (ví dụ chữ trong sơ đồ và khung ngoài) thành một khu vực lớn nhất bao trùm toàn bộ hình.
  - Thêm khoảng lề (padding) 10px để ảnh cắt không bị quá sát.
  - Cắt và lưu thành file `.png` vào thư mục `storage/crops/`.

### Bước 2: `ml/src/ocr_text/` — Trích xuất ngữ cảnh (Context Extractor)
**Thư viện:** `PyMuPDF` (`fitz`)

- **Nhiệm vụ:** Lấy các chữ (text) xung quanh khu vực bức ảnh vừa được cắt để làm cơ sở cho AI hiểu bức ảnh nói về điều gì.
- **Hoạt động:** Chuyển đổi tọa độ YOLO về tọa độ PDF và lấy ra 3 luồng thông tin:
  - **P1:** Text nằm trong vùng mở rộng ±60 pixel xung quanh ảnh (thường sẽ bắt được các dòng Caption ngay dưới ảnh).
  - **P2:** Toàn bộ text trên trang slide đó.
  - **P3:** Tiêu đề của trang slide (Block text đầu tiên).

### Bước 3: `ml/src/content/` — Sinh nội dung mặt sau (AI Generator)
**Mô hình:** Vision-Language Model cục bộ (Local VLM) thông qua **Ollama** (như `qwen2.5vl:3b` hoặc `moondream`).

- **Nhiệm vụ:** Kết hợp hình ảnh mặt trước và text ngữ cảnh để tạo ra một câu giải thích súc tích bằng tiếng Việt.
- **Hoạt động:** 
  - Đưa ảnh đã crop và ngữ cảnh (`P1`, `P3`) vào mô hình.
  - Sử dụng prompt đặc chế với các ràng buộc khắt khe: Giải thích bằng tiếng Việt, dưới 25 từ, đúng 1 câu, KHÔNG sao chép nguyên văn slide, KHÔNG liệt kê dạng bullet. AI bắt buộc phải "tóm tắt bản chất" của hình ảnh.

---

## Luồng xử lý Data Flow (Backend + ML)

```text
[Người dùng upload file PDF]
         ↓
POST /upload (tại ml/main.py)
         ↓
FastAPI lưu file vào storage/uploads/ và trả về task_id ngay lập tức
         ↓
[Background Task (background_process_pdf)]
         ↓
Khởi tạo FlashcardPipeline(limit=30)
         ↓
1. cropper.run()      ← Quét toàn bộ trang, YOLO nhận diện và cắt ảnh (trả về danh sách)
2. Lọc & Random mẫu   ← Chọn ngẫu nhiên tối đa 30 ảnh để tránh quá tải AI
3. Vòng lặp từng ảnh:
   a. extractor.get_context() ← PyMuPDF lấy text xung quanh ảnh (P1, P2, P3)
   b. generator.generate()    ← Ollama đọc ảnh và ngữ cảnh, sinh text mặt sau
         ↓
Đóng gói JSON (id, front_url, back_text, page)
         ↓
Cập nhật trạng thái task thành "completed"
         ↓
[Frontend gọi GET /results/{task_id}]
Lấy danh sách flashcard về lưu vào Database (SQLite) và bắt đầu quá trình ôn tập (SM-2).
```

---

## Tech Stack hiện tại

| Layer | Công nghệ |
|---|---|
| **Computer Vision / Crop** | YOLO (Ultralytics), OpenCV |
| **PDF Parsing & OCR** | PyMuPDF (`fitz`) |
| **Text Generation (AI)** | Ollama (Local Vision-Language Models như Qwen2.5-VL) |
| **ML Backend Server** | FastAPI, Uvicorn, BackgroundTasks |
| **Main Backend** | FastAPI, SQLAlchemy, SQLite |
| **Frontend** | React, Vite, Tailwind CSS, Zustand |

---

## Các hàm API chính của ML Server (`ml/main.py`)

- **`POST /upload`**: Gửi file PDF lên để bắt đầu tiến trình phân tích. Trả về `task_id`.
- **`GET /status/{task_id}`**: Polling để lấy phần trăm tiến độ xử lý (% progress).
- **`GET /results/{task_id}`**: Lấy danh sách flashcard hoàn chỉnh khi task đã chạy xong.
- **`Thư mục tĩnh (/static)`**: Phục vụ các file ảnh trong `storage/` để frontend có thể hiển thị ảnh mặt trước của flashcard (`<img src="http://localhost:8000/static/crops/...png" />`).
