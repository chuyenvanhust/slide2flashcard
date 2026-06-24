import cv2
import os
import glob
import numpy as np
from ultralytics import YOLO

def draw_multi_comparison(model_path_a, model_path_b, image_folder, label_folder, output_folder):
    model_a = YOLO(model_path_a)
    model_b = YOLO(model_path_b)
    os.makedirs(output_folder, exist_ok=True)
    
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(glob.glob(os.path.join(image_folder, ext)))
    
    print(f">>> Đã tìm thấy {len(image_files)} ảnh. Đang so sánh...")

    for img_path in image_files:
        img_name = os.path.basename(img_path)
        img_basename = os.path.splitext(img_name)[0]
        label_path = os.path.join(label_folder, img_basename + ".txt")
        
        img = cv2.imread(img_path)
        if img is None: continue
        h, w, _ = img.shape
        
        # 1. Vẽ Label (Màu Đỏ - Nét dày nhất 4px)
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = list(map(float, line.split()))
                    if len(parts) < 5: continue
                    coords = parts[1:]
                    points = np.array([[int(coords[i]*w), int(coords[i+1]*h)] for i in range(0, len(coords), 2)])
                    x1, y1 = np.min(points, axis=0); x2, y2 = np.max(points, axis=0)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(img, "Label", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 2. Vẽ Model A (Màu Xanh lá - Nét 3px)
        res_a = model_a(img_path, conf=0.2, verbose=False)
        for box in res_a[0].boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(img, "Model A", (x1, y1+25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 3. Vẽ Model B (Màu Xanh dương - Nét 3px - Dịch nhẹ tọa độ)
        res_b = model_b(img_path, conf=0.2, verbose=False)
        for box in res_b[0].boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = map(int, box)
            # Dịch tọa độ +5px để không bị trùng hoàn toàn với Model A
            cv2.rectangle(img, (x1+5, y1+5), (x2+5, y2+5), (255, 0, 0), 3)
            cv2.putText(img, "Model B", (x1+5, y2+25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
        cv2.imwrite(os.path.join(output_folder, img_name), img)
        print(f"Đã vẽ: {img_name}")

if __name__ == '__main__':
    # Đường dẫn 2 model cần so sánh
    model_a = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\models\train_results_20260620_233507\weights\best.pt"
    model_b = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\models\train_results_20260621_193353\weights\best.pt"
    
    image_folder = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\images"
    label_folder = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\labels"
    
    draw_multi_comparison(model_a, model_b, image_folder, label_folder, "comparison_results_all")