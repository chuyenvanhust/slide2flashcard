# ml/src/crop_diagram/image_embedder.py
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import cv2
import numpy as np
from PIL import Image

class ImageEmbedder:
    def __init__(self):
        # Thiết lập thiết bị phần cứng tối ưu
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load mạng ResNet50 pre-trained chuẩn công nghiệp
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        # Cắt bỏ tầng phân loại Fully Connected cuối cùng để lấy đặc trưng thô (Feature Map)
        self.model = torch.nn.Sequential(*(list(resnet.children())[:-1]))
        self.model.eval()
        self.model.to(self.device)
        
        # Bộ pipeline tiền xử lý ảnh đầu vào bắt buộc của PyTorch Vision
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def extract_embedding(self, cv2_img):
        """Chuyển đổi ma trận ảnh OpenCV thành Vector L2-Normalized 2048 chiều"""
        if cv2_img is None or cv2_img.size == 0:
            return None
            
        # Chuyển đổi hệ màu từ BGR (OpenCV) sang RGB (PIL)
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        
        # Tiền xử lý và đẩy tensor dữ liệu vào GPU/CPU
        tensor_img = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            # Trích xuất và làm phẳng đặc trưng về dạng mảng 1D
            embedding = self.model(tensor_img).flatten().cpu().numpy()
            
        # Chuẩn hóa L2 (L2-Normalization) để độ dài vector bằng 1.0, hỗ trợ tính tích vô hướng Cosine nhanh hơn
        norm = np.linalg.norm(embedding)
        return embedding / norm if norm > 0 else embedding