// pages/StudySession.jsx — Main study screen: flip card + rating buttons + keyboard shortcuts

import { useEffect } from "react";
import { useStudySession } from "../hooks/useStudySession";
import FlashCard from "../components/flashcard/FlashCard";
import RatingButtons from "../components/flashcard/RatingButtons";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { RATING_META } from "../constants";

export default function StudySession({ deckId, onBack }) {
  const {
    cards, currentCard, idx, flipped, loading, done,
    stats, progress, totalReviewed, flip, rate,
  } = useStudySession(deckId);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (!flipped && e.key === " ") { e.preventDefault(); flip(); }
      if (flipped) {
        const map = { "1": "again", "2": "hard", "3": "medium", "4": "easy" };
        if (map[e.key]) rate(map[e.key]);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [flipped, flip, rate]);

  if (loading) return <LoadingSpinner />;

  // Done screen
  if (done) {
    return (
      <div style={{ maxWidth: 480, margin: "60px auto", textAlign: "center" }}>
        <div style={{ fontSize: 56, marginBottom: 20 }}>🎉</div>
        <h2 style={{ color: "#0f172a", marginBottom: 8, fontFamily: "'DM Sans', sans-serif" }}>Hoàn thành session!</h2>
        <p style={{ color: "#64748b", fontFamily: "'DM Mono', monospace", marginBottom: 28, fontSize: 14 }}>
          Đã ôn tập {totalReviewed} flashcard
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12, marginBottom: 32 }}>
          {Object.entries(RATING_META).map(([k, { label, color }]) => (
            <div key={k} style={{ background: "#ffffff", border: `1px solid ${color}40`, borderRadius: 12, padding: "16px", boxShadow: "0 2px 4px rgba(0,0,0,0.02)" }}>
              <div style={{ fontSize: 24, fontWeight: 700, color, fontFamily: "'DM Mono', monospace" }}>{stats[k]}</div>
              <div style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace", marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>
        <button onClick={onBack} style={{ padding: "12px 32px", borderRadius: 10, border: "none", background: "#2563eb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 14, fontWeight: 600, cursor: "pointer", boxShadow: "0 4px 6px rgba(37,99,235,0.2)" }}>
          ← Về trang chủ
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 620, margin: "0 auto" }}>
      {/* Progress bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 18, padding: 0, lineHeight: 1 }}>←</button>
        <div style={{ flex: 1, background: "#e2e8f0", borderRadius: 4, height: 6 }}>
          <div style={{ height: "100%", borderRadius: 4, width: `${progress}%`, background: "#2563eb", transition: "width 0.4s ease" }} />
        </div>
        <span style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace", whiteSpace: "nowrap", fontWeight: 500 }}>
          {idx + 1} / {cards.length}
        </span>
      </div>

      {/* Card */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
        <FlashCard card={currentCard} flipped={flipped} onFlip={flip} />
      </div>

      {/* Controls */}
      {!flipped ? (
        <div style={{ textAlign: "center", width: "100%" }}>
          <button onClick={flip} style={{ width: "100%", padding: "16px 24px", borderRadius: 12, border: "2px solid #e2e8f0", background: "#ffffff", color: "#0f172a", fontFamily: "'DM Mono', monospace", fontSize: 16, fontWeight: 600, cursor: "pointer", boxShadow: "0 4px 6px rgba(0,0,0,0.05)", transition: "all 0.15s" }}>
            Xem giải thích <span style={{ color: "#94a3b8", marginLeft: 4, fontWeight: 400 }}>[Space]</span>
          </button>
        </div>
      ) : (
        <RatingButtons onRate={rate} />
      )}

      <div style={{ textAlign: "center", marginTop: 20, fontSize: 11, color: "#94a3b8", fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>
        {flipped ? "Phím 1–4 để đánh giá" : "Click card hoặc Space để lật"}
      </div>
    </div>
  );
}
