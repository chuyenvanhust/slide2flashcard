import os
import pandas as pd
import numpy as np
from ultralytics import YOLO

def get_f1_score(metrics):
    p = metrics.box.p.mean()
    r = metrics.box.r.mean()
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0

def find_best_conf_f1_val(model_path, data_yaml_path):
    model = YOLO(model_path)
    best_f1 = 0
    best_conf = 0.05 # Mặc định
    
    # Quét ngưỡng conf trên tập VAL để tìm F1 max
    for conf in np.arange(0.05, 0.55, 0.05):
        metrics = model.val(data=data_yaml_path, split='val', conf=conf, verbose=False)
        f1 = get_f1_score(metrics)
        if f1 > best_f1:
            best_f1 = f1
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
        print(f"\n--- Đang tối ưu F1 trên VAL cho: {model_name} ---")
        
        # 1. Tìm Best Conf dựa trên F1-Score của tập VAL
        best_conf = find_best_conf_f1_val(model_path, data_yaml_path)
        
        # 2. Dùng chính Best Conf đó để test trên tập TEST
        model = YOLO(model_path)
        test_metrics = model.val(data=data_yaml_path, split='test', conf=best_conf, verbose=False)
        
        # 3. Lưu ảnh dự đoán từ tập TEST để xem trực quan
        model.predict(
            source=test_images_path,
            conf=best_conf,
            save=True,
            project='runs/final_evaluation',
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
    print("BẢNG ĐÁNH GIÁ TRÊN TEST (Dùng Best Conf từ Val)")
    print("="*80)
    print(df.to_string(index=False))

if __name__ == '__main__':
    main()