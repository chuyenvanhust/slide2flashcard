#ml/src/crop_diagram/generic/process.py
"""
process.py — Sinh synthetic slides cho YOLO training.

Logic mới so với bản cũ:
  - Nhận thêm `anti_pool`: danh sách ảnh KHÔNG phải diagram (từ ANTI_KEYWORD_SET).
    Các ảnh này được dán lên slide KHÔNG kèm label (YOLO học negative sample).
  - Mỗi slide: dán ngẫu nhiên 0-2 diagram (có label) + 0-2 ảnh anti (không label).
  - Tất cả ảnh dán lên đều check overlap với nhau (diagram và anti dùng chung
    danh sách existing_boxes để tránh trùng lấp bất kỳ loại nào).
  - Scale vẫn theo phân phối 3 nhóm (nhỏ / trung bình / lớn).
"""
import os
import random
from pathlib import Path

from PIL import Image
from background import create_base_slide


SCALE_TIERS = [
    {"range": (0.15, 0.30), "weight": 0.30},
    {"range": (0.35, 0.60), "weight": 0.50},
    {"range": (0.65, 0.85), "weight": 0.20},
]


def _sample_scale() -> float:
    tier = random.choices(
        SCALE_TIERS,
        weights=[t["weight"] for t in SCALE_TIERS],
        k=1,
    )[0]
    lo, hi = tier["range"]
    return random.uniform(lo, hi)


def check_overlap(box1: tuple, existing_boxes: list) -> bool:
    """Trả về True nếu box1 (x1,y1,x2,y2) chồng lấp bất kỳ box nào trong danh sách."""
    for box2 in existing_boxes:
        x1_max = max(box1[0], box2[0])
        y1_max = max(box1[1], box2[1])
        x2_min = min(box1[2], box2[2])
        y2_min = min(box1[3], box2[3])
        if max(0, x2_min - x1_max) > 0 and max(0, y2_min - y1_max) > 0:
            return True
    return False


def _paste_image(
    slide: Image.Image,
    img_path: str,
    SIZE: int,
    existing_boxes: list,
    max_attempts: int = 20,
) -> tuple[int, int, int, int] | None:
    """
    Thử dán 1 ảnh từ img_path lên slide không chồng lấp các box đã có.
    Trả về (x1, y1, x2, y2) nếu thành công, None nếu không tìm được vị trí.
    """
    for _ in range(max_attempts):
        try:
            with Image.open(img_path) as img:
                scale = _sample_scale()
                new_w = int(SIZE * scale)
                new_h = int(img.height * (new_w / img.width))

                if new_h >= SIZE * 0.92:
                    new_h = int(SIZE * min(0.85, scale + 0.05))
                new_w = min(new_w, SIZE)
                new_h = min(new_h, SIZE)

                if new_w <= 0 or new_h <= 0:
                    continue

                x1 = random.randint(0, SIZE - new_w)
                y1 = random.randint(0, SIZE - new_h)
                x2 = x1 + new_w
                y2 = y1 + new_h

                if not check_overlap((x1, y1, x2, y2), existing_boxes):
                    resized = img.resize((new_w, new_h)).convert("RGB")
                    slide.paste(resized, (x1, y1))
                    existing_boxes.append((x1, y1, x2, y2))
                    return (x1, y1, x2, y2)
        except Exception:
            continue
    return None


def generate_dataset(
    label_pools: dict[str, list[str]],
    class_map: dict[str, int],
    num_slides: int,
    output_dir: str,
    split_name: str,
    anti_pool: list[str] | None = None,
):
    """
    Sinh ảnh synthetic cho 1 tập (train / val).

    Args:
        label_pools : {label_name: [image_paths]} — ảnh diagram có label.
        class_map   : {label_name: class_id}.
        num_slides  : số slide cần sinh.
        output_dir  : thư mục gốc (chứa images/ và labels/).
        split_name  : "train" | "val".
        anti_pool   : danh sách ảnh KHÔNG phải diagram (dán lên không label).
                      Nếu None hoặc rỗng thì bỏ qua.
    """
    img_out = os.path.join(output_dir, "images", split_name)
    lbl_out = os.path.join(output_dir, "labels", split_name)
    os.makedirs(img_out, exist_ok=True)
    os.makedirs(lbl_out, exist_ok=True)

    SIZE = 640

    # Gom ảnh diagram thành flat pool kèm class_id
    flat_diag_pool: list[tuple[str, int]] = []
    for label, paths in label_pools.items():
        class_id = class_map.get(label)
        if class_id is None:
            continue
        flat_diag_pool.extend((p, class_id) for p in paths)

    anti_imgs: list[str] = anti_pool if anti_pool else []

    if not flat_diag_pool:
        print(f"⚠️  [{split_name}] Pool diagram rỗng — slide sẽ chỉ có background + anti-images.")

    print(f"  [{split_name}] Đang sinh {num_slides} slide "
          f"(diagram pool: {len(flat_diag_pool)}, anti pool: {len(anti_imgs)})...")

    for idx in range(num_slides):
        slide = create_base_slide(size=(SIZE, SIZE))
        existing_boxes: list[tuple] = []
        yolo_labels: list[str] = []

        # ── Quyết định số lượng diagram và anti-image cần đặt ────────────────
        num_diagrams = random.choice([0, 1, 2]) if flat_diag_pool else 0
        num_anti     = random.choice([0, 1, 2]) if anti_imgs else 0

        # ── Dán ảnh ANTI trước (không label) — thứ tự không quan trọng về
        #    label nhưng dán trước để diagram có thể đè lên nếu cần ──────────
        anti_placed = 0
        for _ in range(num_anti * 3):          # tối đa 3x thử mỗi ảnh anti
            if anti_placed >= num_anti:
                break
            anti_path = random.choice(anti_imgs)
            box = _paste_image(slide, anti_path, SIZE, existing_boxes)
            if box:
                anti_placed += 1
                # KHÔNG thêm vào yolo_labels (ảnh anti không có label)

        # ── Dán ảnh DIAGRAM (có label) ──────────────────────────────────────
        diag_placed = 0
        for _ in range(num_diagrams * 10):     # tối đa 10x thử mỗi diagram
            if diag_placed >= num_diagrams:
                break
            diag_path, class_id = random.choice(flat_diag_pool)
            box = _paste_image(slide, diag_path, SIZE, existing_boxes)
            if box:
                x1, y1, x2, y2 = box
                new_w = x2 - x1
                new_h = y2 - y1
                x_center = (x1 + new_w / 2) / SIZE
                y_center = (y1 + new_h / 2) / SIZE
                w_norm   = new_w / SIZE
                h_norm   = new_h / SIZE
                yolo_labels.append(
                    f"{class_id} {x_center:.6f} {y_center:.6f} "
                    f"{w_norm:.6f} {h_norm:.6f}"
                )
                diag_placed += 1

                # Dừng sớm nếu diagram lớn chiếm > 65% diện tích
                area_ratio = (new_w * new_h) / (SIZE * SIZE)
                if area_ratio > 0.65 and diag_placed < num_diagrams:
                    break

        # ── Lưu ảnh + label ─────────────────────────────────────────────────
        file_base = f"synthetic_{split_name}_{idx:05d}"
        slide.save(os.path.join(img_out, f"{file_base}.jpg"), "JPEG", quality=92)

        with open(os.path.join(lbl_out, f"{file_base}.txt"), "w") as f:
            if yolo_labels:
                f.write("\n".join(yolo_labels) + "\n")
            # File trống = negative sample (background + anti-image, không có diagram)

        if (idx + 1) % 500 == 0:
            print(f"  [{split_name}] {idx + 1}/{num_slides} slide đã sinh xong...")

    print(f"  [{split_name}] ✅ Hoàn thành {num_slides} slide.")