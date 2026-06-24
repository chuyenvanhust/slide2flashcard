// store/deckStore.js — Zustand store: decks list + current deck
// Install: npm install zustand

import { create } from "zustand";
import { api } from "../api/client";

export const useDeckStore = create((set, get) => ({
  decks: [],
  currentDeckId: null,
  loading: false,

  fetchDecks: async () => {
    set({ loading: true });
    const decks = await api.getDecks();
    set({ decks, loading: false });
  },

  setCurrentDeck: (id) => set({ currentDeckId: id }),

  deleteDeck: async (id) => {
    await api.deleteDeck(id);
    set((state) => ({ decks: state.decks.filter((d) => d.id !== id) }));
  },

  getCurrentDeck: () => {
    const { decks, currentDeckId } = get();
    return decks.find((d) => d.id === currentDeckId) || null;
  },
}));
