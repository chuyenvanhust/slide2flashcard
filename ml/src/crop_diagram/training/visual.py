import os
from ultralytics import YOLO

def run_visual_evaluation():
    # 1. Đường dẫn mô hình tốt nhất (dựa trên bảng so sánh trước đó của bạn)
    # Hãy thay bằng folder mô hình có chỉ số tốt nhất mà bạn đã chọn
    best_model_folder = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\models\train_results_20260620_233507"
    best_model_path = os.path.join(best_model_folder, "weights", "best.pt")
    
    # 2. Đường dẫn tập test (ảnh)
    # Trỏ đến thư mục chứa ảnh test của bạn
    test_images_path = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\images"
    
    # 3. Load model
    model = YOLO(best_model_path)
    
    # 4. Chạy dự đoán
    # save=True: lưu ảnh có vẽ box
    # conf=0.25: ngưỡng tự tin, bạn có thể chỉnh theo Best_Conf đã tìm được
    # visualize=False: không cần lưu feature maps để chạy cho nhanh
    print(f"Đang chạy dự đoán trên tập test với model: {best_model_folder}")
    results = model.predict(
        source=test_images_path,
        conf=0.2, 
        save=True, 
        save_txt=True,    # Lưu cả tọa độ box ra file txt để debug
        project='runs/detect', 
        name='final_visual_test',
        exist_ok=True
    )
    
    print("\nĐã hoàn thành!")
    print("Mở thư mục sau để xem kết quả: C:\\Users\\trumx\\slide2flashcard\\ml\\src\\crop_diagram\\runs\\detect\\final_visual_test")

if __name__ == '__main__':
    run_visual_evaluation()