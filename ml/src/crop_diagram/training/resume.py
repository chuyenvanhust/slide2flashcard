#ml\src\crop_diagram\training\train.py
from ultralytics import YOLO
import os
import torch
from datetime import datetime

def train_model():
    # 1. Kiểm tra và thiết lập thiết bị (GPU vs CPU)
    if torch.cuda.is_available():
        device = 0
        print(f"✅ Đã nhận diện GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("⚠️ Sử dụng CPU")

    # 2. Khởi tạo mô hình
    model = YOLO("C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/models/train_results_20260619_091532/weights/last.pt") 

    # 3. Xử lý đường dẫn
    data_yaml_path = "C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/training/dataset/data.yaml"
    base_models_dir = "C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/models"

    if not os.path.exists(data_yaml_path):
        print(f"❌ Lỗi: Không tìm thấy file {data_yaml_path}")
        return

    # --- TẠO TIMESTAMP ---
    # Lấy thời gian hiện tại theo định dạng: NămThángNgày_GiờPhútGiây (VD: 20240520_153025)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"train_results_{timestamp}"

    print(f"🚀 Bắt đầu training: {run_name}")

    # 4. Tiến hành Training
    results = model.train(
        data=data_yaml_path,
        epochs=250, 
        imgsz=640,
        batch=16,             
        device=device,
        
        # --- LƯU VÀO THƯ MỤC CÓ TIMESTAMP ---
        project=base_models_dir, 
        name=run_name,             # Thư mục con sẽ là train_results_2024...
        # ------------------------------------

        patience=20,          
        optimizer='AdamW',    
        lr0=0.005,            
        cos_lr=True,          
        amp=True,             
        workers=4,            
        exist_ok=False,       # Để False để đảm bảo luôn tạo folder mới nếu trùng (hiếm khi trùng với timestamp)
        plots=True            
    )

    print("\n" + "="*30)
    print("✅ Training hoàn tất!")
    print(f"📍 Toàn bộ kết quả lưu tại: {results.save_dir}")
    print(f"📍 Model tốt nhất: {os.path.join(results.save_dir, 'weights', 'best.pt')}")
    print("="*30)

if __name__ == "__main__":
    train_model()