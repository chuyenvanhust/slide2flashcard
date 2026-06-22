r"""
ml\src\crop_diagram\generic\main.py

Pipeline tạo synthetic dataset cho YOLO training:
  1. Crawl ảnh thô (Chỉ lấy nguồn duy nhất từ link Google nạp vào) — data train nội bộ
     (bỏ qua nếu dùng --skip-crawl, đã có data/raw_crawled từ trước)
  2. Sinh dataset synthetic (dán ảnh vào slide giả) — CHỈ 1 TẬP TRAIN DUY NHẤT,
     không chia train/val/test nữa
  3. Tự tạo data.yaml cho YOLO với 1 class duy nhất: "diagram"

Chạy:
    python main.py
    python main.py --skip-crawl   # dùng ảnh đã crawl từ trước, bỏ qua bước 1
"""
import argparse
import os
from pathlib import Path

from crawl_diagrams import crawl_diagram_images
from process import generate_dataset

# Tất cả đường dẫn được tính tương đối theo vị trí thực của main.py
BASE_DIR           = Path(__file__).resolve().parent
RAW_DIR            = str(BASE_DIR / "data" / "raw_crawled")
OUTPUT_DATASET_DIR = str(BASE_DIR / "synthetic_dataset")

# Chỉ còn 1 class duy nhất: "diagram"
CLASS_MAP = {
    "diagram": 0,
}

# CHỈ lấy duy nhất nhãn "diagram" từ file crawl_diagrams.py
MERGE_LABELS_INTO_DIAGRAM = ["diagram"]

# Bỏ chia train/val/test — chỉ sinh 1 tập train duy nhất
TOTAL_TRAIN_SLIDES = 2000


def collect_images_by_label(raw_dir: str) -> dict[str, list[str]]:
    """Gom ảnh đã crawl theo nhãn diagram duy nhất."""
    merged_images: list[str] = []
    for label in MERGE_LABELS_INTO_DIAGRAM:
        label_dir = Path(raw_dir) / label
        if not label_dir.exists():
            continue
        imgs = [str(p) for p in label_dir.glob("*")
                if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        merged_images.extend(imgs)

    return {"diagram": merged_images}


def main(skip_crawl: bool = False, engine: str = "google"):
    # ── BƯỚC 1: Crawl ảnh thô — Chỉ lấy duy nhất nguồn nhãn "diagram" ───────
    if not skip_crawl:
        for label in MERGE_LABELS_INTO_DIAGRAM:
            print(f"🔍 Đang crawl ảnh cho nguồn '{label}' "
                  f"(sẽ gộp vào class duy nhất: diagram)...")
            crawl_diagram_images(
                output_dir      = RAW_DIR,
                label_filter    = label,
                max_per_keyword = 200,
                engine          = engine,
            )
    else:
        print(f"⏭️  Bỏ qua crawl, dùng ảnh có sẵn tại '{RAW_DIR}'")

    # ── BƯỚC 2: Gom toàn bộ ảnh thành 1 pool duy nhất (không chia split) ────
    pools_by_label = collect_images_by_label(RAW_DIR)

    total_raw = len(pools_by_label["diagram"])
    print(f"\n📊 Tổng ảnh gốc thu được (nhãn diagram): {total_raw}")

    if total_raw == 0:
        print("❌ Không có ảnh nào để sinh dữ liệu. Kiểm tra lại bước crawl hoặc link URL.")
        return

    # Không split — dùng nguyên pool cho tập train duy nhất
    train_pool = {"diagram": pools_by_label["diagram"]}
    print(f"🔒 Dùng toàn bộ {total_raw} ảnh gốc cho tập train (không chia val/test).")

    # ── BƯỚC 3: Sinh synthetic dataset — chỉ 1 tập "train" ──────────────────
    print(f"\n🚀 Đang sinh {TOTAL_TRAIN_SLIDES} slide nhân tạo cho tập train...")

    generate_dataset(
        label_pools  = train_pool,
        class_map    = CLASS_MAP,
        num_slides   = TOTAL_TRAIN_SLIDES,
        output_dir   = OUTPUT_DATASET_DIR,
        split_name   = "train",
    )
    print(f"🔹 Hoàn thành sinh tập Train ({TOTAL_TRAIN_SLIDES} ảnh).")

    # ── BƯỚC 4: Tạo data.yaml cho YOLO — chỉ có train, không có val/test ───
    sorted_classes = sorted(CLASS_MAP.items(), key=lambda x: x[1])
    names_block = "\n".join(f"  {idx}: {name}" for name, idx in sorted_classes)

    # YOLO yêu cầu phải có field "val" để không lỗi khi load config.
    # Vì không sinh tập val riêng, tạm trỏ val về cùng thư mục train —
    # nghĩa là không có validation độc lập thực sự, chỉ để tránh crash
    # khi gọi model.train(). Cần tạo val set riêng trước khi train thật.
    yaml_content = f"""path: {os.path.abspath(OUTPUT_DATASET_DIR)}
train: images/train
val: images/train

names:
{names_block}
"""
    yaml_path = os.path.join(OUTPUT_DATASET_DIR, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"\n🎉 Xong! Bộ dữ liệu đã sẵn sàng tại '{OUTPUT_DATASET_DIR}'")
    print(f"🔗 File cấu hình YOLO: {yaml_path}")
    print(f"⚠️  data.yaml: val đang trỏ về chính tập train (chưa có val set riêng).")
    print(f"⚠️  Lưu ý: data train nội bộ, không dùng để public/deploy thương mại.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-crawl", action="store_true",
                        help="Bỏ qua bước crawl, dùng ảnh đã có tại data/raw_crawled")
    parser.add_argument("--engine", type=str, default="google",
                        choices=["google"])
    args = parser.parse_args()

    main(skip_crawl=args.skip_crawl, engine=args.engine)