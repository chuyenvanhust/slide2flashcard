// components/flashcard/CardFront.jsx
import Badge from "../common/Badge";
import { BACKEND_DOMAIN } from "../../constants";

export default function CardFront({ card }) {
  // Đảm bảo URL luôn trỏ về port 8000
  const imageUrl = card.image_path.startsWith("http") 
    ? card.image_path 
    : `${BACKEND_DOMAIN}${card.image_path}`;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backfaceVisibility: "hidden",
        borderRadius: 16,
        overflow: "hidden",
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
      }}
    >
      <img
        src={imageUrl}
        alt="diagram"
        style={{ width: "100%", height: "100%", objectFit: "contain", background: "#f8fafc" }}
        draggable={false}
      />
      <div style={{ position: "absolute", top: 12, left: 12 }}>
        <Badge type={card.card_type} />
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 12,
          right: 14,
          fontSize: 10,
          color: "#64748b",
          fontFamily: "'DM Mono', monospace",
          fontWeight: 500,
          background: "rgba(255,255,255,0.8)",
          padding: "4px 8px",
          borderRadius: 6,
          backdropFilter: "blur(4px)",
        }}
      >
        Slide {card.source_page} · click để xem giải thích
      </div>
    </div>
  );
}
