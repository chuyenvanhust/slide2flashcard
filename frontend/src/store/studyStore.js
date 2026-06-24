// store/studyStore.js — Zustand store: study session state, current card, flip
// Install: npm install zustand

import { create } from "zustand";

export const useStudyStore = create((set, get) => ({
  sessionCards: [],
  currentIndex: 0,
  isFlipped: false,
  sessionStats: { easy: 0, medium: 0, hard: 0, again: 0 },
  sessionDone: false,

  initSession: (cards) =>
    set({
      sessionCards: cards,
      currentIndex: 0,
      isFlipped: false,
      sessionStats: { easy: 0, medium: 0, hard: 0, again: 0 },
      sessionDone: cards.length === 0,
    }),

  flipCard: () => set((state) => ({ isFlipped: !state.isFlipped })),

  recordRating: (rating) => {
    const { sessionCards, currentIndex, sessionStats } = get();
    const next = currentIndex + 1;
    set({
      sessionStats: { ...sessionStats, [rating]: sessionStats[rating] + 1 },
      currentIndex: next,
      isFlipped: false,
      sessionDone: next >= sessionCards.length,
    });
  },

  getCurrentCard: () => {
    const { sessionCards, currentIndex } = get();
    return sessionCards[currentIndex] || null;
  },

  getProgress: () => {
    const { sessionCards, currentIndex } = get();
    return sessionCards.length > 0
      ? Math.round((currentIndex / sessionCards.length) * 100)
      : 0;
  },
}));
