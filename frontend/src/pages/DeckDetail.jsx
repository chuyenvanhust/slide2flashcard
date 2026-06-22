// pages/DeckDetail.jsx — All cards in a deck, filter by type, search, detail panel

import { useState, useRef } from "react";
import { useDeck, useDecks } from "../hooks/useDeck";
import Badge from "../components/common/Badge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import FlashCard from "../components/flashcard/FlashCard";
import { TYPE_META, RATING_META, CARD_TYPES, BACKEND_DOMAIN } from "../constants";

export default function DeckDetail({ deckId, onStudy, onBack, onNavigate }) {
  const { deck, cards, loading, updateDeckName, removeCard, editCard, transferCards } = useDeck(deckId);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isSelectMode, setIsSelectMode] = useState(false);
  const [selectedCards, setSelectedCards] = useState([]);
  const [transferMode, setTransferMode] = useState(null);
  const [targetDeckId, setTargetDeckId] = useState("");
  const [newTargetName, setNewTargetName] = useState("");
  const [showMultiDeleteConfirm, setShowMultiDeleteConfirm] = useState(false);
  const { decks } = useDecks(); // Hook to get other decks
  
  const timerRef = useRef(null);
  const isLongPress = useRef(false);

  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState("");
  const [modalMode, setModalMode] = useState(null);
  const [editBuffer, setEditBuffer] = useState("");

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
        <button onClick={onBack} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <div>
          {isRenaming ? (
            <input 
              autoFocus
              value={newName} 
              onChange={e => setNewName(e.target.value)}
              onBlur={() => { if(newName) updateDeckName(newName); setIsRenaming(false); }}
              onKeyDown={e => { if(e.key === 'Enter') { updateDeckName(newName); setIsRenaming(false); }}}
              style={{ fontSize: 18, fontFamily: "'DM Sans', sans-serif", fontWeight: 600, padding: 4, border: "1px solid #cbd5e1", borderRadius: 4 }}
            />
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <h2 style={{ margin: 0, color: "#0f172a", fontSize: 18, fontFamily: "'DM Sans', sans-serif", fontWeight: 600 }}>
                {deck?.name ? deck.name.split(/[/\\]/).pop().replace(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}_/, '') : ""}
              </h2>
              <button onClick={() => { setNewName(deck.name); setIsRenaming(true); }} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", padding: 0 }}>✎</button>
            </div>
          )}
          <div style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace", marginTop: 4 }}>{cards.length} flashcard</div>
        </div>
        
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button
            onClick={() => onNavigate("upload", deckId)}
            style={{ padding: "8px 18px", borderRadius: 8, border: "1px solid #cbd5e1", background: "#fff", color: "#475569", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", fontWeight: 600, transition: "all 0.15s" }}
            onMouseEnter={(e) => { e.target.style.borderColor = "#94a3b8"; e.target.style.background = "#f8fafc"; }}
            onMouseLeave={(e) => { e.target.style.borderColor = "#cbd5e1"; e.target.style.background = "#fff"; }}
          >
            + Upload PDF
          </button>
          {deck?.due_cards > 0 && (
            <button
              onClick={() => onStudy(deckId)}
              style={{ padding: "8px 18px", borderRadius: 8, border: "none", background: "#2563eb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", fontWeight: 600 }}
            >
              Học ngay ({deck.due_cards})
            </button>
          )}
        </div>
      </div>

      {/* Filter bar */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {["all", ...CARD_TYPES].map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            style={{
              padding: "6px 16px", borderRadius: 20,
              border: `1px solid ${filter === t ? (TYPE_META[t]?.color || "#2563eb") : "#e2e8f0"}`,
              background: filter === t ? (TYPE_META[t]?.bg || "#eff6ff") : "#ffffff",
              color: filter === t ? (TYPE_META[t]?.color || "#2563eb") : "#64748b",
              fontFamily: "'DM Mono', monospace", fontSize: 12, fontWeight: 500, cursor: "pointer",
            }}
          >
            {t === "all" ? "Tất cả" : TYPE_META[t]?.label}
          </button>
        ))}
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Tìm trong text..."
          style={{ marginLeft: "auto", padding: "6px 14px", borderRadius: 20, border: "1px solid #e2e8f0", background: "#ffffff", color: "#0f172a", fontFamily: "'DM Mono', monospace", fontSize: 12, outline: "none", width: 180 }}
        />
      </div>

      {/* Card grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
        {filtered.map((card) => (
          <div
            key={card.id}
            onPointerDown={(e) => {
              if (e.button === 2 || isSelectMode) return;
              isLongPress.current = false;
              timerRef.current = setTimeout(() => {
                isLongPress.current = true;
                setIsSelectMode(true);
                setSelectedCards(prev => [...new Set([...prev, card.id])]);
                timerRef.current = null;
                if (window.navigator && window.navigator.vibrate) {
                  window.navigator.vibrate(50);
                }
              }, 500);
            }}
            onPointerUp={() => {
              if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
              }
              if (isLongPress.current) {
                setTimeout(() => isLongPress.current = false, 100);
                return;
              }
              if (isSelectMode) {
                if (selectedCards.includes(card.id)) {
                  setSelectedCards(selectedCards.filter(id => id !== card.id));
                } else {
                  setSelectedCards([...selectedCards, card.id]);
                }
              } else {
                setSelected(card); setIsFlipped(false); setModalMode(null); 
              }
            }}
            onPointerLeave={(e) => {
              if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
              }
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)";
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-4px)";
              e.currentTarget.style.boxShadow = "0 12px 20px -5px rgba(0,0,0,0.1)";
            }}
            onContextMenu={(e) => {
              e.preventDefault();
              if (!isSelectMode) {
                setIsSelectMode(true);
                setSelectedCards(prev => [...new Set([...prev, card.id])]);
              }
            }}
            style={{
              position: "relative",
              background: (selected?.id === card.id || selectedCards.includes(card.id)) ? "#eff6ff" : "#ffffff",
              border: `2px solid ${(selected?.id === card.id || selectedCards.includes(card.id)) ? "#3b82f6" : "#e2e8f0"}`,
              borderRadius: 12, overflow: "hidden", cursor: "pointer", transition: "all 0.15s",
              boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
            }}
          >
            {isSelectMode && (
              <div style={{ position: "absolute", top: 8, right: 8, width: 22, height: 22, borderRadius: 6, border: "2px solid #3b82f6", background: selectedCards.includes(card.id) ? "#3b82f6" : "rgba(255,255,255,0.9)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 10 }}>
                {selectedCards.includes(card.id) && <span style={{ color: "white", fontSize: 14, fontWeight: "bold" }}>✓</span>}
              </div>
            )}
            <div style={{ aspectRatio: "16/9", overflow: "hidden", background: "#f8fafc", borderBottom: `1px solid ${(selected?.id === card.id || selectedCards.includes(card.id)) ? "#93c5fd" : "#e2e8f0"}` }}>
              <img src={card.image_path?.startsWith("http") ? card.image_path : `${BACKEND_DOMAIN}${card.image_path}`} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
            </div>
            <div style={{ padding: "12px 14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <Badge type={card.card_type} />
                <span style={{ fontSize: 10, color: "#94a3b8", fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>Slide {card.source_page}</span>
              </div>
              <p style={{ margin: 0, fontSize: 12, color: "#475569", lineHeight: 1.5, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                {card.back_text}
              </p>
              {card.last_rating && (
                <div style={{ marginTop: 8, fontSize: 11, color: RATING_META[card.last_rating]?.color || "#64748b", fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>
                  ● {RATING_META[card.last_rating]?.label}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Flashcard Modal */}
      {selected && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 20, animation: "overlayFade 0.2s ease-out forwards" }}>
          <div style={{ background: "white", padding: modalMode === 'delete' ? 32 : 24, borderRadius: 16, width: "100%", maxWidth: modalMode === 'delete' ? 400 : 600, boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)", maxHeight: "90vh", overflowY: "auto", textAlign: modalMode === 'delete' ? "center" : "left", animation: "modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards" }}>
            {modalMode !== 'delete' && (
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <h3 style={{ margin: 0, fontFamily: "'DM Sans', sans-serif", fontSize: 18, color: "#0f172a" }}>Chi tiết Flashcard</h3>
                <button onClick={() => { setSelected(null); setModalMode(null); }} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer", color: "#64748b", padding: 0, lineHeight: 1 }}>✕</button>
              </div>
            )}

            {modalMode === 'edit' ? (
              <>
                <textarea 
                  value={editBuffer}
                  onChange={e => setEditBuffer(e.target.value)}
                  style={{ width: "100%", height: 160, padding: 16, border: "1px solid #cbd5e1", borderRadius: 8, marginBottom: 24, fontFamily: "inherit", fontSize: 15, resize: "vertical", outline: "none", lineHeight: 1.6 }}
                />
                <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
                  <button onClick={() => setModalMode(null)} style={{ padding: "10px 20px", borderRadius: 8, border: "1px solid #e2e8f0", background: "#f8fafc", cursor: "pointer", fontWeight: 500, fontFamily: "'DM Mono', monospace", color: "#475569" }}>Hủy</button>
                  <button onClick={async () => { await editCard(selected.id, editBuffer); setSelected({ ...selected, back_text: editBuffer }); setModalMode(null); }} style={{ padding: "10px 20px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>Lưu thay đổi</button>
                </div>
              </>
            ) : modalMode === 'delete' ? (
              <>
                <div style={{ width: 48, height: 48, borderRadius: "50%", background: "#fee2e2", color: "#ef4444", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, margin: "0 auto 16px" }}>✕</div>
                <h3 style={{ margin: "0 0 12px 0", fontFamily: "'DM Sans', sans-serif", fontSize: 18, color: "#0f172a" }}>Xóa Flashcard này?</h3>
                <p style={{ margin: "0 0 24px 0", color: "#64748b", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.5 }}>
                  Bạn có chắc chắn muốn xóa Flashcard này khỏi bộ bài không? Hành động này không thể hoàn tác.
                </p>
                <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
                  <button onClick={() => setModalMode(null)} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "1px solid #e2e8f0", background: "#f8fafc", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", color: "#475569" }}>Hủy</button>
                  <button onClick={async () => { await removeCard(selected.id); setSelected(null); setModalMode(null); }} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "none", background: "#ef4444", color: "white", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>Xóa ngay</button>
                </div>
              </>
            ) : (
              <>
                <div style={{ marginBottom: 16, display: "flex", justifyContent: "center" }}>
                  <FlashCard card={selected} flipped={isFlipped} onFlip={() => setIsFlipped(!isFlipped)} />
                </div>
                <div style={{ textAlign: "center", marginBottom: 24, fontSize: 13, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>Click vào thẻ để lật</div>
                <div style={{ display: "flex", justifyContent: "center", gap: 16, borderTop: "1px solid #e2e8f0", paddingTop: 24 }}>
                  <button onClick={() => { setEditBuffer(selected.back_text); setModalMode('edit'); }} style={{ flex: 1, maxWidth: 160, padding: "12px 24px", borderRadius: 10, border: "1px solid #cbd5e1", background: "#fff", color: "#475569", cursor: "pointer", fontFamily: "'DM Mono', monospace", fontWeight: 600, transition: "all 0.15s" }} onMouseEnter={e => e.target.style.background="#f8fafc"} onMouseLeave={e => e.target.style.background="#fff"}>Sửa thẻ</button>
                  <button onClick={() => setModalMode('delete')} style={{ flex: 1, maxWidth: 160, padding: "12px 24px", borderRadius: 10, border: "1px solid #fecaca", background: "#fff", color: "#ef4444", cursor: "pointer", fontFamily: "'DM Mono', monospace", fontWeight: 600, transition: "all 0.15s" }} onMouseEnter={e => e.target.style.background="#fee2e2"} onMouseLeave={e => e.target.style.background="#fff"}>Xóa thẻ</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Selection Action Bar */}
      {isSelectMode && (
        <div style={{ position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)", background: "rgba(255, 255, 255, 0.9)", backdropFilter: "blur(12px)", border: "1px solid #e2e8f0", padding: "12px 24px", borderRadius: 100, display: "flex", alignItems: "center", gap: 16, boxShadow: "0 10px 25px -5px rgba(0,0,0,0.1)", zIndex: 50 }}>
          <span style={{ color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontWeight: 600 }}>Đã chọn {selectedCards.length} thẻ</span>
          {selectedCards.length > 0 && (
             <>
                <div style={{ width: 1, height: 20, background: "#e2e8f0" }} />
                <button onClick={() => setTransferMode("copy")} style={{ background: "transparent", border: "none", color: "#2563eb", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", fontSize: 14 }}>Sao chép</button>
                <button onClick={() => setTransferMode("move")} style={{ background: "transparent", border: "none", color: "#ea580c", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", fontSize: 14 }}>Di chuyển</button>
                <button onClick={() => setShowMultiDeleteConfirm(true)} style={{ background: "transparent", border: "none", color: "#ef4444", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", fontSize: 14 }}>Xóa</button>
             </>
          )}
          <div style={{ width: 1, height: 20, background: "#e2e8f0" }} />
          <button onClick={() => {
            if (selectedCards.length === filtered.length) {
              setSelectedCards([]);
            } else {
              setSelectedCards(filtered.map(c => c.id));
            }
          }} style={{ background: "transparent", border: "none", color: "#475569", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", fontSize: 14 }}>{selectedCards.length === filtered.length ? "Bỏ chọn tất cả" : "Chọn tất cả"}</button>
          <button onClick={() => { setIsSelectMode(false); setSelectedCards([]); }} style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", fontSize: 14 }}>Hủy</button>
        </div>
      )}

      {/* Transfer Modal */}
      {transferMode && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 20, animation: "overlayFade 0.2s ease-out forwards" }}>
          <div style={{ background: "white", padding: 28, borderRadius: 16, width: "100%", maxWidth: 420, boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)", animation: "modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards" }}>
            <h3 style={{ margin: "0 0 20px 0", fontFamily: "'DM Sans', sans-serif", fontSize: 18, color: "#0f172a" }}>
              {transferMode === "copy" ? "Sao chép" : "Di chuyển"} {selectedCards.length} thẻ tới:
            </h3>
            
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: "block", marginBottom: 8, fontSize: 14, color: "#475569", fontWeight: 500 }}>Chọn bộ thẻ có sẵn:</label>
              <select value={targetDeckId} onChange={e => { setTargetDeckId(e.target.value); setNewTargetName(""); }} style={{ width: "100%", padding: "12px", borderRadius: 8, border: "1px solid #cbd5e1", fontSize: 15 }}>
                <option value="">-- Chọn bộ thẻ --</option>
                {decks?.filter(d => d.id !== parseInt(deckId)).map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            
            <div style={{ textAlign: "center", margin: "20px 0", color: "#94a3b8", fontSize: 13, fontWeight: 600 }}>HOẶC</div>
            
            <div style={{ marginBottom: 28 }}>
              <label style={{ display: "block", marginBottom: 8, fontSize: 14, color: "#475569", fontWeight: 500 }}>Tạo bộ thẻ mới:</label>
              <input value={newTargetName} onChange={e => { setNewTargetName(e.target.value); setTargetDeckId(""); }} placeholder="Nhập tên bộ thẻ mới..." style={{ width: "100%", padding: "12px", borderRadius: 8, border: "1px solid #cbd5e1", fontSize: 15 }} />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
              <button onClick={() => setTransferMode(null)} style={{ padding: "12px 24px", borderRadius: 8, border: "1px solid #e2e8f0", background: "#f8fafc", cursor: "pointer", fontWeight: 500, color: "#475569", fontFamily: "'DM Mono', monospace" }}>Hủy</button>
              <button 
                disabled={!targetDeckId && !newTargetName}
                onClick={async () => { 
                  await transferCards(selectedCards, targetDeckId || null, newTargetName || null, transferMode);
                  setTransferMode(null);
                  setIsSelectMode(false);
                  setSelectedCards([]);
                }} 
                style={{ padding: "12px 24px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", cursor: "pointer", fontWeight: 600, opacity: (!targetDeckId && !newTargetName) ? 0.5 : 1, fontFamily: "'DM Mono', monospace" }}
              >
                Xác nhận
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Multi Delete Confirm Modal */}
      {showMultiDeleteConfirm && (
        <div style={{ position: "fixed", inset: 0, zIndex: 100, background: "rgba(15,23,42,0.6)", display: "flex", alignItems: "center", justifyContent: "center", backdropFilter: "blur(4px)", animation: "overlayFade 0.2s ease-out forwards" }} onClick={(e) => { e.stopPropagation(); setShowMultiDeleteConfirm(false); }}>
          <div style={{ background: "#fff", width: "90%", maxWidth: 400, borderRadius: 16, padding: 32, boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)", textAlign: "center", animation: "modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards" }} onClick={e => e.stopPropagation()}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "#fee2e2", color: "#ef4444", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, margin: "0 auto 16px" }}>
              ✕
            </div>
            <h3 style={{ margin: "0 0 12px 0", fontFamily: "'DM Sans', sans-serif", fontSize: 18, color: "#0f172a" }}>Xóa {selectedCards.length} thẻ?</h3>
            <p style={{ margin: "0 0 24px 0", color: "#64748b", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.5 }}>
              Bạn có chắc chắn muốn xóa <strong>{selectedCards.length}</strong> thẻ đã chọn? Hành động này không thể hoàn tác.
            </p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button onClick={() => setShowMultiDeleteConfirm(false)} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "1px solid #e2e8f0", background: "#f8fafc", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace", color: "#475569" }}>Hủy</button>
              <button onClick={async () => {
                setShowMultiDeleteConfirm(false);
                for(let id of selectedCards) await removeCard(id);
                setIsSelectMode(false);
                setSelectedCards([]);
              }} style={{ flex: 1, padding: "10px 0", borderRadius: 8, border: "none", background: "#ef4444", color: "white", cursor: "pointer", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>Xóa ngay</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
