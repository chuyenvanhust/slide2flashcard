// components/common/ProgressBar.jsx — Reusable progress bar

export default function ProgressBar({ pct = 0, color = "#58a6ff", height = 6, style = {} }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.06)",
        borderRadius: height,
        height,
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        style={{
          height: "100%",
          borderRadius: height,
          width: `${pct}%`,
          background: color,
          transition: "width 0.5s ease",
        }}
      />
    </div>
  );
}
