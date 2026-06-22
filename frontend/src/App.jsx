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
    setActiveDeckId(deckId);
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "linear-gradient(rgba(248, 250, 252, 0.88), rgba(248, 250, 252, 0.88)), url('/bg-pattern.png') repeat", 
      backgroundSize: "400px", 
      backgroundPosition: "center",
      color: "#0f172a" 
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        body { margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        @keyframes modalPop {
          0% { opacity: 0; transform: scale(0.95) translateY(10px); }
          100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes overlayFade {
          0% { opacity: 0; backdrop-filter: blur(0px); }
          100% { opacity: 1; backdrop-filter: blur(4px); }
        }
      `}</style>

      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 50, background: "rgba(255,255,255,0.85)", backdropFilter: "blur(12px)", borderBottom: "1px solid #e2e8f0", padding: "0 24px", display: "flex", alignItems: "center", height: 56, boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
        <span
          onClick={() => nav("home")}
          style={{ fontFamily: "'DM Mono', monospace", fontWeight: 700, fontSize: 16, color: "#2563eb", cursor: "pointer", letterSpacing: 1 }}
        >
          SLIDE2FLASHCARD
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
                background: page === p ? "rgba(37,99,235,0.1)" : "transparent",
                color: page === p ? "#2563eb" : "#64748b",
                fontFamily: "'DM Mono', monospace", fontSize: 13, fontWeight: 500, cursor: "pointer", transition: "all 0.15s",
              }}
              onMouseEnter={(e) => { if (page !== p) e.target.style.background = "rgba(100,116,139,0.1)"; }}
              onMouseLeave={(e) => { if (page !== p) e.target.style.background = "transparent"; }}
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
        {page === "detail" && <DeckDetail deckId={activeDeckId} onStudy={(id) => nav("study", id)} onBack={() => nav("home")} onNavigate={nav} />}
        {page === "upload" && <Upload deckId={activeDeckId} onBack={() => nav("home")} />}
        {page === "stats"  && <Stats onBack={() => nav("home")} />}
      </main>
    </div>
  );
}
