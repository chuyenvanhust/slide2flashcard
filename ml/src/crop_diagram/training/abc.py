import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Đường dẫn đến các thư mục labels
label_paths = [
    os.path.join(ROOT_DIR, 'dataset/train/labels'), 
    os.path.join(ROOT_DIR, 'dataset/valid/labels'),  # Trong ảnh của bạn là 'valid', không phải 'val'
    os.path.join(ROOT_DIR, 'dataset/test/labels')
]

def transform_labels(directory):
    count_deleted = 0
    count_transformed = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.split()
                if not parts: continue
                
                class_id = int(parts[0])
                
                # 1. Xóa Formula (ID 2)
                if class_id == 2:
                    count_deleted += 1
                    continue
                
                # 2. Gộp Chart (0) và Diagram (1) thành ID 0 mới
                if class_id == 0 or class_id == 1:
                    parts[0] = '0'
                    count_transformed += 1
                
                # 3. Chuyển Table (3) thành ID 1 mới
                elif class_id == 3:
                    parts[0] = '1'
                    count_transformed += 1
                
                new_lines.append(" ".join(parts) + "\n")
            
            with open(filepath, 'w') as f:
                f.writelines(new_lines)

    print(f"Thư mục {directory}:")
    print(f"- Đã xóa {count_deleted} nhãn Formula.")
    print(f"- Đã chuyển đổi {count_transformed} nhãn (Gộp Chart/Diagram và chỉnh lại Table).")

# Thực thi
for path in label_paths:
    if os.path.exists(path):
        transform_labels(path)
    else:
        print(f"Cảnh báo: Không tìm thấy lộ trình {path}")

print("\n--- HOÀN TẤT: Bộ nhãn đã sẵn sàng cho 2 Class: Diagram và Table ---")