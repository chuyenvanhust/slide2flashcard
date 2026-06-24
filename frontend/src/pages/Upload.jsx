// pages/Upload.jsx — Upload PDF + pipeline progress display

import { useUpload } from "../hooks/useUpload";
import UploadZone from "../components/upload/UploadZone";
import ProcessingStatus from "../components/upload/ProcessingStatus";

const PIPELINE_INFO = [
  { icon: "🔍", label: "YOLOv8",          desc: "Phát hiện diagram/chart/table/formula trong slide" },
  { icon: "📝", label: "PaddleOCR",        desc: "Trích xuất văn bản từ các trang slide" },
  { icon: "🔗", label: "CLIP fine-tuned",  desc: "Ghép ảnh với đoạn text giải thích liên quan" },
];

export default function Upload({ onBack }) {
  const { upload, status, polling, isDone } = useUpload();

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.5)", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <h2 style={{ margin: 0, color: "#e6edf3", fontFamily: "'DM Sans', sans-serif", fontSize: 18 }}>Upload Slide PDF</h2>
      </div>

      {!status ? (
        <>
          <UploadZone onUpload={upload} disabled={polling} />

          {/* Pipeline info */}
          <div style={{ marginTop: 20, background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "16px 20px" }}>
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", fontFamily: "monospace", marginBottom: 10, fontWeight: 600 }}>
              Pipeline xử lý:
            </div>
            {PIPELINE_INFO.map(({ icon, label, desc }) => (
              <div key={label} style={{ display: "flex", gap: 10, marginBottom: 10, alignItems: "flex-start" }}>
                <span style={{ fontSize: 16 }}>{icon}</span>
                <div>
                  <span style={{ fontSize: 11, color: "#58a6ff", fontFamily: "monospace", fontWeight: 600 }}>{label} </span>
                  <span style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", fontFamily: "monospace" }}>{desc}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <>
          <ProcessingStatus status={status} />
          {isDone && (
            <button
              onClick={onBack}
              style={{ marginTop: 16, width: "100%", padding: "10px", borderRadius: 10, border: "none", background: "#1f6feb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer" }}
            >
              Xem deck vừa tạo →
            </button>
          )}
        </>
      )}
    </div>
  );
}
