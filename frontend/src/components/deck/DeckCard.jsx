// components/deck/DeckCard.jsx — Deck preview card: name, stats, actions

import { useState } from "react";
import { TYPE_META } from "../../constants";
import ProgressRing from "../common/ProgressRing";

export default function DeckCard({ deck, onStudy, onDelete, onView }) {
  const cleanFileName = (str) => {
    if (!str) return "";
    return str.split(/[/\\]/).pop().replace(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}_/, '');
  };

  const pct = deck.total_cards > 0
    ? Math.round((deck.known_cards / deck.total_cards) * 100)
    : 0;
  const [hover, setHover] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  return (
    <>
      <div
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        style={{
          background: hover ? "#f8fafc" : "#ffffff",
          border: `1px solid ${hover ? "#cbd5e1" : "#e2e8f0"}`,
          borderRadius: 14,
          padding: "20px 22px",
          transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
          cursor: "default",
          transform: hover ? "translateY(-4px)" : "translateY(0)",
          boxShadow: hover ? "0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)" : "0 1px 3px rgba(0,0,0,0.05)",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
          <div style={{ flex: 1 }}>
            <h3 style={{ margin: 0, color: "#0f172a", fontSize: 16, fontWeight: 600, fontFamily: "'DM Sans', sans-serif", lineHeight: 1.3, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={cleanFileName(deck.name)}>
              {cleanFileName(deck.name)}
            </h3>
            <div style={{ fontSize: 12, color: "#64748b", marginTop: 4, fontFamily: "'DM Mono', monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={cleanFileName(deck.source_file)}>
              {cleanFileName(deck.source_file)}
            </div>
          </div>
          <div style={{ position: "relative" }}>
            <ProgressRing
              pct={pct} size={44} stroke={3}
              color={pct > 70 ? "#16a34a" : pct > 40 ? "#ca8a04" : "#2563eb"}
            />
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#0f172a", fontFamily: "'DM Mono', monospace", fontWeight: 700 }}>
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
                style={{ padding: "2px 8px", borderRadius: 20, fontSize: 10, background: TYPE_META[t]?.bg, color: TYPE_META[t]?.color, fontFamily: "'DM Mono', monospace" }}
              >
                {n} {t}
              </span>
            ))}
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: 16, marginBottom: 16, fontSize: 12, fontFamily: "'DM Mono', monospace" }}>
          <span style={{ color: "#16a34a" }}>✓ {deck.known_cards} biết</span>
          <span style={{ color: "#ea580c" }}>↻ {deck.due_cards} ôn tập</span>
          <span style={{ color: "#94a3b8" }}>{deck.total_cards} tổng</span>
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: 8 }}>
          {deck.due_cards > 0 && (
            <button
              onClick={() => onStudy(deck.id)}
              style={{ flex: 1, padding: "8px", borderRadius: 8, border: "none", background: "#2563eb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", fontWeight: 600, transition: "background 0.15s" }}
              onMouseEnter={(e) => (e.target.style.background = "#1d4ed8")}
              onMouseLeave={(e) => (e.target.style.background = "#2563eb")}
            >
              Học ngay ({deck.due_cards})
            </button>
          )}
          <button
            onClick={() => onView(deck.id)}
            style={{ flex: 1, padding: "8px", borderRadius: 8, border: "1px solid #e2e8f0", background: "transparent", color: "#64748b", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", transition: "all 0.15s" }}
            onMouseEnter={(e) => { e.target.style.borderColor = "#94a3b8"; e.target.style.color = "#0f172a"; e.target.style.background = "#f8fafc"; }}
            onMouseLeave={(e) => { e.target.style.borderColor = "#e2e8f0"; e.target.style.color = "#64748b"; e.target.style.background = "transparent"; }}
          >
            Xem tất cả
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #fecaca", background: "transparent", color: "#ef4444", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", transition: "all 0.15s" }}
            onMouseEnter={(e) => (e.target.style.background = "#fee2e2")}
            onMouseLeave={(e) => (e.target.style.background = "transparent")}
          >
            ✕
          </button>
        </div>
      </div>

      {/* Delete Confirm Modal */}
      {showDeleteConfirm && (
        <div style={{ position: "fixed", inset: 0, zIndex: 100, background: "rgba(15,23,42,0.6)", display: "flex", alignItems: "center", justifyContent: "center", backdropFilter: "blur(4px)", animation: "overlayFade 0.2s ease-out forwards" }} onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(false); }}>
          <div style={{ background: "#fff", width: "90%", maxWidth: 400, borderRadius: 16, padding: 32, boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)", textAlign: "center", animation: "modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards" }} onClick={e => e.stopPropagation()}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "#fee2e2", color: "#ef4444", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, margin: "0 auto 16px" }}>
              ✕
            </div>
            <h3 style={{ margin: "0 0 12px 0", fontFamily: "'DM Sans', sans-serif", fontSize: 18, color: "#0f172a" }}>Xóa bộ thẻ này?</h3>
            <p style={{ margin: "0 0 24px 0", color: "#64748b", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.5 }}>
              Bạn có chắc chắn muốn xóa bộ thẻ "<strong>{cleanFileName(deck.name)}</strong>"? Hành động này sẽ xóa toàn bộ thẻ bên trong và không thể hoàn tác.
            </p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button onClick={() => setShowDeleteConfirm(false)} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "1px solid #e2e8f0", background: "#f8fafc", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", color: "#475569" }}>Hủy</button>
              <button onClick={() => { setShowDeleteConfirm(false); onDelete(deck.id); }} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "none", background: "#ef4444", color: "white", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>Xóa ngay</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
