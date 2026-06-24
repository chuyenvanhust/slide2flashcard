#ml\src\crop_diagram\training\train.py
from pathlib import Path
from datetime import datetime

import torch
from ultralytics import YOLO


def train_model():
    # 1. Thiết bị
    if torch.cuda.is_available():
        device = 0
        print(f"✅ Đã nhận diện GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("⚠️ Sử dụng CPU")

    # 2. Đường dẫn — tương đối theo vị trí file, không hardcode tuyệt đối
    ROOT_DIR        = Path(__file__).resolve().parent
    data_yaml_path  = ROOT_DIR / "dataset_merged_final" / "data.yaml"
    base_models_dir = ROOT_DIR.parent / "models"

    if not data_yaml_path.exists():
        print(f"❌ Lỗi: Không tìm thấy file {data_yaml_path}")
        return

    # 3. Resume nếu có checkpoint bị gián đoạn trước đó
    last_ckpt = base_models_dir / "train_results_latest" / "weights" / "last.pt"
    if last_ckpt.exists():
        print(f"🔄 Tìm thấy checkpoint dở, resume training: {last_ckpt}")
        model = YOLO(str(last_ckpt))
        model.train(resume=True)
        return

    # 4. Model mới
    model = YOLO("yolo11s.pt")   # bỏ "v" — đúng convention YOLO11

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name  = f"train_results_{timestamp}"
    print(f"🚀 Bắt đầu training: {run_name}")

    model.train(
        data=str(data_yaml_path),
        epochs=250,
        imgsz=640,
        batch=8,                  # tăng từ 8 — tận dụng GPU tốt hơn
        device=device,

        project=str(base_models_dir),
        name=run_name,
        exist_ok=False,

        patience=40,               # tăng từ 20 — phù hợp với cos_lr trên 250 epoch
        optimizer="AdamW",
        lr0=0.001,
        cos_lr=True,
        amp=True,
        workers=4,

        # Augmentation — tối ưu cho tài liệu/slide, không phải ảnh tự nhiên
        mosaic=1.0,
        close_mosaic=15,
        mixup=0.0,
        degrees=0.0,                # slide không bị xoay
        shear=0.0,
        perspective=0.0,
        flipud=0.0,                 # không bao giờ lật ngược tài liệu
        fliplr=0.3,
        hsv_h=0.0,
        hsv_s=0.3,
        hsv_v=0.3,
        scale=0.3,
        translate=0.1,

        # Loss
        cls=1.0,                    # bỏ giải thích "bảo vệ Table" — single class
        box=7.5,

        val=True,
        plots=True,
    )

    save_dir = model.trainer.save_dir   # sửa lỗi .save_dir không tồn tại
    best_pt  = save_dir / "weights" / "best.pt"

    print("\n" + "=" * 30)
    print("✅ Training hoàn tất!")
    print(f"📍 Toàn bộ kết quả lưu tại: {save_dir}")
    print(f"📍 Model tốt nhất: {best_pt}")
    print("=" * 30)


if __name__ == "__main__":
    train_model()