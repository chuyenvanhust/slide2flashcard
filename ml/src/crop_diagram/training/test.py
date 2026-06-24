#ml\src\crop_diagram\training\test.py

import os
import sys
import glob
import cv2
import re

# Thiết lập đường dẫn gốc
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from ml.src.crop_diagram.engine import DiagramCropper

# ... (Hàm get_iou giữ nguyên như cũ) ...
def get_iou(box1, box2):
    b1_x1, b1_x2 = box1[0] - box1[2]/2, box1[0] + box1[2]/2
    b1_y1, b1_y2 = box1[1] - box1[3]/2, box1[1] + box1[3]/2
    b2_x1, b2_x2 = box2[0] - box2[2]/2, box2[0] + box2[2]/2
    b2_y1, b2_y2 = box2[1] - box2[3]/2, box2[1] + box2[3]/2
    inter_x1, inter_y1 = max(b1_x1, b2_x1), max(b1_y1, b2_y1)
    inter_x2, inter_y2 = min(b1_x2, b2_x2), min(b1_y2, b2_y2)
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    union = (box1[2]*box1[3]) + (box2[2]*box2[3]) - inter
    return inter / union if union > 0 else 0

def extract_timestamp(path):
    # Tìm chuỗi số dạng 2026xxxx_xxxxxx
    match = re.search(r'(\d{8}_\d{6})', path)
    return match.group(1) if match else os.path.basename(os.path.dirname(os.path.dirname(path)))

def evaluate_model(model_path, test_img_dir, lbl_dir):
    cropper = DiagramCropper(model_path=model_path)
    metrics = {cid: {"tp": 0, "fp": 0, "fn": 0} for cid in cropper.model.names}
    img_files = glob.glob(os.path.join(test_img_dir, "*.png")) + glob.glob(os.path.join(test_img_dir, "*.jpg"))

    for img_path in img_files:
        img = cv2.imread(img_path)
        h, w, _ = img.shape
        lbl_path = os.path.join(lbl_dir, os.path.splitext(os.path.basename(img_path))[0] + ".txt")
        gt_list = []
        if os.path.exists(lbl_path):
            with open(lbl_path, 'r') as f:
                for line in f:
                    parts = list(map(float, line.split()))
                    gt_list.append({"cls": int(parts[0]), "box": parts[1:5]})

        results = cropper.detect_and_cluster(img)
        pred_list = []
        name_to_id = {v: k for k, v in cropper.model.names.items()}
        for res in results:
            cid = name_to_id.get(res['label'])
            if cid is not None:
                pred_list.append({"cls": cid, "box_norm": [(res['bbox'][0]+(res['bbox'][2]-res['bbox'][0])/2)/w, (res['bbox'][1]+(res['bbox'][3]-res['bbox'][1])/2)/h, (res['bbox'][2]-res['bbox'][0])/w, (res['bbox'][3]-res['bbox'][1])/h]})

        matched_gt = [False] * len(gt_list)
        for pred in pred_list:
            best_iou, best_idx = 0, -1
            for i, gt in enumerate(gt_list):
                if not matched_gt[i] and pred['cls'] == gt['cls']:
                    iou = get_iou(pred['box_norm'], gt['box'])
                    if iou > best_iou: best_iou, best_idx = iou, i
            if best_iou >= 0.5:
                metrics[pred['cls']]["tp"] += 1
                matched_gt[best_idx] = True
            else:
                metrics[pred['cls']]["fp"] += 1
        for i, gt in enumerate(gt_list):
            if not matched_gt[i]: metrics[gt['cls']]["fn"] += 1
    return metrics

if __name__ == "__main__":
    IMG_DIR = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\images"
    LBL_DIR = r"C:\Users\trumx\slide2flashcard\ml\src\crop_diagram\training\dataset_merged_final\test\labels"
    MODELS = [
        r"ml\src\crop_diagram\models\train_results\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260619_004301\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260619_091532\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260619_232455\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260620_105114\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260620_233507\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260621_091731\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260621_193353\weights\best.pt",
        r"ml\src\crop_diagram\models\train_results_20260623_114655\weights\best.pt",
    ]
    
    print(f"{'Timestamp':<20} | {'Prec':<6} | {'Recall':<6} | {'F1 Total':<8} | {'TP':<5} | {'FP':<5} | {'FN':<5}")
    print("-" * 75)

    for m_path in MODELS:
        metrics = evaluate_model(m_path, IMG_DIR, LBL_DIR)
        
        # Tính tổng TP, FP, FN cho tất cả class
        total_tp = sum(m['tp'] for m in metrics.values())
        total_fp = sum(m['fp'] for m in metrics.values())
        total_fn = sum(m['fn'] for m in metrics.values())
        
        p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        
        ts = extract_timestamp(m_path)
        print(f"{ts:<20} | {p:.2f}   | {r:.2f}   | {f1:.2f}     | {total_tp:<5} | {total_fp:<5} | {total_fn:<5}")