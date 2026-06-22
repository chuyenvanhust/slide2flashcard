// components/flashcard/FlashCard.jsx — CSS 3D flip card container

import CardFront from "./CardFront";
import CardBack from "./CardBack";

export default function FlashCard({ card, flipped, onFlip }) {
  return (
    <div
      onClick={onFlip}
      style={{
        width: "100%",
        maxWidth: 560,
        aspectRatio: "16/10",
        cursor: "pointer",
        perspective: 1200,
        userSelect: "none",
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          position: "relative",
          transformStyle: "preserve-3d",
          transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
          transition: "transform 0.55s cubic-bezier(0.4,0,0.2,1)",
        }}
      >
        <CardFront card={card} />
        <CardBack card={card} />
      </div>
    </div>
  );
}
