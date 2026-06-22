import { useState, useEffect } from "react";
import { api } from "../api/client";
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { TYPE_META } from "../constants";

export default function Stats({ onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats().then(d => {
      setData(d);
      setLoading(false);
    }).catch(e => {
      console.error(e);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner message="Đang tải dữ liệu thống kê..." />;
  if (!data) return <div style={{textAlign: "center", marginTop: 50, color: "#64748b", fontFamily: "'DM Mono', monospace"}}>Lỗi tải dữ liệu</div>;

  const retentionData = [
    { name: "Đã thuộc", value: data.retention_rate, color: "#16a34a" },
    { name: "Quên", value: 100 - data.retention_rate, color: "#e2e8f0" }
  ];

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", paddingBottom: 40 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <button onClick={onBack} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 18, padding: 0 }}>←</button>
        <h2 style={{ margin: 0, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontSize: 20 }}>Tiến độ học tập</h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        
        {/* Reviews theo ngày */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: 15, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, marginBottom: 16 }}>Reviews 14 ngày qua</div>
          <div style={{ height: 200 }}>
            {data.reviews_by_date.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.reviews_by_date}>
                  <XAxis dataKey="date" tick={{fontSize: 10, fill: "#94a3b8"}} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{fill: "#f8fafc"}} contentStyle={{borderRadius: 8, border: "none", boxShadow: "0 4px 6px rgba(0,0,0,0.1)", fontSize: 12, fontFamily: "'DM Mono', monospace"}} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
               <div style={{color: "#94a3b8", fontSize: 12, textAlign: "center", marginTop: 80, fontFamily: "'DM Mono', monospace"}}>Chưa có dữ liệu học</div>
            )}
          </div>
        </div>

        {/* Retention */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 15, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, marginBottom: 16 }}>Tỉ lệ nhớ bài (Retention)</div>
          <div style={{ flex: 1, position: "relative", display: "flex", justifyContent: "center" }}>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={retentionData} innerRadius={60} outerRadius={80} dataKey="value" startAngle={90} endAngle={-270} stroke="none">
                  {retentionData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column"}}>
               <div style={{fontSize: 28, fontWeight: 700, color: "#0f172a", fontFamily: "'DM Mono', monospace"}}>{data.retention_rate}%</div>
            </div>
          </div>
        </div>

        {/* Card types */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: 15, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, marginBottom: 16 }}>Phân loại Flashcard</div>
          <div style={{ height: 200, display: "flex", alignItems: "center" }}>
             {data.type_breakdown.length > 0 ? (
               <>
                 <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie data={data.type_breakdown} innerRadius={40} outerRadius={70} dataKey="count" nameKey="type" stroke="none">
                        {data.type_breakdown.map((e, i) => <Cell key={i} fill={TYPE_META[e.type]?.color || "#cbd5e1"} />)}
                      </Pie>
                    </PieChart>
                 </ResponsiveContainer>
                 <div style={{ flex: 1, paddingLeft: 20 }}>
                   {data.type_breakdown.map(e => (
                     <div key={e.type} style={{display: "flex", alignItems: "center", gap: 8, marginBottom: 10}}>
                       <div style={{width: 12, height: 12, borderRadius: 3, background: TYPE_META[e.type]?.color || "#cbd5e1"}} />
                       <span style={{fontSize: 13, color: "#64748b", fontFamily: "'DM Mono', monospace", textTransform: "capitalize"}}>{TYPE_META[e.type]?.label || e.type}: </span>
                       <strong style={{fontSize: 13, color: "#0f172a", fontFamily: "'DM Mono', monospace"}}>{e.count}</strong>
                     </div>
                   ))}
                 </div>
               </>
             ) : (
                <div style={{color: "#94a3b8", fontSize: 12, textAlign: "center", width: "100%", fontFamily: "'DM Mono', monospace"}}>Chưa có thẻ nào</div>
             )}
          </div>
        </div>

        {/* Deck Progress */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", overflowY: "auto", maxHeight: 280 }}>
          <div style={{ fontSize: 15, color: "#0f172a", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, marginBottom: 16 }}>Tiến độ từng Deck</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {data.deck_progress.length > 0 ? data.deck_progress.map(d => {
              const pct = d.total > 0 ? Math.round((d.known / d.total) * 100) : 0;
              return (
                <div key={d.name}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 12, fontFamily: "'DM Mono', monospace" }}>
                    <span style={{ color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 200 }} title={d.name}>{d.name}</span>
                    <span style={{ color: "#0f172a", fontWeight: 600 }}>{pct}%</span>
                  </div>
                  <div style={{ background: "#e2e8f0", borderRadius: 4, height: 6, overflow: "hidden" }}>
                    <div style={{ background: pct === 100 ? "#16a34a" : "#2563eb", height: "100%", width: `${pct}%`, borderRadius: 4 }} />
                  </div>
                </div>
              );
            }) : (
               <div style={{color: "#94a3b8", fontSize: 12, textAlign: "center", marginTop: 40, fontFamily: "'DM Mono', monospace"}}>Chưa có Deck nào</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
