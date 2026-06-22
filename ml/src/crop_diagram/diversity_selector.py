# ml/src/crop_diagram/diversity_selector.py
import numpy as np

class DiversitySelector:
    def __init__(self, top_k=30):
        """
        top_k: Số lượng ảnh tối đa hệ thống được phép giữ lại để đưa vào VLM sinh flashcard.
        """
        self.top_k = top_k

    def select_maximum_diversity(self, candidate_crops, embeddings):
        """
        Tối đa hóa khoảng cách biên ngữ nghĩa (Semantic Distance Maximization)
        candidate_crops: Danh sách thông tin metadata của các ảnh đã crop.
        embeddings: Danh sách các mảng vector tương ứng xếp theo đúng thứ tự.
        """
        total_candidates = len(candidate_crops)
        
        # Nếu tổng số lượng ảnh cắt được ít hơn hoặc bằng quota quy định, lấy hết không cần lọc
        if total_candidates <= self.top_k:
            return candidate_crops

        # Mảng lưu trữ chỉ số index của các tấm ảnh ĐÃ ĐƯỢC CHỌN
        selected_indices = []
        
        # Bước 1: Chọn tấm ảnh mốc đầu tiên. 
        # Chúng ta chọn tấm ảnh có điểm Confidence từ YOLO lớn nhất để làm mốc chất lượng.
        confitudes = [item.get("confidence", 0) for item in candidate_crops]
        best_first_step = int(np.argmax(confitudes))
        selected_indices.append(best_first_step)

        # Bước 2: Thực hiện vòng lặp giải thuật tham lam (Greedy Strategy) để nhặt 29 tấm còn lại
        while len(selected_indices) < self.top_k:
            max_min_distance = -1.0
            best_candidate_idx = -1

            for i in range(total_candidates):
                # Không xét lại các tấm ảnh đã nằm trong hàng đợi tuyển chọn
                if i in selected_indices:
                    continue

                # Tính khoảng cách hình học ngữ nghĩa (1.0 - Cosine Similarity) tới toàn bộ các ảnh đã chọn
                distances_to_selected = []
                for sel_idx in selected_indices:
                    # Vì vector đã được L2-normalize ở module trước, dot product chính là Cosine Similarity
                    cosine_sim = np.dot(embeddings[i], embeddings[sel_idx])
                    distance = 1.0 - cosine_sim  # Khoảng cách càng lớn, hai ảnh càng khác biệt nhau về bản chất
                    distances_to_selected.append(distance)

                # Tìm khoảng cách GẦN NHẤT từ ứng viên i tới tập hợp các ảnh đã chọn
                min_distance_to_cluster = min(distances_to_selected)

                # Kỹ thuật Chọn Đa dạng: Ta muốn tìm ứng viên nằm "xa" cụm đã chọn nhất 
                # (tức là giá trị min_distance_to_cluster phải đạt cực đại)
                if min_distance_to_cluster > max_min_distance:
                    max_min_distance = min_distance_to_cluster
                    best_candidate_idx = i

            # Đóng gói ứng viên xuất sắc nhất vào danh sách đã chọn
            if best_candidate_idx != -1:
                selected_indices.append(best_candidate_idx)
            else:
                break

        # Trả về danh sách metadata của 30 tấm ảnh có độ phủ tri thức lớn nhất
        return [candidate_crops[idx] for idx in selected_indices]