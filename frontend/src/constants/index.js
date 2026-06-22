// constants/index.js — Shared theme constants, metadata, and labels

export const BACKEND_DOMAIN = "http://localhost:8000";

export const TYPE_META = {
  diagram: { label: "Diagram", color: "#2563eb", bg: "#dbeafe" },
  table:   { label: "Table",   color: "#ea580c", bg: "#ffedd5" },
};

export const RATING_META = {
  again:  { label: "Chưa biết",  color: "#dc2626", key: "1" },
  hard:   { label: "Khó",        color: "#ea580c", key: "2" },
  medium: { label: "Trung bình", color: "#ca8a04", key: "3" },
  easy:   { label: "Dễ",         color: "#16a34a", key: "4" },
};

export const STEP_LABELS = ["Lưu file", "Trích xuất ảnh", "Tạo nội dung", "Lưu Data"];

export const CARD_TYPES = ["diagram", "table"];
