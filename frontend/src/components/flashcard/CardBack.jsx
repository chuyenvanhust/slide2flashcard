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
        border: "1px solid rgba(255,255,255,0.1)",
        background: "#0d1422",
        boxShadow: "0 24px 64px rgba(0,0,0,0.5)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "32px 36px",
      }}
    >
      <div
        style={{
          fontSize: 10,
          color: "rgba(255,255,255,0.3)",
          fontFamily: "monospace",
          letterSpacing: 2,
          marginBottom: 18,
          textTransform: "uppercase",
        }}
      >
        Giải thích · Slide {card.source_page}
      </div>
      <p style={{ color: "#c9d1d9", fontSize: 15, lineHeight: 1.8, margin: 0 }}>
        {card.back_text}
      </p>
      <div style={{ marginTop: 20, display: "flex", gap: 8, alignItems: "center" }}>
        <Badge type={card.card_type} />
        <span style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", fontFamily: "monospace" }}>
          confidence {Math.round(card.confidence * 100)}%
        </span>
      </div>
    </div>
  );
}
