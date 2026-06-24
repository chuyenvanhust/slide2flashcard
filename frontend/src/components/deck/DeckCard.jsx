// components/deck/DeckCard.jsx — Deck preview card: name, stats, actions

import { useState } from "react";
import { TYPE_META } from "../../constants";
import ProgressRing from "../common/ProgressRing";

export default function DeckCard({ deck, onStudy, onDelete, onView }) {
  const pct = deck.total_cards > 0
    ? Math.round((deck.known_cards / deck.total_cards) * 100)
    : 0;
  const [hover, setHover] = useState(false);

  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: hover ? "#161b26" : "#0d1117",
        border: `1px solid ${hover ? "rgba(88,166,255,0.3)" : "rgba(255,255,255,0.07)"}`,
        borderRadius: 14,
        padding: "20px 22px",
        transition: "all 0.2s",
        cursor: "default",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: 0, color: "#e6edf3", fontSize: 15, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", lineHeight: 1.3 }}>
            {deck.name}
          </h3>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginTop: 4, fontFamily: "monospace" }}>
            {deck.source_file}
          </div>
        </div>
        <div style={{ position: "relative" }}>
          <ProgressRing
            pct={pct} size={44} stroke={3}
            color={pct > 70 ? "#3fb950" : pct > 40 ? "#e3b341" : "#58a6ff"}
          />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#e6edf3", fontFamily: "monospace", fontWeight: 700 }}>
            {pct}%
          </div>
        </div>
      </div>

      {/* Type pills */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
        {Object.entries(deck.card_types || {})
          .filter(([, n]) => n > 0)
          .map(([t, n]) => (
            <span
              key={t}
              style={{ padding: "2px 8px", borderRadius: 20, fontSize: 10, background: TYPE_META[t]?.bg, color: TYPE_META[t]?.color, fontFamily: "monospace" }}
            >
              {n} {t}
            </span>
          ))}
      </div>

      {/* Stats */}
      <div style={{ display: "flex", gap: 16, marginBottom: 16, fontSize: 12, fontFamily: "monospace" }}>
        <span style={{ color: "#3fb950" }}>✓ {deck.known_cards} biết</span>
        <span style={{ color: "#f78166" }}>↻ {deck.due_cards} ôn tập</span>
        <span style={{ color: "rgba(255,255,255,0.35)" }}>{deck.total_cards} tổng</span>
      </div>

      {/* Actions */}
      <div style={{ display: "flex", gap: 8 }}>
        {deck.due_cards > 0 && (
          <button
            onClick={() => onStudy(deck.id)}
            style={{ flex: 1, padding: "8px", borderRadius: 8, border: "none", background: "#1f6feb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 12, cursor: "pointer", fontWeight: 600, transition: "background 0.15s" }}
            onMouseEnter={(e) => (e.target.style.background = "#388bfd")}
            onMouseLeave={(e) => (e.target.style.background = "#1f6feb")}
          >
            Học ngay ({deck.due_cards})
          </button>
        )}
        <button
          onClick={() => onView(deck.id)}
          style={{ flex: 1, padding: "8px", borderRadius: 8, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "rgba(255,255,255,0.6)", fontFamily: "'DM Mono', monospace", fontSize: 12, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={(e) => { e.target.style.borderColor = "rgba(255,255,255,0.3)"; e.target.style.color = "#fff"; }}
          onMouseLeave={(e) => { e.target.style.borderColor = "rgba(255,255,255,0.1)"; e.target.style.color = "rgba(255,255,255,0.6)"; }}
        >
          Xem tất cả
        </button>
        <button
          onClick={() => onDelete(deck.id)}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid rgba(248,81,73,0.2)", background: "transparent", color: "#f85149", fontFamily: "monospace", fontSize: 12, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={(e) => (e.target.style.background = "rgba(248,81,73,0.1)")}
          onMouseLeave={(e) => (e.target.style.background = "transparent")}
        >
          ✕
        </button>
      </div>
    </div>
  );
}
