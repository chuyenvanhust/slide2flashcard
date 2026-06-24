// pages/Stats.jsx — Learning progress charts (placeholder, extend as needed)
// Suggested charts: daily review heatmap, per-deck retention, card type breakdown

export default function Stats({ onBack }) {
  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.5)", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <h2 style={{ margin: 0, color: "#e6edf3", fontFamily: "'DM Sans', sans-serif", fontSize: 18 }}>Tiến độ học tập</h2>
      </div>

      {/* Placeholder grid — wire up real charts (recharts / d3) here */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {[
          { title: "Reviews theo ngày",       hint: "Heatmap / bar chart theo ngày trong 30 ngày qua" },
          { title: "Tỉ lệ retention",          hint: "% card rated easy+medium / tổng mỗi session" },
          { title: "Card type breakdown",      hint: "Pie: diagram / chart / table / formula" },
          { title: "Deck progress overtime",   hint: "Line: % known tăng dần theo thời gian" },
        ].map(({ title, hint }) => (
          <div key={title} style={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "20px 22px", minHeight: 160 }}>
            <div style={{ fontSize: 13, color: "#e6edf3", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, marginBottom: 8 }}>{title}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", fontFamily: "monospace", lineHeight: 1.6 }}>{hint}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
