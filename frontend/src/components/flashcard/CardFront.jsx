// components/flashcard/CardFront.jsx
import Badge from "../common/Badge";

// Khai báo địa chỉ Backend (nên đưa vào file .env sau này)
const BACKEND_DOMAIN = "http://localhost:8000";

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
        border: "1px solid rgba(255,255,255,0.08)",
        background: "#0a0e1a",
        boxShadow: "0 24px 64px rgba(0,0,0,0.5)",
      }}
    >
      <img
        src={imageUrl}
        alt="diagram"
        style={{ width: "100%", height: "100%", objectFit: "contain" }}
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
          color: "rgba(255,255,255,0.25)",
          fontFamily: "monospace",
        }}
      >
        Slide {card.source_page} · click để xem giải thích
      </div>
    </div>
  );
}