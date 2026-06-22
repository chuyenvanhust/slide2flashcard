// hooks/useDeck.js — Fetch and cache deck data (deck info + all cards)

import { useState, useEffect } from "react";
import { api } from "../api/client";

export function useDeck(deckId) {
  const [deck, setDeck] = useState(null);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!deckId) return;
    setLoading(true);
    Promise.all([api.getDeck(deckId), api.getCards(deckId)]).then(([d, c]) => {
      setDeck(d);
      setCards(c);
      setLoading(false);
    });
  }, [deckId]);

  const updateDeckName = async (name) => {
    const updated = await api.updateDeck(deckId, name);
    setDeck(updated);
  };

  const removeCard = async (cardId) => {
    await api.deleteCard(cardId);
    setCards(c => c.filter(x => x.id !== cardId));
    setDeck(d => ({ ...d, total_cards: Math.max(0, d.total_cards - 1) }));
  };

  const editCard = async (cardId, backText) => {
    const updatedCard = await api.updateCard(cardId, backText);
    setCards(c => c.map(x => x.id === cardId ? updatedCard : x));
  };

  const transferCards = async (cardIds, targetDeckId, targetDeckName, action) => {
    await api.transferCards(cardIds, targetDeckId, targetDeckName, action);
    if (action === "move") {
      setCards(c => c.filter(x => !cardIds.includes(x.id)));
      setDeck(d => ({ ...d, total_cards: Math.max(0, d.total_cards - cardIds.length) }));
    }
  };

  return { deck, cards, loading, updateDeckName, removeCard, editCard, transferCards };
}

export function useDecks() {
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(true);

  const reload = () => {
    setLoading(true);
    api.getDecks().then((d) => {
      setDecks(d);
      setLoading(false);
    });
  };

  useEffect(() => {
    reload();
  }, []);

  const deleteDeck = async (id) => {
    await api.deleteDeck(id);
    setDecks((d) => d.filter((x) => x.id !== id));
  };

  const createDeck = async (name) => {
    const newDeck = await api.createDeck(name);
    setDecks([newDeck, ...decks]);
    return newDeck;
  };

  return { decks, loading, deleteDeck, createDeck, reload };
}
