// pages/Home.jsx — Deck grid + stats banner + upload CTA

import { useDecks } from "../hooks/useDeck";
import DeckList from "../components/deck/DeckList";
import LoadingSpinner from "../components/common/LoadingSpinner";

export default function Home({ onStudy, onView, onNavigate }) {
  const { decks, loading, deleteDeck } = useDecks();

  const totalDue = decks.reduce((a, d) => a + d.due_cards, 0);
  const totalCards = decks.reduce((a, d) => a + d.total_cards, 0);
  const totalKnown = decks.reduce((a, d) => a + d.known_cards, 0);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      {/* Stats banner */}
      {decks.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 28 }}>
          {[
            { label: "Tổng flashcard", value: totalCards, color: "#58a6ff" },
            { label: "Đã nắm vững",    value: totalKnown,  color: "#3fb950" },
            { label: "Cần ôn tập",     value: totalDue,    color: "#f78166" },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "16px 20px" }}>
              <div style={{ fontSize: 24, fontWeight: 700, color, fontFamily: "'DM Mono', monospace" }}>{value}</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginTop: 4, fontFamily: "monospace" }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {decks.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🗂️</div>
          <div style={{ color: "rgba(255,255,255,0.4)", fontFamily: "'DM Sans', sans-serif" }}>
            Chưa có deck nào. Upload slide PDF để bắt đầu!
          </div>
          <button
            onClick={() => onNavigate("upload")}
            style={{ marginTop: 20, padding: "10px 24px", borderRadius: 10, border: "none", background: "#1f6feb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer" }}
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
    </div>
  );
}
