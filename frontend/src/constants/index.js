// constants/index.js — Shared theme constants, metadata, and labels

export const TYPE_META = {
  diagram: { label: "Diagram", color: "#58a6ff", bg: "rgba(88,166,255,0.12)" },
  chart:   { label: "Chart",   color: "#3fb950", bg: "rgba(63,185,80,0.12)" },
  table:   { label: "Table",   color: "#f78166", bg: "rgba(247,129,102,0.12)" },
  formula: { label: "Formula", color: "#d2a8ff", bg: "rgba(210,168,255,0.12)" },
};

export const RATING_META = {
  again:  { label: "Chưa biết",  color: "#f85149", key: "1" },
  hard:   { label: "Khó",        color: "#f78166", key: "2" },
  medium: { label: "Trung bình", color: "#e3b341", key: "3" },
  easy:   { label: "Dễ",         color: "#3fb950", key: "4" },
};

export const STEP_LABELS = ["Trích xuất", "Phát hiện", "OCR", "CLIP Match", "Tạo card"];

export const CARD_TYPES = ["diagram", "chart", "table", "formula"];
