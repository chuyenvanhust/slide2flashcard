// pages/Upload.jsx — Upload PDF + pipeline progress display

import { useUpload } from "../hooks/useUpload";
import UploadZone from "../components/upload/UploadZone";
import ProcessingStatus from "../components/upload/ProcessingStatus";

const PIPELINE_INFO = [
  { icon: "🔍", label: "YOLOv8 Detect",    desc: "Phát hiện Diagram và Table trên từng trang slide" },
  { icon: "📝", label: "PyMuPDF Extract",  desc: "Trích xuất văn bản ngữ cảnh xung quanh hình ảnh" },
  { icon: "🧠", label: "Qwen2.5-VL",       desc: "AI phân tích hình ảnh và tạo nội dung Flashcard" },
];

export default function Upload({ deckId, onBack }) {
  const { upload, status, polling, isDone } = useUpload(deckId);

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <h2 style={{ margin: 0, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontSize: 18 }}>Upload Slide PDF</h2>
      </div>

      {!status ? (
        <>
          <UploadZone onUpload={upload} disabled={polling} />

          {/* Pipeline info */}
          <div style={{ marginTop: 20, background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 20px" }}>
            <div style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace", marginBottom: 10, fontWeight: 600 }}>
              Pipeline xử lý:
            </div>
            {PIPELINE_INFO.map(({ icon, label, desc }) => (
              <div key={label} style={{ display: "flex", gap: 10, marginBottom: 10, alignItems: "flex-start" }}>
                <span style={{ fontSize: 16 }}>{icon}</span>
                <div>
                  <span style={{ fontSize: 12, color: "#2563eb", fontFamily: "'DM Mono', monospace", fontWeight: 600 }}>{label} </span>
                  <span style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>{desc}</span>
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
              style={{ marginTop: 16, width: "100%", padding: "10px", borderRadius: 10, border: "none", background: "#2563eb", color: "#fff", fontFamily: "'DM Mono', monospace", fontSize: 13, cursor: "pointer", fontWeight: 600 }}
            >
              {deckId ? "Quay lại bộ bài →" : "Xem deck vừa tạo →"}
            </button>
          )}
        </>
      )}
    </div>
  );
}
