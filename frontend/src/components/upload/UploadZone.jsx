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
        border: `2px dashed ${drag ? "#58a6ff" : "rgba(255,255,255,0.12)"}`,
        borderRadius: 16,
        padding: "52px 32px",
        textAlign: "center",
        cursor: disabled ? "not-allowed" : "pointer",
        background: drag ? "rgba(88,166,255,0.05)" : "rgba(255,255,255,0.02)",
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
          color: "#e6edf3",
          fontSize: 16,
          fontWeight: 600,
          marginBottom: 8,
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        {drag ? "Thả file vào đây" : "Kéo thả hoặc click để chọn PDF"}
      </div>
      <div style={{ color: "rgba(255,255,255,0.35)", fontSize: 12, fontFamily: "monospace" }}>
        Slide bài giảng dạng PDF · tối đa 50MB
      </div>
    </div>
  );
}
