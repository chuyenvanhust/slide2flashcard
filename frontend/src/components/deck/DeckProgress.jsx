// components/deck/DeckProgress.jsx — Progress bar showing new/learning/known counts

import ProgressBar from "../common/ProgressBar";

export default function DeckProgress({ deck }) {
  const { total_cards, known_cards, due_cards } = deck;
  const knownPct = total_cards > 0 ? Math.round((known_cards / total_cards) * 100) : 0;
  const color = knownPct > 70 ? "#3fb950" : knownPct > 40 ? "#e3b341" : "#58a6ff";

  return (
    <div>
      <ProgressBar pct={knownPct} color={color} height={4} />
      <div
        style={{
          display: "flex",
          gap: 16,
          marginTop: 8,
          fontSize: 12,
          fontFamily: "'DM Mono', monospace",
        }}
      >
        <span style={{ color: "#3fb950" }}>✓ {known_cards} biết</span>
        <span style={{ color: "#f78166" }}>↻ {due_cards} ôn tập</span>
        <span style={{ color: "rgba(255,255,255,0.35)" }}>{total_cards} tổng</span>
      </div>
    </div>
  );
}
