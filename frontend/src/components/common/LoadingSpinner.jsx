// components/common/LoadingSpinner.jsx — Centered loading state

export default function LoadingSpinner({ message = "Đang tải..." }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: 80,
        color: "#94a3b8",
        fontFamily: "'DM Mono', monospace",
        fontSize: 13,
      }}
    >
      {message}
    </div>
  );
}
