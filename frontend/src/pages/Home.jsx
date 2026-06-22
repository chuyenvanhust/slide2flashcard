// pages/Home.jsx — Deck grid + stats banner + upload CTA

import { useState } from "react";
import { useDecks } from "../hooks/useDeck";
import DeckList from "../components/deck/DeckList";
import LoadingSpinner from "../components/common/LoadingSpinner";

export default function Home({ onStudy, onView, onNavigate }) {
  const { decks, loading, deleteDeck, createDeck } = useDecks();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDeckName, setNewDeckName] = useState("");

  const totalDue = decks.reduce((a, d) => a + d.due_cards, 0);
  const totalCards = decks.reduce((a, d) => a + d.total_cards, 0);
  const totalKnown = decks.reduce((a, d) => a + d.known_cards, 0);

  const handleCreate = async () => {
    if (!newDeckName.trim()) return;
    const deck = await createDeck(newDeckName);
    setShowCreateModal(false);
    setNewDeckName("");
    onView(deck.id);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      {/* Header Actions */}
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 20 }}>
        <button
          onClick={() => setShowCreateModal(true)}
          style={{
            background: "#ffffff", color: "#475569",
            border: "1px solid #cbd5e1", padding: "8px 18px", borderRadius: 8,
            fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Mono', monospace",
            transition: "all 0.15s"
          }}
          onMouseEnter={(e) => { e.target.style.background = "#f8fafc"; }}
          onMouseLeave={(e) => { e.target.style.background = "#ffffff"; }}
        >
          + Create new deck
        </button>
      </div>

      {/* Stats banner */}
      {decks.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 28 }}>
          {[
            { label: "Tổng flashcard", value: totalCards, color: "#58a6ff" },
            { label: "Đã nắm vững",    value: totalKnown,  color: "#3fb950" },
            { label: "Cần ôn tập",     value: totalDue,    color: "#f78166" },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 20px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: 24, fontWeight: 700, color, fontFamily: "'DM Mono', monospace" }}>{value}</div>
              <div style={{ fontSize: 12, color: "#64748b", marginTop: 4, fontFamily: "'DM Mono', monospace" }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {decks.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🗂️</div>
          <div style={{ color: "#64748b", fontFamily: "'DM Sans', sans-serif" }}>
            Chưa có deck nào. Upload slide PDF để bắt đầu!
          </div>
          <button
            onClick={() => onNavigate("upload")}
            style={{ marginTop: 20, padding: "10px 24px", borderRadius: 10, border: "none", background: "#2563eb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 14, fontWeight: 500, cursor: "pointer", boxShadow: "0 4px 6px rgba(37,99,235,0.2)", transition: "background 0.15s" }}
            onMouseEnter={(e) => (e.target.style.background = "#1d4ed8")}
            onMouseLeave={(e) => (e.target.style.background = "#2563eb")}
          >
            Upload PDF
          </button>
        </div>
      ) : (
        <DeckList
          decks={decks}
          onStudy={onStudy}
          onView={onView}
          onDelete={deleteDeck}
        />
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100
        }}>
          <div style={{ background: "white", padding: 24, borderRadius: 12, width: 400, boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)" }}>
            <h2 style={{ margin: "0 0 16px 0", fontFamily: "'DM Sans', sans-serif" }}>Create new deck</h2>
            <input 
              autoFocus
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
              placeholder="Tên bộ thẻ (ví dụ: Toán Cao Cấp)"
              style={{ width: "100%", padding: "10px 12px", border: "1px solid #cbd5e1", borderRadius: 6, marginBottom: 20, fontFamily: "inherit", fontSize: 14 }}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button onClick={() => setShowCreateModal(false)} style={{ padding: "8px 16px", borderRadius: 6, border: "none", background: "#f1f5f9", cursor: "pointer" }}>Hủy</button>
              <button onClick={handleCreate} style={{ padding: "8px 16px", borderRadius: 6, border: "none", background: "#2563eb", color: "white", cursor: "pointer", fontWeight: 500 }}>Tạo ngay</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
