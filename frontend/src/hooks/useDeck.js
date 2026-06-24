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

  return { deck, cards, loading };
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

  return { decks, loading, deleteDeck, reload };
}
