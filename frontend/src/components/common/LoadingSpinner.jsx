// components/common/LoadingSpinner.jsx — Centered loading state

export default function LoadingSpinner({ message = "Đang tải..." }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: 80,
        color: "rgba(255,255,255,0.3)",
        fontFamily: "monospace",
      }}
    >
      {message}
    </div>
  );
}
