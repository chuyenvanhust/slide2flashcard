from ultralytics import YOLO

# Load model tốt nhất vừa train xong
model = YOLO("C:/Users/trumx/slide2flashcard/ml/src/crop_diagram/models/train_results_VỪA_CHẠY/weights/best.pt")

# Ép mô hình chấm điểm trên tập TEST (100% ảnh thật không có ảnh giả)
metrics = model.val(split='test') 

print("Mức độ chính xác trên từng Class (mAP50):")
print(f"Diagram: {metrics.class_result(0)[2]:.4f}") # Kiểm tra xem có vượt qua 0.74 cũ không
print(f"Table: {metrics.class_result(1)[2]:.4f}")   # Kiểm tra xem có giữ được mốc ~0.88 cũ không