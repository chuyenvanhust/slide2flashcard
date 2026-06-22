# ml/src/crop_diagram/spatial_cluster.py
import numpy as np
from sklearn.cluster import DBSCAN

class SpatialClusterer:
    def __init__(self, eps=0.8, min_samples=1):
        """
        eps: Ngưỡng khoảng cách hình học tối đa giữa 2 box (1 - IoU).
             eps = 0.8 đồng nghĩa với việc chỉ cần IoU > 0.2 là các box có thể thuộc về nhau.
        min_samples: Số lượng box tối thiểu để cấu thành một cụm (mặc định là 1).
        """
        self.eps = eps
        self.min_samples = min_samples

    def _calculate_iou_matrix(self, boxes_coords):
        """Tính toán ma trận khoảng cách tùy biến dựa trên công thức 1 - IoU"""
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
                area_b = (bx2 - bx1) * (bx2 - bx1)
                union = area_a + area_b - intersection
                
                iou = intersection / union if union > 0 else 0
                # Khoảng cách hình học nghịch đảo: IoU càng cao thì khoảng cách càng gần (về 0)
                iou_matrix[i, j] = 1.0 - iou  
        return iou_matrix

    def get_merged_clusters(self, yolo_boxes, img_shape):
        """
        Nhận vào boxes từ kết quả YOLO của 1 trang slide và trả ra danh sách các vùng cắt đã gộp cụm.
        """
        if len(yolo_boxes) == 0:
            return []

        h, w = img_shape[:2]
        boxes_coords = yolo_boxes.xyxy.cpu().numpy()
        
        # 1. Tính toán ma trận khoảng cách hình học và chạy DBSCAN phân cụm mật độ
        iou_dist_matrix = self._calculate_iou_matrix(boxes_coords)
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='precomputed').fit(iou_dist_matrix)
        labels = clustering.labels_

        merged_results = []

        # 2. Duyệt qua từng cụm tìm được để gộp biên hình học
        for cluster_id in set(labels):
            if cluster_id == -1:
                continue # Loại bỏ các box nhiễu (Noise) do YOLO đoán bừa, đoán sai

            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_coords = boxes_coords[cluster_indices]
            
            # Lấy các box YOLO thuộc cụm này để tìm ra nhãn có độ tự tin cao nhất
            cluster_boxes = yolo_boxes[cluster_indices]
            best_box_idx = cluster_boxes.conf.argmax()
            best_conf = float(cluster_boxes.conf[best_box_idx])
            best_label_id = int(cluster_boxes.cls[best_box_idx])

            # Áp dụng công thức Min-Max để ôm trọn toàn bộ các cấu phần con bên trong sơ đồ
            x1 = max(0, int(np.min(cluster_coords[:, 0])) - 10)
            y1 = max(0, int(np.min(cluster_coords[:, 1])) - 10)
            x2 = min(w, int(np.max(cluster_coords[:, 2])) + 10)
            y2 = min(h, int(np.max(cluster_coords[:, 3])) + 10)

            merged_results.append({
                "bbox": [x1, y1, x2, y2],
                "label_id": best_label_id,
                "confidence": best_conf
            })

        return merged_results