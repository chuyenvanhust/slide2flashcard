from ultralytics import YOLO

def train_model():
    # Đường dẫn đến file last.pt mà YOLO đã tự lưu lần trước
    # Bạn hãy kiểm tra lại đúng đường dẫn thư mục 'runs' của bạn
    resume_path = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\models\train_results_20260621_193353\weights\last.pt"
    
    # Load model từ file last.pt
    model = YOLO(resume_path)
    
    # Sử dụng resume=True để tiếp tục training
    # Lưu ý: Không cần khai báo lại data, imgsz, hay batch_size 
    # vì nó tự lấy từ file last.pt
    model.train(resume=True)

if __name__ == '__main__':
    train_model()