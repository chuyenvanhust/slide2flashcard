// App.jsx — App shell: nav + page routing

import { useState } from "react";
import Home from "./pages/Home";
import StudySession from "./pages/StudySession";
import DeckDetail from "./pages/DeckDetail";
import Upload from "./pages/Upload";
import Stats from "./pages/Stats";

export default function App() {
  const [page, setPage] = useState("home");
  const [activeDeckId, setActiveDeckId] = useState(null);

  const nav = (p, deckId = null) => {
    setPage(p);
    if (deckId) setActiveDeckId(deckId);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#010409", color: "#e6edf3" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        body { margin: 0; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
      `}</style>

      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 50, background: "rgba(1,4,9,0.85)", backdropFilter: "blur(12px)", borderBottom: "1px solid rgba(255,255,255,0.06)", padding: "0 24px", display: "flex", alignItems: "center", height: 52 }}>
        <span
          onClick={() => nav("home")}
          style={{ fontFamily: "'DM Mono', monospace", fontWeight: 700, fontSize: 15, color: "#58a6ff", cursor: "pointer", letterSpacing: 1 }}
        >
          SLIDE2FLASH
        </span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 4 }}>
          {[
            ["home",   "Decks"],
            ["upload", "Upload"],
            ["stats",  "Stats"],
          ].map(([p, label]) => (
            <button
              key={p}
              onClick={() => nav(p)}
              style={{
                padding: "6px 14px", borderRadius: 8, border: "none",
                background: page === p ? "rgba(88,166,255,0.15)" : "transparent",
                color: page === p ? "#58a6ff" : "rgba(255,255,255,0.45)",
                fontFamily: "'DM Mono', monospace", fontSize: 12, cursor: "pointer", transition: "all 0.15s",
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main style={{ maxWidth: 900, margin: "0 auto", padding: "28px 20px" }}>
        {page === "home"   && <Home onStudy={(id) => nav("study", id)} onView={(id) => nav("detail", id)} onNavigate={nav} />}
        {page === "study"  && <StudySession deckId={activeDeckId} onBack={() => nav("home")} />}
        {page === "detail" && <DeckDetail deckId={activeDeckId} onStudy={(id) => nav("study", id)} onBack={() => nav("home")} />}
        {page === "upload" && <Upload onBack={() => nav("home")} />}
        {page === "stats"  && <Stats onBack={() => nav("home")} />}
      </main>
    </div>
  );
}
