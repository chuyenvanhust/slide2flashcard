from datetime import datetime, timedelta
from typing import Tuple

def calculate_sm2(
    rating: str, 
    current_interval: int = 0, 
    current_ease: float = 2.5
) -> Tuple[datetime, int, float]:
    """
    Thuật toán SuperMemo-2 (SM-2)
    Returns: (next_review_date, new_interval, new_ease_factor)
    """
    # Chuyển đổi rating dạng chữ sang quality (0-5)
    quality_map = {
        "again": 0,   # Quên sạch
        "hard": 2,    # Nhớ nhưng rất khó khăn
        "medium": 4,  # Nhớ sau khi do dự
        "easy": 5     # Nhớ ngay lập tức
    }
    q = quality_map.get(rating, 0)

    # 1. Tính toán Interval (Khoảng cách ngày ôn tập tiếp theo)
    if q < 3: # Nếu đánh giá là again hoặc hard -> Học lại từ đầu
        new_interval = 1
    elif current_interval == 0: # Thẻ mới học lần đầu
        new_interval = 1
    elif current_interval == 1: # Học lần thứ 2
        new_interval = 6
    else: # Từ lần thứ 3 trở đi
        new_interval = int(round(current_interval * current_ease))

    # 2. Tính toán Ease Factor (Hệ số sụt giảm)
    # Công thức gốc của SM-2: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    new_ease = current_ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    
    # E-factor không bao giờ được nhỏ hơn 1.3
    if new_ease < 1.3:
        new_ease = 1.3

    # 3. Tính ngày review tiếp theo
    next_review = datetime.utcnow() + timedelta(days=new_interval)

    return next_review, new_interval, round(new_ease, 2)