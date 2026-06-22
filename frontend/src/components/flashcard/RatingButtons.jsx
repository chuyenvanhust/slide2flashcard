// components/flashcard/RatingButtons.jsx — 4 rating buttons: again/hard/medium/easy

import { RATING_META } from "../../constants";

export default function RatingButtons({ onRate, loading }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 12, width: "100%" }}>
      {Object.entries(RATING_META).map(([key, { label, color, key: k }]) => (
        <button
          key={key}
          onClick={() => onRate(key)}
          disabled={loading}
          style={{
            padding: "16px 12px",
            borderRadius: 12,
            border: `1.5px solid ${color}40`,
            background: `${color}14`,
            color,
            fontFamily: "'DM Mono', monospace",
            fontSize: 13,
            cursor: "pointer",
            transition: "all 0.15s",
            fontWeight: 600,
          }}
          onMouseEnter={(e) => {
            e.target.style.background = `${color}28`;
            e.target.style.borderColor = color;
          }}
          onMouseLeave={(e) => {
            e.target.style.background = `${color}14`;
            e.target.style.borderColor = `${color}40`;
          }}
        >
          {label} <span style={{ opacity: 0.4, fontSize: 10 }}>[{k}]</span>
        </button>
      ))}
    </div>
  );
}
