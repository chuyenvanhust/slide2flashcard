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
  uploadPDF: async (file, deckId = null) => {
    const formData = new FormData();
    formData.append("file", file);
    if (deckId) {
      formData.append("deck_id", deckId);
    }
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

  // 9. Lấy dữ liệu thống kê tổng hợp
  getStats: async () => {
    const response = await fetch(`${BASE_URL}/stats/summary`);
    if (!response.ok) throw new Error("Lỗi khi tải dữ liệu thống kê");
    return response.json();
  },

  // 10. Tạo Deck mới rỗng
  createDeck: async (name) => {
    const response = await fetch(`${BASE_URL}/decks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, source_file: "" }),
    });
    if (!response.ok) throw new Error("Lỗi khi tạo bộ bài");
    return response.json();
  },

  // 11. Cập nhật tên Deck
  updateDeck: async (id, name) => {
    const response = await fetch(`${BASE_URL}/decks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (!response.ok) throw new Error("Lỗi khi đổi tên bộ bài");
    return response.json();
  },

  // 12. Cập nhật văn bản thẻ
  updateCard: async (id, backText) => {
    const response = await fetch(`${BASE_URL}/decks/cards/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ back_text: backText }),
    });
    if (!response.ok) throw new Error("Lỗi khi cập nhật thẻ");
    return response.json();
  },

  // 13. Xóa thẻ
  deleteCard: async (id) => {
    const response = await fetch(`${BASE_URL}/decks/cards/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Lỗi khi xóa thẻ");
    return response.json();
  },

  // 14. Sao chép hoặc Di chuyển các thẻ
  transferCards: async (cardIds, targetDeckId, targetDeckName, action) => {
    const response = await fetch(`${BASE_URL}/decks/cards/transfer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        card_ids: cardIds, 
        target_deck_id: targetDeckId,
        target_deck_name: targetDeckName,
        action: action 
      }),
    });
    if (!response.ok) throw new Error(`Lỗi khi ${action} thẻ`);
    return response.json();
  },
};