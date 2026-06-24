#ml\src\crop_diagram\engine.py
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if model_path is None or model_path == "ml/src/crop_diagram/models/best.pt":
            model_path = os.path.join(current_dir, "models", "best.pt")
        elif not os.path.isabs(model_path):
            model_path = os.path.abspath(model_path)
            
        if not os.path.exists(model_path):
            model_path = "yolo11n.pt" 
            
        self.model = YOLO(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.embedder = torch.nn.Sequential(*(list(resnet.children())[:-1]))
        self.embedder.eval().to(self.device)
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    # --- CÁC MODULE DÙNG CHUNG ---
    def detect_and_cluster(self, img):
        # 1. Dự đoán
        results = self.model.predict(img, conf=0.1, iou=0.5, verbose=False)[0]
        boxes = []
        for box in results.boxes:
            conf = float(box.conf)
            cls_id = int(box.cls)
            cls_name = self.model.names[cls_id]
            
            # --- ĐOẠN CODE LỌC CONF THEO CLASS ---
            # Ngưỡng table khắt khe để giảm FP, diagram linh hoạt để tăng Recall
            if cls_name == 'table' and conf < 0.84:
                continue
            if cls_name == 'diagram' and conf < 0.22:
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            boxes.append({
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "label": self.model.names[int(box.cls)],
                "conf": float(box.conf)
            })

        # 2. Xóa các box nằm trong box khác (bất kể class)
        # Sắp xếp theo diện tích giảm dần để giữ box lớn
        boxes.sort(key=lambda b: (b['x2']-b['x1'])*(b['y2']-b['y1']), reverse=True)
        survivors = []
        for i, b1 in enumerate(boxes):
            is_contained = False
            for b2 in survivors:
                if b1['x1'] >= b2['x1'] and b1['y1'] >= b2['y1'] and \
                   b1['x2'] <= b2['x2'] and b1['y2'] <= b2['y2']:
                    is_contained = True; break
            if not is_contained: survivors.append(b1)

        # 3. Gom box cùng class bằng Greedy Grouping (O(n^2))
        final_clusters = []
        while survivors:
            b1 = survivors.pop(0)
            merged = False
            for i, b2 in enumerate(survivors):
                if b1['label'] == b2['label'] and self._can_merge(b1, b2, img.shape):
                    # Gộp vào b2 (box lớn hơn hoặc bằng)
                    survivors[i] = self._merge_boxes(b1, b2)
                    merged = True; break
            if not merged: final_clusters.append(b1)
        
        return [{"bbox": [b['x1'], b['y1'], b['x2'], b['y2']], "label": b['label'], "confidence": b['conf']} for b in final_clusters]

    def _can_merge(self, b1, b2, img_shape):
        # 1. Tính toán thẳng hàng (Alignment) - Đây là điều kiện "tiên quyết"
        # Dùng tọa độ tâm để kiểm tra
        c1 = ((b1['x1']+b1['x2'])/2, (b1['y1']+b1['y2'])/2)
        c2 = ((b2['x1']+b2['x2'])/2, (b2['y1']+b2['y2'])/2)
        
        # Ngưỡng 10% chiều của box (Dựa trên trung bình chiều rộng/cao của 2 box)
        threshold_x = 0.075 * ((b1['x2']-b1['x1']) + (b2['x2']-b2['x1'])) / 2
        threshold_y = 0.075 * ((b1['y2']-b1['y1']) + (b2['y2']-b2['y1'])) / 2
        
        # Kiểm tra nằm trên trục đứng hoặc trục ngang
        is_aligned_x = abs(c1[0] - c2[0]) < threshold_x
        is_aligned_y = abs(c1[1] - c2[1]) < threshold_y
        
        if not (is_aligned_x or is_aligned_y):
            # Nếu không thẳng hàng, dù giao nhau hay gần, đều KHÔNG gộp (An toàn!)
            return False

        # 2. Tính toán khoảng cách (Gap) và Giao nhau (Overlap)
        # Logic này xử lý dist_x=0 nếu giao nhau về chiều X
        dist_x = max(b1['x1'] - b2['x2'], b2['x1'] - b1['x2'], 0)
        dist_y = max(b1['y1'] - b2['y2'], b2['y1'] - b1['y2'], 0)
        
        # 3. Tính toán giao nhau thực sự (IoU - optional, để thắt chặt FP)
        # inter_w = max(0, min(b1['x2'], b2['x2']) - max(b1['x1'], b2['x1']))
        # inter_h = max(0, min(b1['y2'], b2['y2']) - max(b1['y1'], b2['y1']))
        # if inter_w * inter_h > 0: # Có giao nhau
        #     # Nếu giao nhau mà conf quá thấp, hãy coi nó là nhiễu và không gộp
        #     if min(b1['conf'], b2['conf']) < 0.2: return False
        
        # 4. Logic quyết định gộp: Chỉ gộp khi "Thẳng hàng" VÀ (Giao nhau HOẶC Khoảng cách nhỏ)
        # Vùng giao nhau đã nằm trong logic `dist==0` (nhỏ hơn threshold).
        return (is_aligned_x and dist_x < threshold_x) or (is_aligned_y and dist_y < threshold_y)

    def _merge_boxes(self, b1, b2):
        return {
            "x1": min(b1['x1'], b2['x1']), "y1": min(b1['y1'], b2['y1']),
            "x2": max(b1['x2'], b2['x2']), "y2": max(b1['y2'], b2['y2']),
            "label": b1['label'], "conf": max(b1['conf'], b2['conf'])
        }

    def run(self, pdf_path, output_base_dir="storage/crops", eps=0.8, min_samples=1, top_k=30):
        """Production pipeline: Gọi detect_and_cluster rồi thực hiện chọn lọc đa dạng và lưu file"""
        doc = fitz.open(pdf_path)
        pdf_filename = os.path.basename(pdf_path)
        folder_name = self.sanitize_name(pdf_filename)
        final_output_dir = os.path.join(output_base_dir, folder_name)
        os.makedirs(final_output_dir, exist_ok=True)
        
        raw_candidates = []
        all_embeddings = []
        
        for page_idx in range(len(doc)):
            pix = doc[page_idx].get_pixmap(matrix=fitz.Matrix(2, 2))
            img = cv2.imdecode(np.frombuffer(pix.tobytes(), np.uint8), cv2.IMREAD_COLOR)
            
            clusters = self.detect_and_cluster(img, eps, min_samples)
            for c in clusters:
                x1, y1, x2, y2 = map(int, c['bbox'])
                crop = img[y1:y2, x1:x2]
                raw_candidates.append({**c, "page_number": page_idx+1, "_crop_img": crop, "source_pdf": pdf_filename, "folder_tag": folder_name})
                all_embeddings.append(self._get_image_embedding(crop))

        # Diversity Selector
        final_selected = self._select_maximum_diversity(raw_candidates, all_embeddings, top_k=top_k)
        
        results = []
        for item in final_selected:
            path = os.path.join(final_output_dir, f"{folder_name}_p{item['page_number']}_c{item['cluster_id']}_{item['label']}.png")
            cv2.imwrite(path, item["_crop_img"])
            results.append({**item, "crop_path": path})
        
        doc.close()
        return results

    # --- CÁC HÀM HỖ TRỢ (KEEP AS IS) ---
    def _calculate_iou_matrix(self, boxes_coords):
        n = len(boxes_coords)
        iou_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                ax1, ay1, ax2, ay2 = boxes_coords[i]
                bx1, by1, bx2, by2 = boxes_coords[j]
                inter = max(0, min(ax2, bx2) - max(ax1, bx1)) * max(0, min(ay2, by2) - max(ay1, by1))
                union = (ax2-ax1)*(ay2-ay1) + (bx2-bx1)*(by2-by1) - inter
                iou_matrix[i, j] = 1.0 - (inter / union if union > 0 else 0)
        return iou_matrix

    def _get_image_embedding(self, cv2_img):
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        tensor = self.transform(Image.fromarray(img_rgb)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            emb = self.embedder(tensor).flatten().cpu().numpy()
        return emb / np.linalg.norm(emb) if np.linalg.norm(emb) > 0 else emb

    def _select_maximum_diversity(self, candidates, embeddings, top_k):
        if len(candidates) <= top_k: return candidates
        indices = [int(np.argmax([c["confidence"] for c in candidates]))]
        while len(indices) < top_k:
            best_idx = -1
            max_min_dist = -1
            for i in range(len(candidates)):
                if i in indices: continue
                min_dist = min([1.0 - np.dot(embeddings[i], embeddings[idx]) for idx in indices])
                if min_dist > max_min_dist:
                    max_min_dist, best_idx = min_dist, i
            if best_idx != -1: indices.append(best_idx)
            else: break
        return [candidates[i] for i in indices]

    def sanitize_name(self, name):
        return re.sub(r'[^\w\s-]', '', os.path.splitext(name)[0]).strip().replace(' ', '_')