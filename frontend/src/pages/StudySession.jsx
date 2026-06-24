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
        <h2 style={{ color: "#e6edf3", marginBottom: 8, fontFamily: "'DM Sans', sans-serif" }}>Hoàn thành session!</h2>
        <p style={{ color: "rgba(255,255,255,0.4)", fontFamily: "monospace", marginBottom: 28 }}>
          Đã ôn tập {totalReviewed} flashcard
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 10, marginBottom: 28 }}>
          {Object.entries(RATING_META).map(([k, { label, color }]) => (
            <div key={k} style={{ background: "#0d1117", border: `1px solid ${color}30`, borderRadius: 10, padding: "12px 16px" }}>
              <div style={{ fontSize: 22, fontWeight: 700, color, fontFamily: "'DM Mono', monospace" }}>{stats[k]}</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", fontFamily: "monospace" }}>{label}</div>
            </div>
          ))}
        </div>
        <button onClick={onBack} style={{ padding: "10px 28px", borderRadius: 10, border: "none", background: "#1f6feb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer" }}>
          ← Về trang chủ
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 620, margin: "0 auto" }}>
      {/* Progress bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.4)", cursor: "pointer", fontSize: 18, padding: 0, lineHeight: 1 }}>←</button>
        <div style={{ flex: 1, background: "rgba(255,255,255,0.06)", borderRadius: 4, height: 4 }}>
          <div style={{ height: "100%", borderRadius: 4, width: `${progress}%`, background: "#58a6ff", transition: "width 0.4s ease" }} />
        </div>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", fontFamily: "monospace", whiteSpace: "nowrap" }}>
          {idx + 1} / {cards.length}
        </span>
      </div>

      {/* Card */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
        <FlashCard card={currentCard} flipped={flipped} onFlip={flip} />
      </div>

      {/* Controls */}
      {!flipped ? (
        <div style={{ textAlign: "center" }}>
          <button onClick={flip} style={{ padding: "10px 32px", borderRadius: 10, border: "1px solid rgba(255,255,255,0.15)", background: "transparent", color: "rgba(255,255,255,0.7)", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer" }}>
            Xem giải thích <span style={{ opacity: 0.4 }}>[Space]</span>
          </button>
        </div>
      ) : (
        <RatingButtons onRate={rate} />
      )}

      <div style={{ textAlign: "center", marginTop: 16, fontSize: 10, color: "rgba(255,255,255,0.2)", fontFamily: "monospace" }}>
        {flipped ? "Phím 1–4 để đánh giá" : "Click card hoặc Space để lật"}
      </div>
    </div>
  );
}
