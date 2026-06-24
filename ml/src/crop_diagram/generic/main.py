r"""
ml\src\crop_diagram\generic\main.py

Pipeline tạo synthetic dataset cho YOLO training:
  1. Crawl ảnh diagram (KEYWORD_SETS) và ảnh anti-diagram (ANTI_KEYWORD_SET)
     bằng Selenium — dùng --skip-crawl nếu đã có sẵn data/raw_crawled/.
  2. Chia ẢNH NGUỒN thành train_pool / val_pool theo tỉ lệ 80/20, seed cố định.
     Cả diagram pool và anti pool đều được chia riêng để tránh leakage.
  3. Sinh dataset synthetic:
       - Train: 12 000 slide (dùng train_pool diagram + train_pool anti)
       - Val  :  3 000 slide (dùng val_pool diagram   + val_pool anti)
     Mỗi slide: background thật + nhiễu text/hình kỷ hà + ảnh diagram (có label)
     + ảnh anti-diagram (không label).
  4. Tạo data.yaml cho YOLO với 1 class: "diagram".

Chạy:
    python main.py
    python main.py --skip-crawl   # bỏ qua bước crawl
"""
import argparse
import os
import random
from pathlib import Path

from crawl_diagrams import crawl_diagram_images, ANTI_KEYWORD_SET
from process import generate_dataset

BASE_DIR           = Path(__file__).resolve().parent
RAW_DIR            = str(BASE_DIR / "data" / "raw_crawled")
OUTPUT_DATASET_DIR = str(BASE_DIR / "synthetic_dataset")

CLASS_MAP = {"diagram": 0}

TOTAL_TRAIN_SLIDES = 12_000
TOTAL_VAL_SLIDES   =  3_000
TRAIN_SOURCE_RATIO =  0.80      # 80% ảnh nguồn → train, 20% → val
SPLIT_SEED         = 42


# ── Helpers ────────────────────────────────────────────────────────────────

def _collect_images(subdir: str) -> list[str]:
    """Trả về danh sách đường dẫn ảnh trong subdir (bất kể tên file)."""
    d = Path(subdir)
    if not d.exists():
        return []
    return [str(p) for p in d.glob("*")
            if p.suffix.lower() in (".jpg", ".jpeg", ".png")]


def _split_list(lst: list, ratio: float, seed: int) -> tuple[list, list]:
    """Xáo trộn ngẫu nhiên (seed cố định) rồi chia theo ratio."""
    shuffled = lst[:]
    random.Random(seed).shuffle(shuffled)
    n = int(len(shuffled) * ratio)
    return shuffled[:n], shuffled[n:]


# ── Main ───────────────────────────────────────────────────────────────────

def main(skip_crawl: bool = False, engine: str = "google"):

    # ── BƯỚC 1: Crawl ─────────────────────────────────────────────────────
    if not skip_crawl:
        print("🔍 Crawl ảnh diagram (keyword pool)...")
        crawl_diagram_images(
            output_dir      = RAW_DIR,
            label_filter    = "diagram",
            max_per_keyword = 200,
            engine          = engine,
        )

        print("🔍 Crawl ảnh anti-diagram (anti keyword pool)...")
        crawl_diagram_images(
            output_dir      = RAW_DIR,
            label_filter    = "anti",
            custom_keywords = ANTI_KEYWORD_SET,
            max_per_keyword = 200,
            engine          = engine,
        )
    else:
        print(f"⏭️  Bỏ qua crawl, dùng ảnh có sẵn tại '{RAW_DIR}'")

    # ── BƯỚC 2: Gom ảnh và chia pool ─────────────────────────────────────
    diagram_imgs = _collect_images(str(Path(RAW_DIR) / "diagram"))
    anti_imgs    = _collect_images(str(Path(RAW_DIR) / "anti"))

    print(f"\n📊 Ảnh gốc: diagram={len(diagram_imgs)}, anti={len(anti_imgs)}")

    if not diagram_imgs:
        print("❌ Không có ảnh diagram. Kiểm tra lại bước crawl.")
        return

    # Chia diagram pool 80/20 (không leakage)
    diag_train, diag_val = _split_list(diagram_imgs, TRAIN_SOURCE_RATIO, SPLIT_SEED)
    # Chia anti pool 80/20 độc lập
    anti_train, anti_val = _split_list(anti_imgs, TRAIN_SOURCE_RATIO, SPLIT_SEED + 1)

    print(f"🔀 Chia ảnh nguồn (seed={SPLIT_SEED}):")
    print(f"   diagram : {len(diag_train)} train | {len(diag_val)} val")
    print(f"   anti    : {len(anti_train)} train | {len(anti_val)} val")
    print("   ✅ 0 ảnh trùng giữa train/val — không data leakage")

    if not diag_val:
        print("❌ val_pool diagram rỗng — crawl thêm ảnh hoặc giảm TRAIN_SOURCE_RATIO.")
        return

    # ── BƯỚC 3: Sinh dataset ──────────────────────────────────────────────
    print(f"\n🚀 Sinh {TOTAL_TRAIN_SLIDES} slide TRAIN...")
    generate_dataset(
        label_pools = {"diagram": diag_train},
        class_map   = CLASS_MAP,
        num_slides  = TOTAL_TRAIN_SLIDES,
        output_dir  = OUTPUT_DATASET_DIR,
        split_name  = "train",
        anti_pool   = anti_train,
    )

    print(f"\n🚀 Sinh {TOTAL_VAL_SLIDES} slide VAL...")
    generate_dataset(
        label_pools = {"diagram": diag_val},
        class_map   = CLASS_MAP,
        num_slides  = TOTAL_VAL_SLIDES,
        output_dir  = OUTPUT_DATASET_DIR,
        split_name  = "val",
        anti_pool   = anti_val,
    )

    # ── BƯỚC 4: data.yaml ─────────────────────────────────────────────────
    sorted_classes = sorted(CLASS_MAP.items(), key=lambda x: x[1])
    names_block    = "\n".join(f"  {idx}: {name}" for name, idx in sorted_classes)

    yaml_content = f"""path: {os.path.abspath(OUTPUT_DATASET_DIR)}
train: images/train
val:   images/val

names:
{names_block}
"""
    yaml_path = os.path.join(OUTPUT_DATASET_DIR, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"\n🎉 Xong!")
    print(f"   Dataset : {OUTPUT_DATASET_DIR}")
    print(f"   YAML    : {yaml_path}")
    print(f"   Train   : {TOTAL_TRAIN_SLIDES} slide | Val: {TOTAL_VAL_SLIDES} slide")
    print(f"   Split   : 80/20 trên ảnh nguồn (seed={SPLIT_SEED}) — không leakage")
    print("⚠️  Data train nội bộ, không dùng để public/deploy thương mại.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-crawl", action="store_true",
                        help="Bỏ qua crawl, dùng ảnh đã có tại data/raw_crawled/")
    parser.add_argument("--engine", type=str, default="google",
                        choices=["google"])
    args = parser.parse_args()
    main(skip_crawl=args.skip_crawl, engine=args.engine)