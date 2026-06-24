import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Tự động lấy đường dẫn tuyệt đối đến thư mục 'backend' chứa file database.py này
# os.path.abspath(__file__) -> .../backend/core/database.py
# dirname đầu tiên -> .../backend/core
# dirname thứ hai -> .../backend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

# Cố định vị trí file DB nằm ngay trong thư mục backend
DB_PATH = os.path.join(BACKEND_DIR, "slide2flashcard.db")

# 2. Cấu hình chuỗi kết nối sử dụng đường dẫn tuyệt đối chuẩn xác
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 3. Khởi tạo engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()