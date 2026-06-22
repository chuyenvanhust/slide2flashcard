# Slide2Flashcard 🚀

Slide2Flashcard là một ứng dụng full-stack (FastAPI + React) giúp tự động trích xuất các thành phần quan trọng từ bài giảng PDF (như biểu đồ, hình ảnh, văn bản, công thức) và chuyển đổi chúng thành các thẻ ghi nhớ (Flashcard) thông qua sự trợ giúp của AI (YOLO & Vision Language Models).

Hệ thống có tích hợp thuật toán **Spaced Repetition (SM-2)** để giúp người dùng ôn tập hiệu quả.

---

## 🛠 Yêu cầu hệ thống (Prerequisites)

Để chạy dự án này trên máy tính cá nhân, bạn cần cài đặt:
1. **Python 3.10+**
2. **[uv](https://github.com/astral-sh/uv)** - Trình quản lý package Python cực nhanh (được khuyên dùng).
3. **Node.js** & **npm** - Dành cho môi trường Frontend.
4. **Git** (tuỳ chọn).

---

## ⚙️ Cài đặt & Khởi chạy Backend

Backend được viết bằng Python/FastAPI. Cơ sở dữ liệu mặc định là SQLite, bảng dữ liệu sẽ được tự động khởi tạo trong lần chạy đầu tiên.

### 1. Cài đặt Ollama & Qwen2.5-VL Model
Dự án sử dụng mô hình Qwen2.5-VL thông qua **Ollama** để tự động phân tích ảnh và sinh nội dung Flashcard.
- Tải và cài đặt Ollama từ trang chủ: [https://ollama.com/](https://ollama.com/)
- Mở Terminal và chạy lệnh sau để tải model về máy:
  ```bash
  ollama pull qwen2.5vl:3b
  ```
*(Hãy đảm bảo ứng dụng Ollama đang được bật và chạy ngầm trước khi sử dụng ứng dụng web).*

### 2. Cài đặt các thư viện Python
Dự án sử dụng `uv` để quản lý môi trường ảo và thư viện thông qua `pyproject.toml` và `uv.lock`. Mở Terminal ở thư mục gốc của dự án (`slide2flashcard/`) và chạy:

```bash
uv sync
```
*Lệnh này sẽ tự động tạo thư mục `.venv` và tải toàn bộ các package cần thiết.*

### 3. Khởi chạy Server Backend
Sử dụng `uv run` để chạy file `main.py` của backend. Server sẽ khởi chạy tại cổng **8000**:

```bash
uv run backend/main.py
```
*Sau khi server chạy thành công, bạn có thể truy cập tài liệu API tự động (Swagger UI) tại: http://localhost:8000/docs*

---

## 🎨 Cài đặt & Khởi chạy Frontend

Frontend được phát triển bằng React + Vite, mang lại trải nghiệm UI/UX hiện đại và mượt mà.

### 1. Di chuyển vào thư mục frontend
Mở một tab Terminal mới và trỏ vào thư mục `frontend`:

```bash
cd frontend
```

### 2. Cài đặt các Node Modules
```bash
npm install
```

### 3. Khởi chạy Server Frontend (Development mode)
```bash
npm run dev
```
*Vite server sẽ khởi chạy, thường mặc định ở địa chỉ: http://localhost:5173. Bạn chỉ cần click vào link hiển thị trên Terminal để trải nghiệm ứng dụng!*

---

## 📁 Cấu trúc thư mục tham khảo

- `/backend/`: Chứa mã nguồn FastAPI, Models, Schemas, và API Routers.
- `/frontend/`: Chứa mã nguồn React, Vite, và giao diện UI.
- `/ml/`: Chứa các script hoặc models hỗ trợ trích xuất (YOLO...).
- `/storage/`: Chứa các file PDF upload và ảnh Flashcard sinh ra (được tạo tự động khi chạy app).
- `pyproject.toml` / `uv.lock`: Quản lý dependencies cho backend.
