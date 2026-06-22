// components/flashcard/CardBack.jsx — Back face: explanation text + metadata

import Badge from "../common/Badge";

export default function CardBack({ card }) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backfaceVisibility: "hidden",
        transform: "rotateY(180deg)",
        borderRadius: 16,
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "32px 36px",
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: "#64748b",
          fontFamily: "'DM Mono', monospace",
          letterSpacing: 1.5,
          marginBottom: 18,
          textTransform: "uppercase",
          fontWeight: 600,
        }}
      >
        Giải thích · Slide {card.source_page}
      </div>
      <p style={{ color: "#1e293b", fontSize: 16, lineHeight: 1.7, margin: 0 }}>
        {card.back_text}
      </p>
      <div style={{ marginTop: 24, display: "flex", gap: 10, alignItems: "center" }}>
        <Badge type={card.card_type} />
        <span style={{ fontSize: 11, color: "#94a3b8", fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>
          confidence {Math.round(card.confidence * 100)}%
        </span>
      </div>
    </div>
  );
}
