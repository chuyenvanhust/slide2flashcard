// components/deck/DeckList.jsx — Grid layout for deck cards

import DeckCard from "./DeckCard";

export default function DeckList({ decks, onStudy, onView, onDelete }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
        gap: 14,
      }}
    >
      {decks.map((deck) => (
        <DeckCard
          key={deck.id}
          deck={deck}
          onStudy={onStudy}
          onView={onView}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
