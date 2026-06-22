# ml/src/crop_diagram/engine.py
import fitz
from ultralytics import YOLO
import os
import cv2
import re
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from sklearn.cluster import DBSCAN

class DiagramCropper:
    def __init__(self, model_path=None):
        # 1. Tự động lấy đường dẫn tuyệt đối của thư mục chứa file engine.py hiện tại
        # current_dir sẽ là: C:\Users\trumx\slide2flashcard\ml\src\crop_diagram
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Nếu không truyền gì hoặc truyền chuỗi tương đối mặc định cũ
        if model_path is None or model_path == "ml/src/crop_diagram/models/best.pt":
            # Ghép thành đường dẫn tuyệt đối chính xác tới thư mục models
            model_path = os.path.join(current_dir, "models", "best.pt")
        elif not os.path.isabs(model_path):
            # Nếu truyền một đường dẫn tương đối khác từ ngoài vào, chuyển thành tuyệt đối
            model_path = os.path.abspath(model_path)
            
        # 2. Kiểm tra sự tồn tại của file weights một cách chính xác
        if not os.path.exists(model_path):
            print(f"⚠️ Cảnh báo: Không tìm thấy mô hình tại {model_path}!")
            print(f"👉 Hãy đảm bảo file 'prod_best_1.pt' đã được đặt trong: {os.path.join(current_dir, 'models')}")
            model_path = "yolo11n.pt" 
        else:
            print(f"🎯 ĐÃ TÌM THẤY WEIGHTS PRODUCTION TẠI: {model_path}")
            
        self.model = YOLO(model_path)
        print(f"✅ Đã tải mô hình thành công từ: {model_path}")
        
        # 2. Khởi tạo mạng ResNet50 để làm Image Embedder (Cắt bỏ layer phân loại cuối)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.embedder = torch.nn.Sequential(*(list(resnet.children())[:-1]))
        self.embedder.eval()
        self.embedder.to(self.device)
        
        # Bộ tiền xử lý ảnh bắt buộc cho ResNet50
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
    def sanitize_name(self, name):
        base_name = os.path.splitext(name)[0]
        return re.sub(r'[^\w\s-]', '', base_name).strip().replace(' ', '_')

    def _calculate_iou_matrix(self, boxes_coords):
        """Tính ma trận khoảng cách hình học tùy biến: 1 - IoU"""
        n = len(boxes_coords)
        iou_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                ax1, ay1, ax2, ay2 = boxes_coords[i]
                bx1, by1, bx2, by2 = boxes_coords[j]
                
                # Tính toán vùng giao (Intersection)
                inter_x1 = max(ax1, bx1)
                inter_y1 = max(ay1, by1)
                inter_x2 = min(ax2, bx2)
                inter_y2 = min(ay2, by2)
                inter_w = max(0, inter_x2 - inter_x1)
                inter_h = max(0, inter_y2 - inter_y1)
                intersection = inter_w * inter_h
                
                # Tính toán vùng hợp (Union)
                area_a = (ax2 - ax1) * (ay2 - ay1)
                area_b = (by2 - by1) * (bx2 - bx1)
                union = area_a + area_b - intersection
                
                iou = intersection / union if union > 0 else 0
                iou_matrix[i, j] = 1.0 - iou  # Khoảng cách tỷ lệ nghịch với IoU
        return iou_matrix

    def _get_image_embedding(self, cv2_img):
        """Trích xuất Vector Embedding 2048 chiều đã được chuẩn hóa L2 từ ảnh OpenCV"""
        if cv2_img is None or cv2_img.size == 0:
            return None
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        tensor_img = self.transform(pil_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.embedder(tensor_img).flatten().cpu().numpy()
        norm = np.linalg.norm(embedding)
        return embedding / norm if norm > 0 else embedding

    def _select_maximum_diversity(self, candidate_results, embeddings, top_k=30, similarity_threshold=0.95):
        """Thuật toán tham lam (Greedy MMR) chọn ra top_k ảnh xa nhau nhất trong không gian vector"""
        total_candidates = len(candidate_results)
        if total_candidates == 0:
            return []

        selected_indices = []
        # Tấm ảnh đầu tiên: Nhặt tấm có độ tin cậy (Confidence) cao nhất hệ thống
        confidences = [item["confidence"] for item in candidate_results]
        selected_indices.append(int(np.argmax(confidences)))

        # Vòng lặp tham lam nhặt các tấm tiếp theo dựa trên khoảng cách ngữ nghĩa hình ảnh
        while len(selected_indices) < min(top_k, total_candidates):
            max_min_distance = -1.0
            best_candidate_idx = -1

            for i in range(total_candidates):
                if i in selected_indices:
                    continue

                distances_to_selected = []
                for sel_idx in selected_indices:
                    # Vì vector đã L2-normalized, dot product chính là Cosine Similarity
                    cosine_sim = np.dot(embeddings[i], embeddings[sel_idx])
                    distance = 1.0 - cosine_sim  # Khoảng cách biên ngữ nghĩa
                    distances_to_selected.append(distance)

                # Lấy khoảng cách ngắn nhất đến các ảnh đã chọn
                min_distance = min(distances_to_selected)

                # Lọc đa dạng hóa: Chọn ảnh có khoảng cách ngắn nhất đạt giá trị cực đại
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_candidate_idx = i

            # Thêm chốt chặn loại bỏ trùng lặp:
            # Nếu tấm ảnh khác biệt nhất còn lại cũng chỉ có distance rất nhỏ (VD < 0.05 tức là giống > 95% với ảnh đã chọn)
            # Thì ta dừng việc lấy thêm ảnh để tránh lấy phải ảnh rác/ảnh trùng.
            if max_min_distance < (1.0 - similarity_threshold):
                break

            if best_candidate_idx != -1:
                selected_indices.append(best_candidate_idx)
            else:
                break

        return [candidate_results[idx] for idx in selected_indices]

    def run(self, pdf_path, output_base_dir="storage/crops", eps=0.8, min_samples=1, top_k=30):
        doc = fitz.open(pdf_path)
        pdf_filename = os.path.basename(pdf_path)
        folder_name = self.sanitize_name(pdf_filename)
        
        final_output_dir = os.path.join(output_base_dir, folder_name)
        os.makedirs(final_output_dir, exist_ok=True)
        
        temp_dir = "ml/outputs/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        raw_candidates = []
        all_embeddings = []
        
        # --- GIAI ĐOẠN 1: QUÉT TRANG SLIDE VÀ PHÂN CỤM HÌNH HỌC (DBSCAN) ---
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            img_temp_path = os.path.join(temp_dir, f"temp_{folder_name}_p{page_idx}.png")
            pix.save(img_temp_path)
            
            # YOLO Inference (Cấu hình chiến thuật: hạ conf nhẹ để không sót bảng/sơ đồ mờ)
            yolo_results = self.model.predict(
                img_temp_path, 
                conf=0.20,          # Hạ thấp hơn nữa để bắt trọn các ca khó
                iou=0.15,          
               

                       
            )
            
            img = cv2.imread(img_temp_path)
            if img is None: 
                if os.path.exists(img_temp_path): os.remove(img_temp_path)
                continue

            boxes = yolo_results[0].boxes
            if len(boxes) > 0:
                boxes_coords = boxes.xyxy.cpu().numpy()
                
                # Áp dụng Module 1: Tính toán ma trận IoU và chạy cụm DBSCAN
                iou_matrix = self._calculate_iou_matrix(boxes_coords)
                clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed').fit(iou_matrix)
                labels = clustering.labels_

                # Duyệt qua từng cụm sơ đồ rạch ròi trên trang slide
                for cluster_id in set(labels):
                    if cluster_id == -1:
                        continue  # Bỏ qua các hộp rác/nhiễu li ti không tạo thành cụm

                    cluster_indices = np.where(labels == cluster_id)[0]
                    cluster_coords = boxes_coords[cluster_indices]
                    cluster_boxes = boxes[cluster_indices]

                    # Áp dụng công thức Min-Max thu về ranh giới bao trùm thực thể lớn nhất
                    x1_final = int(np.min(cluster_coords[:, 0]))
                    y1_final = int(np.min(cluster_coords[:, 1]))
                    x2_final = int(np.max(cluster_coords[:, 2]))
                    y2_final = int(np.max(cluster_coords[:, 3]))

                    # Thêm lề padding 10px an toàn
                    h, w, _ = img.shape
                    x1_final = max(0, x1_final - 10)
                    y1_final = max(0, y1_final - 10)
                    x2_final = min(w, x2_final + 10)
                    y2_final = min(h, y2_final + 10)

                    # Chọn nhãn có độ tin cậy tốt nhất trong cụm
                    best_box_idx = cluster_boxes.conf.argmax()
                    label = self.model.names[int(cluster_boxes.cls[best_box_idx])]
                    conf_score = float(cluster_boxes.conf[best_box_idx])
                    
                    crop = img[y1_final:y2_final, x1_final:x2_final]
                    if crop.size > 0:
                        # Áp dụng Module 2: Trích xuất vectơ ngữ nghĩa của ảnh đã crop
                        emb = self._get_image_embedding(crop)
                        
                        # Lưu tạm ảnh vào RAM dữ liệu
                        raw_candidates.append({
                            "source_pdf": pdf_filename,
                            "folder_tag": folder_name,
                            "page_number": page_idx + 1,
                            "label": label,
                            "confidence": conf_score,
                            "bbox": [x1_final, y1_final, x2_final, y2_final],
                            "_crop_img": crop, # Giữ tạm ma trận ảnh trong RAM để chọn lọc sau
                            "cluster_id": cluster_id
                        })
                        all_embeddings.append(emb)
            
            # Dọn dẹp ảnh tạm ngay sau khi xử lý xong trang để tránh tràn ổ đĩa
            if os.path.exists(img_temp_path):
                os.remove(img_temp_path)
        
        doc.close()
        
        # --- GIAI ĐOẠN 2: TỐI ƯU HÓA BAO PHỦ THỰC THỂ (DIVERSITY SELECTOR) ---
        # Áp dụng Module 3: Lọc lấy 30 tấm ảnh đa dạng tri thức nhất dựa trên không gian vector
        final_selected_crops = self._select_maximum_diversity(raw_candidates, all_embeddings, top_k=top_k)
        
        # Ghi các tệp ảnh thành phẩm vật lý xuống bộ nhớ SSD
        results = []
        for idx, item in enumerate(final_selected_crops):
            crop_filename = f"{folder_name}_page{item['page_number']}_c{item['cluster_id']}_{item['label']}_final.png"
            crop_path = os.path.join(final_output_dir, crop_filename)
            
            cv2.imwrite(crop_path, item["_crop_img"])
            
            # Đóng gói dữ liệu đầu ra chuẩn chỉnh đồng bộ với tầng API phía sau
            results.append({
                "source_pdf": item["source_pdf"],
                "folder_tag": item["folder_tag"],
                "page_number": item["page_number"],
                "label": item["label"],
                "confidence": item["confidence"],
                "crop_path": crop_path,
                "bbox": item["bbox"]
            })
            
        # Xóa folder temp nếu trống
        try:
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass

        return results