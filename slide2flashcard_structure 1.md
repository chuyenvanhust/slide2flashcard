# Slide2Flashcard — Cấu trúc dự án

## Tổng quan

Pipeline tự động tạo flashcard từ slide bài giảng PDF:
- **Mặt trước:** Diagram / Chart / Table / Formula (phát hiện bằng ML)
- **Mặt sau:** Text giải thích liên quan (match bằng CLIP)
- **App:** Flashcard study với spaced repetition (SM-2)

---

## Cấu trúc thư mục

```
slide2flashcard/
│
├── ml/                            ← Toàn bộ ML code, tách riêng khỏi app
│   ├── diagram_classifier/        ← ML1: Phân loại ảnh
│   └── clip_matcher/              ← ML2: Match diagram với text
│
├── backend/                       ← FastAPI
├── frontend/                      ← React + Vite
├── data/                          ← Runtime data (gitignore)
└── scripts/                       ← Utility scripts
```

---

## Chi tiết từng phần

### `ml/diagram_classifier/` — ML1: EfficientNet-B0

**Bài toán:** Phân loại ảnh extract từ slide thành 5 class

```
diagram | chart | table | formula | other(bỏ qua)
```

```
ml/diagram_classifier/
├── data/
│   ├── raw/                       ← Ảnh extract thô từ slide PDF
│   ├── annotated/                 ← Ảnh đã gán nhãn thủ công
│   │   ├── diagram/               ← ~300 ảnh
│   │   ├── chart/                 ← ~300 ảnh
│   │   ├── table/                 ← ~300 ảnh
│   │   ├── formula/               ← ~200 ảnh
│   │   └── other/                 ← ~200 ảnh
│   └── splits/
│       ├── train.json             ← 70% — stratified theo bộ slide
│       ├── val.json               ← 15%
│       └── test.json              ← 15%
│
├── configs/
│   └── train_config.yaml          ← lr, batch_size, epochs, augmentation
│
├── src/
│   ├── extract_from_pdf.py        ← PyMuPDF: extract raw images
│   ├── dataset.py                 ← DiagramDataset (torch.utils.data.Dataset)
│   ├── model.py                   ← EfficientNet-B0 + custom classification head
│   ├── train.py                   ← Training loop + WandB logging
│   ├── evaluate.py                ← F1/class, confusion matrix, Grad-CAM
│   └── predict.py                 ← Inference: nhận ảnh → trả class + confidence
│
├── notebooks/
│   ├── 01_data_exploration.ipynb  ← Phân bố class, visualize samples
│   ├── 02_training_analysis.ipynb ← Loss curves, metrics theo epoch
│   └── 03_error_analysis.ipynb    ← Xem ảnh bị classify sai
│
├── weights/
│   ├── best_model.pt              ← Best checkpoint (theo val Macro F1)
│   └── last_model.pt
│
└── requirements.txt
```

**Training details:**
| | |
|---|---|
| Base model | EfficientNet-B0 (pretrained ImageNet) |
| Baseline so sánh | ResNet-50 + Rule-based (size threshold) |
| Loss | Weighted CrossEntropy (handle class imbalance) |
| Augmentation | Flip, Rotate±10°, ColorJitter, RandomGrayscale |
| Strategy | Freeze backbone 5 epoch → unfreeze toàn bộ |

**Metrics:**
| Metric | Mục tiêu | Ý nghĩa |
|---|---|---|
| Per-class F1 | ≥ 0.78 mỗi class | Class nào model yếu |
| Macro F1 | ≥ 0.80 | Overall performance |
| Confusion Matrix | Visualize | Nhầm loại nào với loại nào |
| AUC-ROC | ≥ 0.90 | Khả năng phân biệt |

---

### `ml/clip_matcher/` — ML2: CLIP Fine-tune

**Bài toán:** Cho diagram → tìm text block liên quan nhất trong slide và slide liền kề

```
ml/clip_matcher/
├── data/
│   ├── raw_pairs/                 ← (image_path, text) chưa filter
│   ├── positive_pairs.json        ← (diagram, text giải thích trực tiếp)
│   ├── negative_pairs.json        ← (diagram, text không liên quan)
│   └── splits/
│       ├── train.json
│       ├── val.json
│       └── test.json
│
├── configs/
│   └── finetune_config.yaml       ← lr, batch, temperature, margin
│
├── src/
│   ├── dataset.py                 ← CLIPPairDataset
│   ├── model.py                   ← CLIP wrapper + projection heads
│   ├── losses.py                  ← InfoNCE loss, Contrastive loss
│   ├── train.py                   ← Fine-tune loop
│   ├── evaluate.py                ← Precision@K, NDCG, MRR
│   ├── zero_shot_baseline.py      ← CLIP gốc (baseline để so sánh)
│   └── match_diagram_text.py      ← Inference: diagram → top-K text blocks
│
├── notebooks/
│   ├── 01_baseline_clip.ipynb     ← Zero-shot CLIP performance
│   ├── 02_finetune_analysis.ipynb ← So sánh trước/sau fine-tune
│   └── 03_retrieval_examples.ipynb← Visualize diagram + matched text
│
├── weights/
│   ├── clip_finetuned.pt
│   └── clip_baseline_scores.json  ← Zero-shot scores để so sánh
│
└── requirements.txt
```

**Metrics:**
| Metric | Ý nghĩa |
|---|---|
| Precision@1 | Text đúng có là #1 không |
| Precision@3 | Text đúng có trong top 3 không |
| NDCG@5 | Ranking quality tổng thể |
| MRR | Mean Reciprocal Rank |

---

### `backend/` — FastAPI

```
backend/
├── main.py                        ← FastAPI app, lifespan, middleware
├── requirements.txt
├── .env
│
├── core/
│   ├── config.py                  ← Settings (Pydantic BaseSettings)
│   ├── database.py                ← SQLite engine, SessionLocal, Base
│   └── dependencies.py            ← get_db(), get_classifier(), get_matcher()
│
├── models/                        ← SQLAlchemy ORM
│   ├── deck.py                    ← Deck: id, name, source_pdf, created_at
│   ├── flashcard.py               ← Flashcard: id, deck_id, image_path,
│   │                                  back_text, card_type, source_page
│   ├── review.py                  ← Review: card_id, rating, reviewed_at,
│   │                                  next_review, interval, ease_factor
│   └── user_progress.py           ← Progress: deck_id, total/known/due count
│
├── schemas/                       ← Pydantic (request/response)
│   ├── deck.py
│   ├── flashcard.py
│   └── review.py
│
├── api/v1/
│   ├── router.py                  ← Include tất cả routes
│   ├── upload.py                  ← POST /upload  → tạo deck từ PDF
│   │                                  GET  /upload/status/{job_id}
│   ├── decks.py                   ← GET    /decks
│   │                                  GET    /decks/{id}
│   │                                  DELETE /decks/{id}
│   ├── flashcards.py              ← GET /decks/{id}/cards
│   │                                  GET /decks/{id}/cards/due  ← do SM-2
│   │                                  PUT /cards/{id}            ← edit back text
│   └── reviews.py                 ← POST /cards/{id}/review
│                                       body: {rating: "easy"|"medium"|"hard"|"again"}
│
├── services/
│   ├── pdf_processor.py           ← Điều phối pipeline xử lý PDF
│   ├── diagram_classifier.py      ← Load weights ML1, batch inference
│   ├── text_extractor.py          ← PaddleOCR + extract context window
│   │                                  (text trong slide + slide ±1)
│   ├── clip_matcher.py            ← Load weights ML2, match diagram→text
│   ├── flashcard_builder.py       ← Ghép front(image)+back(text) → flashcard
│   └── spaced_repetition.py       ← SM-2 algorithm
│                                       next_interval(ease, interval, rating)
│
└── storage/
    ├── file_storage.py            ← Save/load ảnh diagram
    └── uploads/                   ← PDF tạm thời
```

**API endpoints tóm tắt:**

| Method | Endpoint | Chức năng |
|---|---|---|
| POST | `/api/v1/upload` | Upload PDF → bắt đầu pipeline |
| GET | `/api/v1/upload/status/{job_id}` | Poll tiến trình |
| GET | `/api/v1/decks` | Danh sách tất cả deck |
| GET | `/api/v1/decks/{id}` | Chi tiết deck + stats |
| GET | `/api/v1/decks/{id}/cards` | Tất cả flashcard trong deck |
| GET | `/api/v1/decks/{id}/cards/due` | Cards đến hạn ôn tập (SM-2) |
| POST | `/api/v1/cards/{id}/review` | Submit kết quả học |
| PUT | `/api/v1/cards/{id}` | Sửa text mặt sau |
| DELETE | `/api/v1/decks/{id}` | Xóa deck |

**Database schema:**

```
Deck               Flashcard              Review
────────────       ────────────────────   ──────────────────────
id (PK)            id (PK)                id (PK)
name               deck_id (FK)           card_id (FK)
source_file        image_path             rating        ← easy/medium/hard/again
total_cards        back_text              reviewed_at
created_at         card_type             next_review    ← SM-2 output
                   source_page           interval       ← ngày
                   confidence            ease_factor    ← SM-2 E-factor
                   created_at
```

---

### `frontend/` — React + Vite

```
frontend/src/
│
├── pages/
│   ├── Home.jsx                   ← Grid danh sách deck + nút upload
│   ├── DeckDetail.jsx             ← Xem tất cả card trong deck, filter
│   ├── StudySession.jsx           ← Màn hình học chính
│   ├── Upload.jsx                 ← Upload PDF + progress pipeline
│   └── Stats.jsx                  ← Biểu đồ tiến độ học
│
├── components/
│   │
│   ├── flashcard/
│   │   ├── FlashCard.jsx          ← CSS 3D flip animation
│   │   │                             click → lật từ mặt trước sang mặt sau
│   │   ├── CardFront.jsx          ← Hiển thị ảnh diagram/chart/table/formula
│   │   │                             badge góc: loại card (diagram/chart/...)
│   │   ├── CardBack.jsx           ← Text giải thích + source page info
│   │   └── RatingButtons.jsx      ← 4 nút sau khi xem mặt sau:
│   │                                  [Chưa biết] [Khó] [Trung bình] [Dễ]
│   │
│   ├── deck/
│   │   ├── DeckCard.jsx           ← Preview deck: tên, số card, % đã biết
│   │   ├── DeckList.jsx           ← Grid layout danh sách deck
│   │   └── DeckProgress.jsx       ← Progress bar: new/learning/known
│   │
│   ├── upload/
│   │   ├── UploadZone.jsx         ← Drag & drop PDF
│   │   └── ProcessingStatus.jsx   ← Stepper: Extract→Classify→Match→Done
│   │
│   └── common/
│       ├── ProgressBar.jsx
│       ├── LoadingSpinner.jsx
│       └── Badge.jsx              ← Hiển thị card_type label
│
├── hooks/
│   ├── useStudySession.js         ← Logic học:
│   │                                  - fetch due cards
│   │                                  - flip state
│   │                                  - submit rating → SM-2
│   │                                  - next card
│   ├── useDeck.js                 ← Fetch + cache deck data
│   └── useUpload.js               ← Upload file + polling status
│
├── store/ (Zustand)
│   ├── deckStore.js               ← decks list, current deck
│   └── studyStore.js              ← session state, current card, flip state
│
└── api/client.js                  ← Axios instance, tất cả API calls
```

**Study Session flow:**

```
User vào StudySession
        ↓
Fetch /cards/due  ← cards đến hạn theo SM-2
        ↓
Hiển thị CardFront (diagram/chart/table/formula)
        ↓
User click → Flip → CardBack (text giải thích)
        ↓
User chọn rating:
  [Chưa biết] → interval = 1 ngày,  ease giảm
  [Khó]       → interval giữ nguyên, ease giảm nhẹ
  [Trung bình]→ interval × ease_factor
  [Dễ]        → interval × ease_factor × 1.3
        ↓
POST /cards/{id}/review → SM-2 tính next_review
        ↓
Card tiếp theo
```

---

### `scripts/` — Utility

```
scripts/
├── extract_images_for_annotation.py   ← Batch extract ảnh từ nhiều PDF
│                                          → output vào ml/diagram_classifier/data/raw/
├── prepare_clip_pairs.py              ← Tạo positive/negative pairs
│                                          dùng Ollama để generate silver labels
├── evaluate_pipeline.py               ← End-to-end: PDF → flashcard accuracy
└── seed_demo_data.py                  ← Tạo demo deck để test UI
```

---

## Data Flow tổng thể

```
User upload PDF
      ↓
[pdf_processor.py]
  PyMuPDF extract: ảnh + text từng trang
      ↓
[diagram_classifier.py]  ← load ML1 weights
  EfficientNet classify từng ảnh
  Giữ lại: diagram / chart / table / formula
  Bỏ qua: other
      ↓
[text_extractor.py]
  PaddleOCR đọc text các slide
  Tạo context window: text slide hiện tại + slide ±1
      ↓
[clip_matcher.py]  ← load ML2 weights
  CLIP fine-tuned match diagram → top-3 text blocks
  Lấy text có relevance_score cao nhất
      ↓
[flashcard_builder.py]
  Front: image file
  Back:  matched text + source page info
  Save vào SQLite + images/
      ↓
React app hiển thị flashcard
User học với SM-2 spaced repetition
```

---

## Tech Stack

| Layer | Tech |
|---|---|
| ML Training | PyTorch, HuggingFace, WandB |
| ML Models | EfficientNet-B0, CLIP (ViT-B/32) |
| OCR | PaddleOCR |
| PDF Parse | PyMuPDF |
| Backend | FastAPI, SQLAlchemy, SQLite |
| Frontend | React, Vite, Zustand |
| Styling | Tailwind CSS |
| Dev | Docker Compose |
