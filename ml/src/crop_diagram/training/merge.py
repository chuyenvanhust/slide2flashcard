import os
import shutil
from pathlib import Path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAM_DIR = Path(os.path.join(ROOT_DIR, "dataset"))
TABLE_DIR = Path(os.path.join(ROOT_DIR, "dataset_table"))
OUTPUT_DIR = Path(os.path.join(ROOT_DIR, "dataset_merged_final"))

# Map lớp table từ ID 0 sang ID 1
TABLE_CLASS_MAPPING = {0: 1}

# Bổ sung thêm 'test' vào danh sách xử lý cho đúng cấu trúc của bạn
SPLITS = ['train', 'valid', 'test']

def init_output_dirs():
    for split in SPLITS:
        (OUTPUT_DIR / split / 'images').mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / split / 'labels').mkdir(parents=True, exist_ok=True)

def copy_diagram_dataset():
    print("📦 Bước 1: Đang sao chép tập dữ liệu Diagram...")
    for split in SPLITS:
        img_src_dir = DIAGRAM_DIR / split / 'images'
        lbl_src_dir = DIAGRAM_DIR / split / 'labels'
        
        if not img_src_dir.exists():
            continue
            
        for img_path in img_src_dir.glob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                shutil.copy2(img_path, OUTPUT_DIR / split / 'images' / img_path.name)
                
        for lbl_path in lbl_src_dir.glob("*.txt"):
            shutil.copy2(lbl_path, OUTPUT_DIR / split / 'labels' / lbl_path.name)

def merge_table_dataset():
    print("⚡ Bước 2: Đang remap ID và gộp tập dữ liệu Table...")
    for split in SPLITS:
        img_src_dir = TABLE_DIR / split / 'images'
        lbl_src_dir = TABLE_DIR / split / 'labels'
        
        if not img_src_dir.exists():
            continue
            
        for lbl_path in lbl_src_dir.glob("*.txt"):
            new_filename_base = f"table_{lbl_path.stem}"
            new_lbl_name = f"{new_filename_base}.txt"
            
            corresponding_img = None
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                potential_img = img_src_dir / f"{lbl_path.stem}{ext}"
                if potential_img.exists():
                    corresponding_img = potential_img
                    break
            
            if not corresponding_img:
                continue
                
            new_lines = []
            with open(lbl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    try:
                        old_id = int(parts[0])
                        new_id = TABLE_CLASS_MAPPING.get(old_id, old_id)
                        parts[0] = str(new_id)
                        new_lines.append(" ".join(parts) + "\n")
                    except ValueError:
                        new_lines.append(line)
                        
            with open(OUTPUT_DIR / split / 'labels' / new_lbl_name, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            new_img_name = f"{new_filename_base}{corresponding_img.suffix}"
            shutil.copy2(corresponding_img, OUTPUT_DIR / split / 'images' / new_img_name)

def create_yaml_file():
    yaml_content = f"""# Cấu hình Dataset hợp nhất
train: ../train/images
val: ../valid/images
test: ../test/images

nc: 2
names: ['diagram', 'table']
"""
    with open(OUTPUT_DIR / 'data.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

if __name__ == "__main__":
    init_output_dirs()
    copy_diagram_dataset()
    merge_table_dataset()
    create_yaml_file()
    print("🎉 Xong! Thư mục 'dataset_merged_final' đã sẵn sàng.")