"""
background.py — Tạo nền slide synthetic từ ảnh thật + nhiễu text/hình kỷ hà.

Thay đổi so với bản cũ:
  - Thêm tam giác vào bộ hình kỷ hà (line / rect / circle / triangle).
  - Tăng alpha nhiễu (80-160) và độ dày nét (3-6px) để nhiễu đủ đậm.
  - Text nhiễu: vẽ chồng 2px theo 4 hướng (giả bold đậm hơn), tăng số dòng (4-10).
  - Mỗi hình / dòng chữ tự chọn màu riêng từ bảng màu đa dạng.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

BACKGROUND_DIR = Path(__file__).resolve().parent / "data" / "background"

SAMPLE_TEXTS = [
    "Machine Learning Lifecycle & Model Evaluation Metrics",
    "Database Normalization Constraints: 1NF, 2NF to 3NF",
    "Operating System Architecture: Process Synchronization Control",
    "- Step 1: Initialize weights randomly according to distribution",
    "- Step 2: Forward propagation through hidden layers",
    "- Step 3: Compute loss function and backpropagate gradients",
    "Figure 4.1: Structural overview of the proposed system pipeline",
    "WARNING: Missing optimizer state during model resumption initialization",
    "Early stopping triggered. Best results captured at checkpoint epoch 27.",
    "Table 2: Comparison of model performance across benchmark datasets",
    "Algorithm 3: Gradient Descent with Momentum and Weight Decay",
    "Note: All experiments conducted on NVIDIA A100 80GB GPU cluster",
    "def forward(self, x): return self.dropout(self.relu(self.fc1(x)))",
    "Accuracy: 94.3% | Precision: 91.7% | Recall: 89.5% | F1: 90.6%",
]

_background_paths_cache: list[Path] | None = None


def _load_background_paths() -> list[Path]:
    global _background_paths_cache
    if _background_paths_cache is None:
        if not BACKGROUND_DIR.exists():
            raise FileNotFoundError(
                f"Không tìm thấy thư mục background: {BACKGROUND_DIR}\n"
                "Cần đặt ảnh nền thật vào đó trước khi sinh dataset."
            )
        paths = [p for p in BACKGROUND_DIR.glob("*")
                 if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        if not paths:
            raise FileNotFoundError(
                f"Thư mục {BACKGROUND_DIR} không có ảnh nào (.jpg/.jpeg/.png)."
            )
        _background_paths_cache = paths
    return _background_paths_cache


DARK_COLORS = [
    (20, 20, 20),
    (45, 30, 20),
    (20, 35, 60),
    (40, 15, 45),
    (15, 45, 30),
    (60, 20, 20),
    (30, 30, 60),
    (80, 40, 10),
    (10, 50, 50),
]

LIGHT_COLORS = [
    (235, 235, 230),
    (255, 210, 120),
    (180, 220, 255),
    (255, 180, 190),
    (200, 255, 210),
    (255, 230, 160),
    (210, 190, 255),
    (255, 200, 150),
    (160, 240, 240),
]


def _pick_diverse_color(bg_color: tuple[int, int, int]) -> tuple[int, int, int]:
    brightness = sum(bg_color) / 3
    palette = DARK_COLORS if brightness > 140 else LIGHT_COLORS
    return random.choice(palette)


def _sample_bg_color(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    patch = img.crop((0, 0, min(60, w), min(60, h))).convert("RGB")
    pixels = list(patch.getdata())
    n = len(pixels)
    r = sum(p[0] for p in pixels) / n
    g = sum(p[1] for p in pixels) / n
    b = sum(p[2] for p in pixels) / n
    return (int(r), int(g), int(b))


def _add_text_noise(draw: ImageDraw.ImageDraw, size: tuple[int, int],
                    bg_color: tuple[int, int, int]) -> None:
    """
    Vẽ 4-10 dòng text nhiễu, mỗi dòng màu riêng.
    Vẽ chồng 4 hướng lệch 1px để giả bold đậm hơn bản cũ (3 lần → 5 lần).
    """
    num_lines = random.randint(4, 10)
    for _ in range(num_lines):
        text = random.choice(SAMPLE_TEXTS)
        x = random.randint(10, int(size[0] * 0.45))
        y = random.randint(20, size[1] - 40)
        color = _pick_diverse_color(bg_color)
        offsets = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), text, fill=color)


def _add_geometric_noise(size: tuple[int, int],
                         bg_color: tuple[int, int, int]) -> Image.Image:
    """
    Vẽ 3-7 hình kỷ hà ngẫu nhiên: line / rect / circle / triangle.
    Alpha 80-160 (đậm hơn hẳn), nét 3-6px.
    """
    w, h = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    num_shapes = random.randint(3, 7)
    for _ in range(num_shapes):
        shape_type = random.choice(["line", "rect_outline", "circle_outline", "triangle"])
        rgb = _pick_diverse_color(bg_color)
        alpha = random.randint(80, 160)
        color = (*rgb, alpha)
        line_width = random.randint(3, 6)

        if shape_type == "line":
            if random.random() < 0.5:
                y = random.randint(0, h)
                odraw.line([(0, y), (w, y)], fill=color, width=line_width)
            else:
                x = random.randint(0, w)
                odraw.line([(x, 0), (x, h)], fill=color, width=line_width)

        elif shape_type == "rect_outline":
            x1 = random.randint(0, int(w * 0.6))
            y1 = random.randint(0, int(h * 0.6))
            bw = random.randint(int(w * 0.10), int(w * 0.45))
            bh = random.randint(int(h * 0.08), int(h * 0.30))
            odraw.rectangle([x1, y1, x1 + bw, y1 + bh], outline=color,
                            width=line_width)

        elif shape_type == "circle_outline":
            cx = random.randint(0, w)
            cy = random.randint(0, h)
            r = random.randint(20, 90)
            odraw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color,
                          width=line_width)

        else:  # triangle
            # 3 đỉnh tam giác ngẫu nhiên trong vùng hợp lệ
            cx = random.randint(int(w * 0.1), int(w * 0.9))
            cy = random.randint(int(h * 0.1), int(h * 0.9))
            size_r = random.randint(30, 100)
            pts = [
                (cx, cy - size_r),
                (cx - int(size_r * 0.87), cy + size_r // 2),
                (cx + int(size_r * 0.87), cy + size_r // 2),
            ]
            odraw.polygon(pts, outline=color, width=line_width)

    return overlay


def create_base_slide(size: tuple[int, int] = (640, 640)) -> Image.Image:
    """
    1. Load ngẫu nhiên 1 ảnh thật từ data/background/
    2. Resize / center-crop về đúng `size`
    3. Vẽ nhiễu text (nhiều màu, pseudo-bold đậm)
    4. Vẽ nhiễu hình kỷ hà: line / rect / circle / triangle (alpha đậm)

    Trả về RGB sẵn sàng để process.py dán ảnh diagram + anti-diagram lên trên.
    """
    paths = _load_background_paths()
    chosen_path = random.choice(paths)

    with Image.open(chosen_path) as src:
        src = src.convert("RGB")
        src_ratio = src.width / src.height
        target_ratio = size[0] / size[1]

        if src_ratio > target_ratio:
            new_h = size[1]
            new_w = int(new_h * src_ratio)
        else:
            new_w = size[0]
            new_h = int(new_w / src_ratio)

        resized = src.resize((new_w, new_h))
        left = (new_w - size[0]) // 2
        top  = (new_h - size[1]) // 2
        slide = resized.crop((left, top, left + size[0], top + size[1])).copy()

    bg_color = _sample_bg_color(slide)

    draw = ImageDraw.Draw(slide)
    _add_text_noise(draw, size, bg_color)

    noise_layer = _add_geometric_noise(size, bg_color)
    slide = slide.convert("RGBA")
    slide.alpha_composite(noise_layer)
    slide = slide.convert("RGB")

    return slide