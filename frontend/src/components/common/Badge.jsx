// components/common/Badge.jsx — Card type label pill

import { TYPE_META } from "../../constants";

export default function Badge({ type }) {
  const m = TYPE_META[type] || TYPE_META.diagram;
  return (
    <span
      style={{
        padding: "2px 8px",
        borderRadius: 20,
        fontSize: 10,
        fontWeight: 700,
        background: m.bg,
        color: m.color,
        letterSpacing: 1,
        textTransform: "uppercase",
        fontFamily: "'DM Mono', monospace",
      }}
    >
      {m.label}
    </span>
  );
}
