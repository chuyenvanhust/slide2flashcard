#ml\src\crop_diagram\generic\background.py
"""
Background module — bản sửa theo yêu cầu mới:

  - KHÔNG còn tự vẽ slide giả từ palette màu nữa.
  - Load background THẬT từ thư mục data/background/ (khoảng 7 ảnh)
    do người dùng cung cấp sẵn — đây là ảnh slide nền thực tế
    (có thể trắng, có theme, có logo trường...).
  - Sau khi load, mô phỏng thêm "nhiễu trang tài liệu":
      + Vài dòng text ngẫu nhiên, MỖI DÒNG MÀU KHÁC NHAU
        (chọn random từ bảng màu đa dạng, KHÔNG dùng trắng vì
        dễ lẫn vào nền sáng), vẽ đè nhẹ để giả lập bold tăng độ dày.
      + Vài hình kỷ hà ngẫu nhiên (line/rect/circle), MỖI HÌNH MÀU KHÁC NHAU,
        alpha và độ dày nét đã tăng (60-120 alpha, 2-5px) để nhiễu
        thực sự có giá trị quan sát được, không quá mờ nhạt như bản trước.
    Bước nhiễu này PHẢI chạy TRƯỚC khi dán diagram đè lên trong process.py,
    để diagram luôn nằm "trên cùng", không bị nhiễu phủ lên làm sai bounding box.
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
]

# Cache danh sách path background để không quét lại ổ đĩa mỗi lần gọi
_background_paths_cache: list[Path] | None = None


def _load_background_paths() -> list[Path]:
    global _background_paths_cache
    if _background_paths_cache is None:
        if not BACKGROUND_DIR.exists():
            raise FileNotFoundError(
                f"Không tìm thấy thư mục background: {BACKGROUND_DIR}\n"
                f"Cần đặt ~7 ảnh nền thật vào đó trước khi sinh dataset."
            )
        paths = [p for p in BACKGROUND_DIR.glob("*")
                 if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        if not paths:
            raise FileNotFoundError(
                f"Thư mục {BACKGROUND_DIR} không có ảnh nào (.jpg/.jpeg/.png)."
            )
        _background_paths_cache = paths
    return _background_paths_cache


# Bảng màu đa dạng cho chữ + hình kỷ hà — KHÔNG dùng trắng vì dễ lẫn vào
# nền sáng (nhiều ảnh background thật có nền trắng/kem). Mỗi màu được gắn
# kèm "tier" sáng/tối để chọn ra màu tương phản tốt với nền thật, nhưng
# trong cùng 1 tier vẫn có nhiều lựa chọn màu khác nhau — tránh tình trạng
# toàn bộ ảnh sinh ra chỉ có đúng 1 màu chữ đen hoặc 1 màu chữ trắng.

DARK_COLORS = [
    (20, 20, 20),      # đen xám chuẩn
    (45, 30, 20),      # nâu cà phê đậm
    (20, 35, 60),      # xanh navy đậm
    (40, 15, 45),      # tím đậm
    (15, 45, 30),      # xanh rêu đậm
    (60, 20, 20),      # đỏ nâu đậm
    (30, 30, 60),      # tím xanh đậm
]

LIGHT_COLORS = [
    (235, 235, 230),   # xám sáng ngà (không phải trắng tinh #FFFFFF)
    (255, 210, 120),   # vàng cam sáng
    (180, 220, 255),   # xanh da trời nhạt
    (255, 180, 190),   # hồng san hô nhạt
    (200, 255, 210),   # xanh mint nhạt
    (255, 230, 160),   # vàng kem đậm hơn ngà
    (210, 190, 255),   # tím lavender nhạt
]


def _pick_diverse_color(bg_color: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    Chọn NGẪU NHIÊN 1 màu trong nhóm tương phản phù hợp với độ sáng nền,
    thay vì luôn trả về đúng 1 màu cố định như bản cũ (_pick_text_color).

    Nền sáng → random trong DARK_COLORS (nhiều màu tối khác nhau)
    Nền tối  → random trong LIGHT_COLORS (nhiều màu sáng khác nhau, trừ trắng)
    """
    brightness = sum(bg_color) / 3
    palette = DARK_COLORS if brightness > 140 else LIGHT_COLORS
    return random.choice(palette)


def _sample_bg_color(img: Image.Image) -> tuple[int, int, int]:
    """Lấy màu trung bình góc trên-trái của ảnh làm đại diện màu nền,
    dùng để quyết định màu chữ/hình kỷ hà tương phản."""
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
    Vẽ vài dòng text ngẫu nhiên mô phỏng nội dung slide.

    Khác bản cũ: mỗi dòng tự chọn 1 màu riêng từ bảng màu đa dạng
    (không dùng 1 màu cố định cho toàn slide), và vẽ đè 1 lần lệch nhẹ
    (giả lập bold) để tăng độ dày nét chữ — làm nhiễu có giá trị rõ hơn,
    không bị quá mảnh/mờ nhạt như bản gốc dùng draw.text() 1 lần.
    """
    num_lines = random.randint(3, 8)
    for _ in range(num_lines):
        text = random.choice(SAMPLE_TEXTS)
        x = random.randint(10, int(size[0] * 0.4))
        y = random.randint(20, size[1] - 40)
        color = _pick_diverse_color(bg_color)

        # Vẽ lệch 1px theo 2 hướng để giả lập độ dày bold,
        # PIL draw.text() không có tham số stroke_width ổn định
        # trên mọi version/font nên dùng cách vẽ chồng thủ công này.
        for dx, dy in [(0, 0), (1, 0), (0, 1)]:
            draw.text((x + dx, y + dy), text, fill=color)


def _add_geometric_noise(size: tuple[int, int],
                         bg_color: tuple[int, int, int]) -> Image.Image:
    """
    Vẽ vài hình kỷ hà ngẫu nhiên mô phỏng nhiễu trang tài liệu thật:
    khung viền, gạch chân tiêu đề, watermark hình tròn, đường kẻ phân đoạn...

    Khác bản cũ:
      - Mỗi hình tự chọn màu riêng từ bảng màu đa dạng (không dùng
        accent_color cố định cho mọi hình trong cùng 1 slide).
      - Tăng alpha (60-120, trước là 25-70) và tăng width nét vẽ
        (2-5px, trước là 1-2px) để nhiễu thực sự có giá trị quan sát được,
        thay vì quá nhạt gần như vô hình như bản cũ.
    """
    w, h = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    num_shapes = random.randint(2, 5)   # tăng nhẹ số lượng hình (trước 1-4)
    for _ in range(num_shapes):
        shape_type = random.choice(["line", "rect_outline", "circle_outline"])
        rgb = _pick_diverse_color(bg_color)
        alpha = random.randint(60, 120)          # đậm hơn bản cũ (25-70)
        color = (*rgb, alpha)
        line_width = random.randint(2, 5)        # dày hơn bản cũ (1-2)

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
            bw = random.randint(int(w * 0.15), int(w * 0.4))
            bh = random.randint(int(h * 0.1), int(h * 0.25))
            odraw.rectangle([x1, y1, x1 + bw, y1 + bh], outline=color,
                            width=line_width)

        else:  # circle_outline
            cx = random.randint(0, w)
            cy = random.randint(0, h)
            r = random.randint(20, 80)
            odraw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color,
                          width=line_width)

    return overlay


def create_base_slide(size: tuple[int, int] = (640, 640)) -> Image.Image:
    """
    Tạo 1 background cho synthetic slide — bản sửa:
      1. Load NGẪU NHIÊN 1 ảnh từ data/background/ (ảnh thật, đã có sẵn)
      2. Resize/crop về đúng `size`
      3. Vẽ thêm text nhiễu
      4. Vẽ thêm hình kỷ hà nhiễu (alpha thấp, không che nội dung)

    Trả về ảnh RGB sẵn sàng để process.py dán diagram lên trên (bước cuối).
    """
    paths = _load_background_paths()
    chosen_path = random.choice(paths)

    with Image.open(chosen_path) as src:
        src = src.convert("RGB")
        # Resize giữ tỷ lệ rồi crop về đúng size để không méo ảnh nền thật
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

    # Hình kỷ hà cần alpha → vẽ trên layer RGBA riêng rồi composite xuống slide
    noise_layer = _add_geometric_noise(size, bg_color)
    slide = slide.convert("RGBA")
    slide.alpha_composite(noise_layer)
    slide = slide.convert("RGB")

    return slide