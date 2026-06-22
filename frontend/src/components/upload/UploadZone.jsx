// components/upload/UploadZone.jsx — Drag & drop PDF upload area

import { useState, useRef } from "react";

export default function UploadZone({ onUpload, disabled }) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef();

  const handle = (file) => {
    if (file && file.name.endsWith(".pdf")) onUpload(file);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files[0]); }}
      onClick={() => !disabled && inputRef.current.click()}
      style={{
        border: `2px dashed ${drag ? "#2563eb" : "#cbd5e1"}`,
        borderRadius: 16,
        padding: "52px 32px",
        textAlign: "center",
        cursor: disabled ? "not-allowed" : "pointer",
        background: drag ? "#eff6ff" : "#ffffff",
        transition: "all 0.2s",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        hidden
        onChange={(e) => handle(e.target.files[0])}
      />
      <div style={{ fontSize: 40, marginBottom: 16 }}>📄</div>
      <div
        style={{
          color: "#0f172a",
          fontSize: 16,
          fontWeight: 600,
          marginBottom: 8,
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        {drag ? "Thả file vào đây" : "Kéo thả hoặc click để chọn PDF"}
      </div>
      <div style={{ color: "#64748b", fontSize: 12, fontFamily: "'DM Mono', monospace" }}>
        Slide bài giảng dạng PDF · tối đa 50MB
      </div>
    </div>
  );
}
