r"""
ml\src\crop_diagram\generic\crawl_diagrams.py

Crawl ảnh nổi trực tiếp từ các đường dẫn (URL) Google Images được nạp vào bằng Selenium.
Không sử dụng từ khóa bừa bãi, không tự động fallback sang Bing/Baidu.
Giải quyết triệt để vấn đề bị Google chặn (0 ảnh tìm thấy) khi dùng requests thuần.
Dùng cho mục đích train nội bộ — KHÔNG dùng để publish hoặc deploy thương mại.
"""
import base64
import hashlib
import logging
import time
import re
from pathlib import Path
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# ── DANH SÁCH LINK GOOGLE ──────────────────────────────────────────────────
KEYWORD_SETS = {
    "diagram": [
        "https://www.google.com.vn/search?q=System+Architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=software+architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=system+design+diagram+flowchart&udm=2"
    ]
}

def crawl_one_keyword(
    keyword: str,
    label: str,
    output_root: str,
    max_num: int,
    engine: str = "google",
    min_size: tuple[int, int] = (150, 150),
) -> int:
    """Cào trực tiếp các ảnh nổi (URL & Base64) hiển thị trên giao diện link Google Images."""
    url_str = str(keyword).strip()
    
    # Tạo thư mục tạm dựa trên mã băm của URL
    clean_folder_name = "url_" + hashlib.md5(url_str.encode('utf-8')).hexdigest()[:10]
    tmp_dir = Path(output_root) / "_tmp" / label / clean_folder_name
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình Selenium chống bị Google nhận diện là Bot/Headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Sử dụng engine headless mới ổn định hơn
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Bypass cơ chế AutomationControlled chống chặn của Google
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    image_urls = []
    base64_data_list = []

    driver = None
    try:
        # Tự động tải và thiết lập ChromeDriver phù hợp
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Fake thông số webdriver bằng Javascript script để chắc chắn qua bộ lọc
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        logger.info(f" -> Đang kết nối và render cấu trúc trang Google...")
        driver.get(url_str)
        time.sleep(3) # Chờ 3 giây để Javascript load toàn bộ ảnh nổi lên giao diện

        # Cuộn trang nhẹ xuống để kích hoạt toàn bộ ảnh lười (lazy-load) hiển thị rõ ràng
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)

        # ✨ ĐOẠN ĐÃ SỬA ĐỔI: Sử dụng DOM Elements thay vì Regex thuần trên Page Source ✨
        logger.info(" -> Đang trích xuất dữ liệu ảnh từ các thẻ IMG trên DOM...")
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        
        for img in img_elements:
            try:
                # Quét mọi thuộc tính có khả năng lưu trữ URL ảnh của Google Images
                src_val = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("data-iurl")
                
                if not src_val:
                    continue
                
                # 1. Bóc tách nếu là chuỗi dữ liệu Base64 trực tiếp
                if src_val.startswith("data:image"):
                    b64_m = re.search(r"base64,([a-zA-Z0-9+/=]+)", src_val)
                    if b64_m:
                        b64_str = b64_m.group(1)
                        if len(b64_str) > 200:  # Lọc bỏ icon rác kích thước nhỏ
                            base64_data_list.append(b64_str)
                
                # 2. Bóc tách nếu là đường dẫn HTTP/HTTPS URL
                elif src_val.startswith("http"):
                    # Giữ lại các ảnh thumbnail mã hóa sạch của google (encrypted-tbn)
                    if "encrypted-tbn" in src_val:
                        image_urls.append(src_val)
                    # Hoặc các link ảnh từ nguồn gốc của bên thứ ba trực tiếp
                    elif "gstatic.com" not in src_val and "google.com" not in src_val:
                        image_urls.append(src_val)
            except Exception:
                continue

    except Exception as e:
        logger.error(f"   Lỗi trong quá trình render trình duyệt Selenium: {e}")
        return 0
    finally:
        if driver:
            driver.quit()

    unique_urls = list(dict.fromkeys(image_urls))
    unique_b64 = list(dict.fromkeys(base64_data_list))
    
    logger.info(f" -> Thu thập được: {len(unique_urls)} link ảnh trực tiếp & {len(unique_b64)} khối Base64 nổi từ giao diện gốc.")

    downloaded_count = 0

    # Xử lý lưu ảnh Base64 thu được
    for idx, b64_content in enumerate(unique_b64):
        if downloaded_count >= max_num:
            break
        try:
            img_data = base64.b64decode(b64_content)
            target_path = tmp_dir / f"b64_{idx}_{int(time.time())}.jpg"
            with open(target_path, "wb") as f:
                f.write(img_data)
            downloaded_count += 1
        except Exception:
            continue

    # Tải ảnh từ các link URL thu được
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for idx, img_url in enumerate(unique_urls):
        if downloaded_count >= max_num:
            break
        try:
            img_res = requests.get(img_url, headers=headers, timeout=10)
            if img_res.status_code == 200:
                ext = img_url.split('.')[-1].split('?')[0].lower()
                ext = ext if ext in ['jpg', 'jpeg', 'png', 'webp'] else 'jpg'
                
                target_path = tmp_dir / f"download_{idx}_{int(time.time())}.{ext}"
                with open(target_path, "wb") as f:
                    f.write(img_res.content)
                downloaded_count += 1
        except Exception:
            continue

    if downloaded_count == 0:
        return 0

    # ── Khối xử lý chuẩn hóa ảnh sang JPEG và lọc kích thước tối thiểu (Giữ nguyên gốc logic)
    final_dir = Path(output_root) / label
    final_dir.mkdir(parents=True, exist_ok=True)

    valid_count = 0
    for img_path in tmp_dir.glob("*"):
        try:
            with Image.open(img_path) as img:
                img.verify()
            with Image.open(img_path) as img:
                if img.width < min_size[0] or img.height < min_size[1]:
                    img_path.unlink()
                    continue
                
                content_hash = hashlib.md5(img_path.read_bytes()).hexdigest()[:10]
                new_name = f"{label}_{content_hash}.jpg"
                new_path = final_dir / new_name

                if new_path.exists():
                    img_path.unlink()
                    continue

                img.convert("RGB").save(new_path, "JPEG", quality=90)
                valid_count += 1
        except Exception:
            pass
        finally:
            if img_path.exists():
                img_path.unlink()

    return valid_count

def crawl_diagram_images(
    output_dir: str = "data/raw_crawled",
    label_filter: str | None = None,
    custom_keywords: list[str] | None = None,
    max_per_keyword: int = 80,
    engine: str = "google",
    sleep_between: float = 1.5
) -> dict[str, int]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    keyword_sets = {label_filter: custom_keywords} if custom_keywords else ( {label_filter: KEYWORD_SETS[label_filter]} if label_filter else KEYWORD_SETS )
    results = {}
    total_keywords = sum(len(kws) for kws in keyword_sets.values())
    done = 0

    for label, keywords in keyword_sets.items():
        logger.info(f"\n{'='*55}\nPhân loại Target: {label}\n{'='*55}")
        label_total = 0
        for keyword in keywords:
            done += 1
            kw_str = str(keyword).strip()
            logger.info(f"[{done}/{total_keywords}] Tiến hành tải: '{kw_str}'")
            count = crawl_one_keyword(kw_str, label, output_dir, max_per_keyword, engine)
            logger.info(f"   → Thu thập được {count} ảnh hợp lệ sạch")
            label_total += count
            time.sleep(sleep_between)
        results[label] = label_total

    tmp_root = Path(output_dir) / "_tmp"
    if tmp_root.exists():
        import shutil
        shutil.rmtree(tmp_root, ignore_errors=True)
    return results

if __name__ == "__main__":
    # Điểm kích hoạt chạy thử nghiệm trực tiếp file
    print("🔍 Đang khởi chạy hệ thống crawl ảnh mẫu...")
    res = crawl_diagram_images(output_dir="data/raw_crawled", max_per_keyword=50)
    print(f"\n📊 Kết quả tổng kết thu thập: {res}")