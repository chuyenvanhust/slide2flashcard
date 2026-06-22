from ml.pipeline import FlashcardPipeline
import json

def main():
    pdf_files = ["ml/data/lecture_1.pdf", "ml/data/lecture_2.pdf"]
    pipeline = FlashcardPipeline(limit=30)
    
    all_results = []
    for pdf in pdf_files:
        print(f"--- Đang xử lý: {pdf} ---")
        # Gọi đúng hàm .run() như đã thống nhất ở Pipeline
        results = pipeline.run(pdf) 
        all_results.extend(results)
    
    print(f"🎉 Đã hoàn thành! Tổng số flashcards: {len(all_results)}")
    with open("flashcards_result.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()