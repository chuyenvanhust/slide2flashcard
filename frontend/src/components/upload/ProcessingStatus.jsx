// components/upload/ProcessingStatus.jsx — Stepper: Extract→Detect→OCR→Match→Done

import { STEP_LABELS } from "../../constants";
import ProgressBar from "../common/ProgressBar";

export default function ProcessingStatus({ status }) {
  if (!status) return null;

  const isDone = status.status === "done";
  const isFail = status.status === "failed";

  const statusColor = isDone ? "#16a34a" : isFail ? "#dc2626" : "#2563eb";
  const statusLabel = isDone ? "✓ Hoàn thành" : isFail ? "✕ Lỗi" : "⟳ Đang xử lý";

  let step_index = 0;
  if (isDone) step_index = 4;
  else if (status.progress >= 80) step_index = 3;
  else if (status.progress >= 20) step_index = 2;
  else if (status.progress >= 10) step_index = 1;

  return (
    <div
      style={{
        background: "#ffffff",
        border: "1px solid #e2e8f0",
        borderRadius: 14,
        padding: "24px 28px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ color: statusColor, fontSize: 13, fontFamily: "'DM Mono', monospace", fontWeight: 600 }}>
          {statusLabel}
        </span>
        <span style={{ color: "#64748b", fontSize: 12, fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>
          {status.progress}%
        </span>
      </div>

      {/* Progress bar */}
      <ProgressBar
        pct={status.progress}
        color={isDone ? "#16a34a" : "#2563eb"}
        style={{ marginBottom: 18 }}
      />

      {/* Steps stepper */}
      <div style={{ display: "flex", gap: 0, marginBottom: 16 }}>
        {STEP_LABELS.map((label, i) => {
          const done = i < step_index || isDone;
          const active = i === step_index && !isDone;
          return (
            <div key={i} style={{ flex: 1, textAlign: "center" }}>
              <div
                style={{
                  width: 28, height: 28, borderRadius: "50%",
                  margin: "0 auto 6px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  background: done ? "#16a34a" : active ? "#3b82f6" : "#f1f5f9",
                  border: `2px solid ${done ? "#16a34a" : active ? "#2563eb" : "#e2e8f0"}`,
                  fontSize: 11,
                  color: done || active ? "#fff" : "#94a3b8",
                  transition: "all 0.3s",
                }}
              >
                {done ? "✓" : i + 1}
              </div>
              <div style={{ fontSize: 9, color: done ? "#16a34a" : active ? "#2563eb" : "#94a3b8", fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>
                {label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Message */}
      <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>
        {status.message}
      </div>

      {/* Done banner */}
      {isDone && status.created_cards > 0 && (
        <div
          style={{
            marginTop: 12, padding: "10px 14px",
            background: "#dcfce3",
            borderRadius: 8, border: "1px solid #bbf7d0",
            fontSize: 12, color: "#16a34a", fontFamily: "'DM Mono', monospace", fontWeight: 500,
          }}
        >
          🎉 Tạo được {status.created_cards} flashcard từ slide của bạn
        </div>
      )}
    </div>
  );
}
