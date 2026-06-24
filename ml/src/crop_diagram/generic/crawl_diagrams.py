r"""
ml\src\crop_diagram\generic\crawl_diagrams.py

Crawl ảnh trực tiếp từ Google Images qua Selenium.
  - KEYWORD_SETS   : ảnh diagram (có label khi sinh dataset).
  - ANTI_KEYWORD_SET: ảnh không phải diagram (dán lên slide không kèm label,
    giúp model học phân biệt diagram thật với các nội dung hình ảnh khác).

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

# ── KEYWORD SETS (ảnh diagram — sẽ được gán label) ────────────────────────
KEYWORD_SETS = {
    "diagram": [
        # Architecture
        "https://www.google.com.vn/search?q=System+Architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=software+architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=microservice+architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=cloud+architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=aws+architecture+diagram&udm=2",
        "https://www.google.com.vn/search?q=database+architecture+diagram&udm=2",
        # Flowchart
        "https://www.google.com.vn/search?q=flowchart&udm=2",
        "https://www.google.com.vn/search?q=process+flowchart&udm=2",
        "https://www.google.com.vn/search?q=business+flowchart&udm=2",
        "https://www.google.com.vn/search?q=workflow+diagram&udm=2",
        "https://www.google.com.vn/search?q=decision+flowchart&udm=2",
        # UML
        "https://www.google.com.vn/search?q=uml+class+diagram&udm=2",
        "https://www.google.com.vn/search?q=uml+sequence+diagram&udm=2",
        "https://www.google.com.vn/search?q=uml+activity+diagram&udm=2",
        "https://www.google.com.vn/search?q=uml+component+diagram&udm=2",
        "https://www.google.com.vn/search?q=uml+deployment+diagram&udm=2",
        "https://www.google.com.vn/search?q=uml+state+machine+diagram&udm=2",
        # ERD
        "https://www.google.com.vn/search?q=entity+relationship+diagram&udm=2",
        "https://www.google.com.vn/search?q=database+erd&udm=2",
        "https://www.google.com.vn/search?q=database+schema+diagram&udm=2",
        # State machine
        "https://www.google.com.vn/search?q=state+machine+diagram&udm=2",
        "https://www.google.com.vn/search?q=state+transition+diagram&udm=2",
        "https://www.google.com.vn/search?q=finite+state+machine+diagram&udm=2",
        # Network
        "https://www.google.com.vn/search?q=network+topology+diagram&udm=2",
        "https://www.google.com.vn/search?q=computer+network+diagram&udm=2",
        "https://www.google.com.vn/search?q=network+architecture+diagram&udm=2",
        # Mind map
        "https://www.google.com.vn/search?q=mind+map&udm=2",
        "https://www.google.com.vn/search?q=concept+map&udm=2",
        "https://www.google.com.vn/search?q=knowledge+map&udm=2",
        # Block diagram
        "https://www.google.com.vn/search?q=block+diagram&udm=2",
        "https://www.google.com.vn/search?q=functional+block+diagram&udm=2",
        "https://www.google.com.vn/search?q=system+block+diagram&udm=2",
        # Engineering
        "https://www.google.com.vn/search?q=circuit+diagram&udm=2",
        "https://www.google.com.vn/search?q=electrical+wiring+diagram&udm=2",
        "https://www.google.com.vn/search?q=electronic+schematic&udm=2",
        "https://www.google.com.vn/search?q=pipeline+diagram&udm=2",
        # Charts
        "https://www.google.com.vn/search?q=column+chart&udm=2",
        "https://www.google.com.vn/search?q=bar+chart&udm=2",
        "https://www.google.com.vn/search?q=line+chart&udm=2",
        "https://www.google.com.vn/search?q=pie+chart&udm=2",
        "https://www.google.com.vn/search?q=scatter+plot&udm=2",
        "https://www.google.com.vn/search?q=area+chart&udm=2",
        "https://www.google.com.vn/search?q=histogram&udm=2",
        "https://www.google.com.vn/search?q=radar+chart&udm=2",
        "https://www.google.com.vn/search?q=tree+map+chart&udm=2",
        "https://www.google.com.vn/search?q=waterfall+chart&udm=2",
        # Educational
        "https://www.google.com.vn/search?q=learning+diagram&udm=2",
        "https://www.google.com.vn/search?q=educational+flowchart&udm=2",
        "https://www.google.com.vn/search?q=knowledge+diagram&udm=2",
        # Infographic
        "https://www.google.com.vn/search?q=infographic&udm=2",
        "https://www.google.com.vn/search?q=process+infographic&udm=2",
        "https://www.google.com.vn/search?q=timeline+infographic&udm=2",
        # Timeline
        "https://www.google.com.vn/search?q=timeline+diagram&udm=2",
        "https://www.google.com.vn/search?q=project+timeline&udm=2",
        # Decision tree
        "https://www.google.com.vn/search?q=decision+tree+diagram&udm=2",
        "https://www.google.com.vn/search?q=classification+tree&udm=2",
    ]
}

# ── ANTI KEYWORD SET (ảnh KHÔNG phải diagram — dán lên slide không có label) ──
ANTI_KEYWORD_SET = [
    # Người / stock photo
    "https://www.google.com.vn/search?q=business+people+meeting+talking&udm=2",
    "https://www.google.com.vn/search?q=smiling+professional+person&udm=2",
    "https://www.google.com.vn/search?q=happy+team+high+five&udm=2",
    "https://www.google.com.vn/search?q=stock+photo+office+working&udm=2",
    "https://www.google.com.vn/search?q=person+pointing+at+screen&udm=2",
    # Biếm họa / minh họa
    "https://www.google.com.vn/search?q=funny+business+cartoon&udm=2",
    "https://www.google.com.vn/search?q=office+humor+comic+strip&udm=2",
    "https://www.google.com.vn/search?q=doodle+icons+set&udm=2",
    "https://www.google.com.vn/search?q=hand+drawn+sketch+illustration&udm=2",
    "https://www.google.com.vn/search?q=flat+design+character+illustration&udm=2",
    # Trang trí / abstract
    "https://www.google.com.vn/search?q=abstract+background+shapes&udm=2",
    "https://www.google.com.vn/search?q=geometric+background+design&udm=2",
    "https://www.google.com.vn/search?q=slide+decorative+elements&udm=2",
    "https://www.google.com.vn/search?q=company+logo+placeholder&udm=2",
    "https://www.google.com.vn/search?q=border+frame+for+presentation&udm=2",
    # Phong cảnh / lifestyle
    "https://www.google.com.vn/search?q=nature+landscape+background&udm=2",
    "https://www.google.com.vn/search?q=city+skyline+background&udm=2",
    "https://www.google.com.vn/search?q=coffee+mug+on+desk&udm=2",
    "https://www.google.com.vn/search?q=office+supplies+flatlay&udm=2",
    # UI mockup
    "https://www.google.com.vn/search?q=mockup+laptop+screen&udm=2",
    "https://www.google.com.vn/search?q=mobile+app+ui+mockup&udm=2",
    "https://www.google.com.vn/search?q=button+ui+design&udm=2",
    "https://www.google.com.vn/search?q=web+banner+design&udm=2",
]


def crawl_one_keyword(
    keyword: str,
    label: str,
    output_root: str,
    max_num: int,
    engine: str = "google",
    min_size: tuple[int, int] = (150, 150),
) -> int:
    """Cào ảnh nổi từ 1 URL Google Images bằng Selenium."""
    url_str = str(keyword).strip()
    clean_folder_name = "url_" + hashlib.md5(url_str.encode("utf-8")).hexdigest()[:10]
    tmp_dir = Path(output_root) / "_tmp" / label / clean_folder_name
    tmp_dir.mkdir(parents=True, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    image_urls: list[str] = []
    base64_data_list: list[str] = []
    driver = None

    try:
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        logger.info(f" -> Đang render: {url_str[:80]}...")
        driver.get(url_str)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)

        img_elements = driver.find_elements(By.TAG_NAME, "img")
        for img in img_elements:
            try:
                src_val = (img.get_attribute("src")
                           or img.get_attribute("data-src")
                           or img.get_attribute("data-iurl"))
                if not src_val:
                    continue

                if src_val.startswith("data:image"):
                    m = re.search(r"base64,([a-zA-Z0-9+/=]+)", src_val)
                    if m and len(m.group(1)) > 200:
                        base64_data_list.append(m.group(1))
                elif src_val.startswith("http"):
                    if "encrypted-tbn" in src_val:
                        image_urls.append(src_val)
                    elif "gstatic.com" not in src_val and "google.com" not in src_val:
                        image_urls.append(src_val)
            except Exception:
                continue

    except Exception as e:
        logger.error(f"   Lỗi Selenium: {e}")
        return 0
    finally:
        if driver:
            driver.quit()

    unique_urls = list(dict.fromkeys(image_urls))
    unique_b64  = list(dict.fromkeys(base64_data_list))
    logger.info(f" -> {len(unique_urls)} URL + {len(unique_b64)} base64 thu được.")

    downloaded_count = 0

    for idx, b64 in enumerate(unique_b64):
        if downloaded_count >= max_num:
            break
        try:
            data = base64.b64decode(b64)
            p = tmp_dir / f"b64_{idx}_{int(time.time())}.jpg"
            p.write_bytes(data)
            downloaded_count += 1
        except Exception:
            continue

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for idx, url in enumerate(unique_urls):
        if downloaded_count >= max_num:
            break
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                ext = url.split(".")[-1].split("?")[0].lower()
                ext = ext if ext in ("jpg", "jpeg", "png", "webp") else "jpg"
                p = tmp_dir / f"download_{idx}_{int(time.time())}.{ext}"
                p.write_bytes(r.content)
                downloaded_count += 1
        except Exception:
            continue

    if downloaded_count == 0:
        return 0

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
    sleep_between: float = 1.5,
) -> dict[str, int]:
    """
    Crawl ảnh theo keyword set.

    - Nếu custom_keywords được truyền vào, dùng nó thay vì KEYWORD_SETS
      (dùng để crawl ANTI_KEYWORD_SET từ main.py).
    - label_filter: tên nhãn output (thư mục con trong output_dir).
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if custom_keywords:
        keyword_sets = {label_filter or "custom": custom_keywords}
    elif label_filter:
        keyword_sets = {label_filter: KEYWORD_SETS[label_filter]}
    else:
        keyword_sets = KEYWORD_SETS

    results: dict[str, int] = {}
    total_keywords = sum(len(kws) for kws in keyword_sets.values())
    done = 0

    for label, keywords in keyword_sets.items():
        logger.info(f"\n{'='*55}\nLabel: {label}\n{'='*55}")
        label_total = 0
        for keyword in keywords:
            done += 1
            kw_str = str(keyword).strip()
            logger.info(f"[{done}/{total_keywords}] {kw_str[:70]}")
            count = crawl_one_keyword(kw_str, label, output_dir, max_per_keyword, engine)
            logger.info(f"   → {count} ảnh hợp lệ")
            label_total += count
            time.sleep(sleep_between)
        results[label] = label_total

    tmp_root = Path(output_dir) / "_tmp"
    if tmp_root.exists():
        import shutil
        shutil.rmtree(tmp_root, ignore_errors=True)

    return results


if __name__ == "__main__":
    print("🔍 Crawl diagram images...")
    res = crawl_diagram_images(output_dir="data/raw_crawled", max_per_keyword=50)
    print(f"📊 Kết quả: {res}")