import os
import pandas as pd
import numpy as np
from ultralytics import YOLO

def find_best_conf_by_map(model_path, data_yaml_path):
    model = YOLO(model_path)
    best_map_score = 0
    best_conf = 0.05
    
    # Quét ngưỡng conf để tìm điểm mAP cao nhất trên tập VAL
    # Kết hợp cả mAP50 và mAP50-95 để tìm sự cân bằng
    for conf in np.arange(0.05, 0.55, 0.05):
        metrics = model.val(data=data_yaml_path, split='val', conf=conf, verbose=False)
        # Điểm số = trung bình cộng của mAP50 và mAP50-95
        map_score = (metrics.box.map50 + metrics.box.map) / 2
        
        if map_score > best_map_score:
            best_map_score = map_score
            best_conf = conf
            
    return best_conf

def main():
    model_folders = [
        "C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/models/train_results_20260620_233507",
        "C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/models/train_results_20260621_193353"
    ]
    
    data_yaml_path = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\data.yaml"
    test_images_path = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\images"
    
    results_list = []

    for folder in model_folders:
        model_path = os.path.join(folder, "weights", "best.pt")
        if not os.path.exists(model_path): continue
        
        model_name = os.path.basename(folder)
        print(f"\n--- Đang tối ưu ngưỡng Conf dựa trên mAP cho: {model_name} ---")
        
        # 1. Tìm Best Conf dựa trên mAP trên VAL
        best_conf = find_best_conf_by_map(model_path, data_yaml_path)
        
        # 2. Đánh giá trên tập TEST với Best Conf này
        model = YOLO(model_path)
        test_metrics = model.val(data=data_yaml_path, split='test', conf=best_conf, verbose=False)
        
        # 3. Lưu ảnh dự đoán từ tập TEST để xem trực quan
        model.predict(
            source=test_images_path,
            conf=best_conf,
            save=True,
            project='runs/map_optimized_eval',
            name=model_name,
            exist_ok=True
        )
        
        results_list.append({
            "Model": model_name,
            "Used_Conf": round(best_conf, 2),
            "mAP50": round(test_metrics.box.map50, 4),
            "mAP50-95": round(test_metrics.box.map, 4),
            "Precision": round(test_metrics.box.p.mean(), 4),
            "Recall": round(test_metrics.box.r.mean(), 4)
        })

    df = pd.DataFrame(results_list)
    print("\n" + "="*80)
    print("BẢNG ĐÁNH GIÁ TRÊN TEST (Dùng Best Conf tối ưu theo mAP trên Val)")
    print("="*80)
    print(df.to_string(index=False))

if __name__ == '__main__':
    main()