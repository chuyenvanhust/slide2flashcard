// components/upload/ProcessingStatus.jsx — Stepper: Extract→Detect→OCR→Match→Done

import { STEP_LABELS } from "../../constants";
import ProgressBar from "../common/ProgressBar";

export default function ProcessingStatus({ status }) {
  if (!status) return null;

  const isDone = status.status === "done";
  const isFail = status.status === "failed";

  const statusColor = isDone ? "#3fb950" : isFail ? "#f85149" : "#58a6ff";
  const statusLabel = isDone ? "✓ Hoàn thành" : isFail ? "✕ Lỗi" : "⟳ Đang xử lý";

  return (
    <div
      style={{
        background: "#0d1117",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14,
        padding: "24px 28px",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ color: statusColor, fontSize: 13, fontFamily: "'DM Mono', monospace", fontWeight: 600 }}>
          {statusLabel}
        </span>
        <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, fontFamily: "monospace" }}>
          {status.progress}%
        </span>
      </div>

      {/* Progress bar */}
      <ProgressBar
        pct={status.progress}
        color={isDone ? "#3fb950" : "#58a6ff"}
        style={{ marginBottom: 18 }}
      />

      {/* Steps stepper */}
      <div style={{ display: "flex", gap: 0, marginBottom: 16 }}>
        {STEP_LABELS.map((label, i) => {
          const done = i < status.step_index || isDone;
          const active = i === status.step_index && !isDone;
          return (
            <div key={i} style={{ flex: 1, textAlign: "center" }}>
              <div
                style={{
                  width: 28, height: 28, borderRadius: "50%",
                  margin: "0 auto 6px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  background: done ? "#3fb950" : active ? "#1f6feb" : "rgba(255,255,255,0.06)",
                  border: `2px solid ${done ? "#3fb950" : active ? "#58a6ff" : "rgba(255,255,255,0.1)"}`,
                  fontSize: 11,
                  color: done || active ? "#fff" : "rgba(255,255,255,0.3)",
                  transition: "all 0.3s",
                }}
              >
                {done ? "✓" : i + 1}
              </div>
              <div style={{ fontSize: 9, color: done ? "#3fb950" : active ? "#58a6ff" : "rgba(255,255,255,0.25)", fontFamily: "monospace" }}>
                {label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Message */}
      <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", fontFamily: "monospace" }}>
        {status.message}
      </div>

      {/* Done banner */}
      {isDone && status.created_cards > 0 && (
        <div
          style={{
            marginTop: 12, padding: "10px 14px",
            background: "rgba(63,185,80,0.08)",
            borderRadius: 8, border: "1px solid rgba(63,185,80,0.2)",
            fontSize: 12, color: "#3fb950", fontFamily: "monospace",
          }}
        >
          🎉 Tạo được {status.created_cards} flashcard từ slide của bạn
        </div>
      )}
    </div>
  );
}
