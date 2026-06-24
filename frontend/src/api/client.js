// api/client.js — Kết nối thực tế tới Backend FastAPI an toàn

const BASE_URL = "http://localhost:8000/api/v1";

export const api = {
  // 1. Lấy danh sách Deck
  getDecks: async () => {
    const response = await fetch(`${BASE_URL}/decks`);
    if (!response.ok) throw new Error("Lỗi khi tải danh sách bộ bài");
    return response.json();
  },

  // 2. Chi tiết 1 Deck
  getDeck: async (id) => {
    const response = await fetch(`${BASE_URL}/decks/${id}`);
    if (!response.ok) throw new Error("Không tìm thấy bộ bài");
    return response.json();
  },

  // 3. Lấy tất cả các thẻ của một bộ (Đã bổ sung hàm bị thiếu!)
  getCards: async (deckId) => {
    const response = await fetch(`${BASE_URL}/decks/${deckId}/cards`);
    // Nếu backend chưa có API này, tạm trả về mảng rỗng để web không bị crash
    if (!response.ok) return [];
    return response.json();
  },

  // 4. Lấy thẻ đến hạn học
  getDueCards: async (deckId) => {
    const response = await fetch(`${BASE_URL}/decks/${deckId}/cards/due`);
    if (!response.ok) return [];
    return response.json();
  },

  // 5. Submit kết quả đánh giá (SM-2)
  submitReview: async (cardId, rating) => {
    const response = await fetch(`${BASE_URL}/cards/${cardId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating }),
    });
    if (!response.ok) throw new Error("Lỗi khi lưu đánh giá");
    return response.json();
  },

  // 6. Xóa Deck
  deleteDeck: async (id) => {
    const response = await fetch(`${BASE_URL}/decks/${id}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Lỗi khi xóa bộ bài");
    return response.json();
  },

  // 7. Upload file PDF
  uploadPDF: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error("Lỗi khi upload file");
    return response.json();
  },

  // 8. Poll trạng thái AI
  getJobStatus: async (jobId) => {
    const response = await fetch(`${BASE_URL}/upload/status/${jobId}`);
    if (!response.ok) throw new Error("Lỗi khi lấy trạng thái");
    return response.json();
  },
};