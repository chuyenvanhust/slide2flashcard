// pages/DeckDetail.jsx — All cards in a deck, filter by type, search, detail panel

import { useState } from "react";
import { useDeck } from "../hooks/useDeck";
import Badge from "../components/common/Badge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { TYPE_META, RATING_META, CARD_TYPES } from "../constants";

export default function DeckDetail({ deckId, onStudy, onBack }) {
  const { deck, cards, loading } = useDeck(deckId);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);

  if (loading) return <LoadingSpinner />;

  const filtered = cards.filter((c) => {
    if (filter !== "all" && c.card_type !== filter) return false;
    if (search && !c.back_text.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.5)", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <div>
          <h2 style={{ margin: 0, color: "#e6edf3", fontSize: 18, fontFamily: "'DM Sans', sans-serif" }}>{deck?.name}</h2>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", fontFamily: "monospace" }}>{cards.length} flashcard</div>
        </div>
        {deck?.due_cards > 0 && (
          <button
            onClick={() => onStudy(deckId)}
            style={{ marginLeft: "auto", padding: "8px 18px", borderRadius: 8, border: "none", background: "#1f6feb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 12, cursor: "pointer" }}
          >
            Học ngay ({deck.due_cards})
          </button>
        )}
      </div>

      {/* Filter bar */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {["all", ...CARD_TYPES].map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            style={{
              padding: "5px 14px", borderRadius: 20,
              border: `1px solid ${filter === t ? (TYPE_META[t]?.color || "#58a6ff") : "rgba(255,255,255,0.1)"}`,
              background: filter === t ? `${TYPE_META[t]?.color || "#58a6ff"}18` : "transparent",
              color: filter === t ? (TYPE_META[t]?.color || "#58a6ff") : "rgba(255,255,255,0.4)",
              fontFamily: "monospace", fontSize: 11, cursor: "pointer",
            }}
          >
            {t === "all" ? "Tất cả" : TYPE_META[t]?.label}
          </button>
        ))}
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Tìm trong text..."
          style={{ marginLeft: "auto", padding: "5px 12px", borderRadius: 20, border: "1px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)", color: "#e6edf3", fontFamily: "monospace", fontSize: 11, outline: "none", width: 180 }}
        />
      </div>

      {/* Card grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 10 }}>
        {filtered.map((card) => (
          <div
            key={card.id}
            onClick={() => setSelected(selected?.id === card.id ? null : card)}
            style={{
              background: selected?.id === card.id ? "#161b26" : "#0d1117",
              border: `1px solid ${selected?.id === card.id ? "rgba(88,166,255,0.4)" : "rgba(255,255,255,0.07)"}`,
              borderRadius: 10, overflow: "hidden", cursor: "pointer", transition: "all 0.15s",
            }}
          >
            <div style={{ aspectRatio: "16/9", overflow: "hidden", background: "#000" }}>
              <img src={card.image_path} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
            </div>
            <div style={{ padding: "10px 12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <Badge type={card.card_type} />
                <span style={{ fontSize: 9, color: "rgba(255,255,255,0.25)", fontFamily: "monospace" }}>Slide {card.source_page}</span>
              </div>
              <p style={{ margin: 0, fontSize: 11, color: "rgba(255,255,255,0.5)", lineHeight: 1.5, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                {card.back_text}
              </p>
              {card.last_rating && (
                <div style={{ marginTop: 6, fontSize: 10, color: RATING_META[card.last_rating]?.color || "#888", fontFamily: "monospace" }}>
                  ● {RATING_META[card.last_rating]?.label}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Detail panel */}
      {selected && (
        <div style={{ marginTop: 20, background: "#0d1117", border: "1px solid rgba(88,166,255,0.2)", borderRadius: 14, padding: "24px 28px" }}>
          <div style={{ display: "flex", gap: 20 }}>
            <img src={selected.image_path} alt="" style={{ width: 260, borderRadius: 8, objectFit: "contain", background: "#000", flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
                <Badge type={selected.card_type} />
                <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", fontFamily: "monospace", alignSelf: "center" }}>
                  Slide {selected.source_page} · confidence {Math.round(selected.confidence * 100)}%
                </span>
              </div>
              <p style={{ color: "#c9d1d9", fontSize: 14, lineHeight: 1.8, margin: 0 }}>{selected.back_text}</p>
              <div style={{ marginTop: 16, fontSize: 11, color: "rgba(255,255,255,0.3)", fontFamily: "monospace" }}>
                Ôn tập {selected.review_count} lần · Interval {selected.interval} ngày
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
