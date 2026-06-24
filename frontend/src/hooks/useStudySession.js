// hooks/useStudySession.js — Study session logic: fetch due cards, flip, rate, advance

import { useState, useEffect, useCallback } from "react";
import { api } from "../api/client";

export function useStudySession(deckId) {
  const [cards, setCards] = useState([]);
  const [idx, setIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [done, setDone] = useState(false);
  const [stats, setStats] = useState({ easy: 0, medium: 0, hard: 0, again: 0 });

  useEffect(() => {
    api.getDueCards(deckId).then((c) => {
      setCards(c);
      setLoading(false);
      setDone(c.length === 0);
    });
  }, [deckId]);

  const flip = useCallback(() => setFlipped((f) => !f), []);

  const rate = useCallback(
    async (rating) => {
      const card = cards[idx];
      await api.submitReview(card.id, rating);
      setStats((s) => ({ ...s, [rating]: s[rating] + 1 }));
      const next = idx + 1;
      if (next >= cards.length) {
        setDone(true);
      } else {
        setIdx(next);
        setFlipped(false);
      }
    },
    [cards, idx]
  );

  const currentCard = cards[idx];
  const progress = cards.length > 0 ? Math.round((idx / cards.length) * 100) : 0;
  const totalReviewed = Object.values(stats).reduce((a, b) => a + b, 0);

  return {
    cards,
    currentCard,
    idx,
    flipped,
    loading,
    done,
    stats,
    progress,
    totalReviewed,
    flip,
    rate,
  };
}
