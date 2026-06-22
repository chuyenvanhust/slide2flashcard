#ml/src/crop_diagram/generic/process.py
import os
import random
from pathlib import Path

from PIL import Image
from background import create_base_slide


# Phân phối tỉ lệ kích thước diagram theo 3 nhóm, có tỉ trọng riêng —
# thay cho random.uniform(0.25, 0.45) cố định trước đây (chỉ tạo ra
# diagram cỡ trung bình, khiến model không học được sơ đồ rất nhỏ
# hoặc sơ đồ choán gần hết slide — 2 trường hợp thực tế hay gặp).
SCALE_TIERS = [
    # 1. Sơ đồ nhỏ (Nhóm "ẩn số"): 30%
    # Giúp mô hình bắt được các sơ đồ khối con hoặc khi tài liệu bố cục dày đặc
    {"range": (0.15, 0.30), "weight": 0.30}, 
    
    # 2. Sơ đồ trung bình (Nhóm "tiêu chuẩn"): 50%
    # Chiếm phần lớn slide, đây là kích thước phổ biến nhất trong tài liệu kỹ thuật
    {"range": (0.35, 0.60), "weight": 0.50}, 
    
    # 3. Sơ đồ lớn (Nhóm "trọng tâm"): 20%
    # Sơ đồ choán diện tích lớn, cần để model không bị "sốc" khi gặp vật thể lớn
    {"range": (0.65, 0.85), "weight": 0.20}, 
]


def _sample_scale() -> float:
    """Chọn 1 giá trị scale theo phân phối 3 nhóm có tỉ trọng (weighted),
    không phải uniform đơn giản trong 1 khoảng cố định."""
    tier = random.choices(
        SCALE_TIERS,
        weights=[t["weight"] for t in SCALE_TIERS],
        k=1,
    )[0]
    lo, hi = tier["range"]
    return random.uniform(lo, hi)


def check_overlap(box1, existing_boxes):
    """Kiểm tra xem box1 (x1, y1, x2, y2) có đè lên các box cũ hay không"""
    for box2 in existing_boxes:
        x1_max = max(box1[0], box2[0])
        y1_max = max(box1[1], box2[1])
        x2_min = min(box1[2], box2[2])
        y2_min = min(box1[3], box2[3])

        inter_w = max(0, x2_min - x1_max)
        inter_h = max(0, y2_min - y1_max)

        if inter_w > 0 and inter_h > 0:
            return True  # Có đè nhau
    return False


def generate_dataset(
    label_pools: dict,
    class_map: dict,
    num_slides: int,
    output_dir: str,
    split_name: str,
):
    """
    Sinh ảnh giả lập cho một tập cụ thể (train/val/test).

    Background giờ lấy từ ảnh thật tại data/background/ (qua create_base_slide()
    đã sửa trong background.py), có thêm nhiễu text + hình kỷ hà TRƯỚC khi
    diagram được dán đè lên — đảm bảo diagram luôn nằm trên cùng, không bị
    nhiễu phủ làm sai lệch bounding box.

    Mỗi slide dán ngẫu nhiên 0, 1, hoặc 2 diagram (đã giảm từ 0-3 xuống 0-2).
    Kích thước mỗi diagram lấy theo phân phối 3 nhóm (xem SCALE_TIERS):
    20% nhỏ (0.10-0.25), 50% trung bình (0.25-0.55), 30% lớn (0.60-0.85) —
    thay cho khoảng cố định 0.25-0.45 trước đây, giúp model học được cả
    sơ đồ phụ rất nhỏ và sơ đồ choán gần hết slide.

    Args:
        label_pools: dict {label_name: [image_paths]}
                     Hiện tại chỉ có 1 key duy nhất: {"diagram": [...]}
        class_map:   dict {label_name: class_id}
                     Hiện tại: {"diagram": 0}
        num_slides:  số lượng slide synthetic cần sinh
        output_dir:  thư mục gốc output (chứa images/ và labels/)
        split_name:  "train" | "val" | "test"
    """
    img_out = os.path.join(output_dir, "images", split_name)
    lbl_out = os.path.join(output_dir, "labels", split_name)
    os.makedirs(img_out, exist_ok=True)
    os.makedirs(lbl_out, exist_ok=True)

    SIZE = 640

    # ── Gộp toàn bộ ảnh từ các label thành 1 pool kèm class_id tương ứng ────
    # Vì hiện chỉ có 1 class ("diagram": 0), pool này thực chất chỉ có 1 nhóm,
    # nhưng giữ dạng (path, class_id) để code vẫn đúng nếu sau này thêm class.
    flat_pool: list[tuple[str, int]] = []
    for label, paths in label_pools.items():
        class_id = class_map.get(label)
        if class_id is None:
            continue  # label không có trong class_map → bỏ qua, không annotate nhầm
        flat_pool.extend((p, class_id) for p in paths)

    if not flat_pool:
        print(f"⚠️  [{split_name}] Pool ảnh rỗng — toàn bộ slide sẽ là background sạch (0 box)")

    for idx in range(num_slides):
        slide = create_base_slide(size=(SIZE, SIZE))
        existing_boxes = []
        yolo_labels = []

        # Quyết định số lượng ảnh đặt vào slide (0, 1, hoặc 2 ảnh)
        # Đã giảm từ [0,1,2,3] xuống [0,1,2] theo yêu cầu mới —
        # background thật (640x640) ít chỗ trống hơn slide vẽ giả trước đây,
        # 3 diagram dễ gây chồng lấp quá nhiều lần check_overlap.
        num_diagrams = random.choice([0, 1, 2])

        # Nếu bộ ảnh nguồn rỗng thì bắt buộc sinh slide 0 ảnh
        if not flat_pool:
            num_diagrams = 0

        attempts = 0
        placed_diagrams = 0

        while placed_diagrams < num_diagrams and attempts < 30:
            attempts += 1
            diag_path, class_id = random.choice(flat_pool)

            try:
                with Image.open(diag_path) as diag_img:
                    # Lấy scale theo phân phối 3 nhóm (nhỏ/trung bình/lớn)
                    # thay cho random.uniform(0.25, 0.45) cố định trước đây
                    scale = _sample_scale()
                    new_w = int(SIZE * scale)
                    new_h = int(diag_img.height * (new_w / diag_img.width))

                    # Ngưỡng chặn chiều cao quá khổ — nới từ 0.8 lên 0.92
                    # vì giờ có nhóm "sơ đồ lớn" (scale tới 0.85), ngưỡng cũ
                    # 0.8 sẽ cắt méo tỷ lệ ngay cả với ảnh vuông bình thường
                    # ở nhóm lớn, làm sai mục đích "diagram choán ~70% slide".
                    if new_h >= SIZE * 0.92:
                        new_h = int(SIZE * min(0.85, scale + 0.05))

                    # Chặn cứng new_w/new_h không vượt SIZE — bắt buộc phải có,
                    # vì nhóm "lớn" (scale tới 0.85) cộng với ảnh nguồn có tỷ lệ
                    # khung hình lệch (rất cao hoặc rất rộng) có thể khiến
                    # new_w hoặc new_h > SIZE sau resize, làm randint(0, âm) crash.
                    new_w = min(new_w, SIZE)
                    new_h = min(new_h, SIZE)

                    x1 = random.randint(0, SIZE - new_w)
                    y1 = random.randint(0, SIZE - new_h)
                    x2 = x1 + new_w
                    y2 = y1 + new_h

                    if not check_overlap((x1, y1, x2, y2), existing_boxes):
                        diag_resized = diag_img.resize((new_w, new_h)).convert("RGB")
                        slide.paste(diag_resized, (x1, y1))

                        existing_boxes.append((x1, y1, x2, y2))

                        # Tọa độ chuẩn hóa YOLO — dùng class_id lấy từ class_map,
                        # không hardcode "0" như bản gốc (để đúng nếu sau này
                        # thêm class thật, dù hiện tại class_id luôn = 0)
                        x_center = (x1 + new_w / 2) / SIZE
                        y_center = (y1 + new_h / 2) / SIZE
                        w_norm = new_w / SIZE
                        h_norm = new_h / SIZE
                        yolo_labels.append(
                            f"{class_id} {x_center:.6f} {y_center:.6f} "
                            f"{w_norm:.6f} {h_norm:.6f}"
                        )

                        placed_diagrams += 1

                        # Nếu vừa đặt 1 diagram "lớn" (chiếm > 65% diện tích slide)
                        # và còn cần đặt thêm diagram nữa, gần như chắc chắn không
                        # còn đủ chỗ trống — dừng sớm để tránh tốn hết 30 attempts
                        # vô ích, ảnh hưởng tốc độ sinh dataset khi chạy hàng nghìn slide.
                        area_ratio = (new_w * new_h) / (SIZE * SIZE)
                        if area_ratio > 0.65 and placed_diagrams < num_diagrams:
                            break
            except Exception:
                continue

        # Lưu file ảnh và file label tương ứng
        file_base_name = f"synthetic_slide_{split_name}_{idx}"
        slide.save(os.path.join(img_out, f"{file_base_name}.jpg"), "JPEG")

        with open(os.path.join(lbl_out, f"{file_base_name}.txt"), "w") as f:
            if yolo_labels:
                f.write("\n".join(yolo_labels) + "\n")
            else:
                pass  # File trống = slide background sạch (YOLO học negative sample)