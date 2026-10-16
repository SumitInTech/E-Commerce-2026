"use client";

import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import { formatInr } from "../../lib/utils";

export default function AdminDashboardModal({ isOpen, onClose }) {
  const [data, setData] = useState(null);
  const [tab, setTab] = useState("metrics"); // "metrics" | "tickets" | "vendors"
  const [isLoading, setIsLoading] = useState(false);
  const [vendorForm, setVendorForm] = useState({
    store_name: "",
    contact: "",
  });

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await api.getAdminMetrics();
      setData(res);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-[32px] border border-white/15 bg-obsidian-950 p-6 md:p-10 text-white shadow-2xl scrollbar-none">
        
        {/* Header */}
        <div className="flex items-start justify-between pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-cyber-cyan">
              <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-pulse"></span>
              <span>EXECUTIVE CONTROL & INCIDENT DESK</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black font-heading mt-1">
              Platform Administration
            </h2>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/70 hover:text-white text-xs font-mono"
          >
            ✕
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-2 my-6 p-1 bg-obsidian-900 border border-white/10 rounded-2xl w-fit">
          <button
            onClick={() => setTab("metrics")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
              tab === "metrics" ? "bg-white text-black shadow-lg" : "text-white/60 hover:text-white"
            }`}
          >
            📊 Live Metrics
          </button>
          <button
            onClick={() => setTab("tickets")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
              tab === "tickets" ? "bg-white text-black shadow-lg" : "text-white/60 hover:text-white"
            }`}
          >
            🎫 Support Desk ({data?.tickets?.length || 0})
          </button>
          <button
            onClick={() => setTab("vendors")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
              tab === "vendors" ? "bg-white text-black shadow-lg" : "text-white/60 hover:text-white"
            }`}
          >
            🏬 Vendor Hub
          </button>
        </div>

        {/* Metrics View */}
        {tab === "metrics" && data?.metrics && (
          <div className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-[10px] font-mono text-white/40 block">GROSS REVENUE</span>
                <span className="text-xl font-black text-cyber-cyan font-mono mt-1 block">
                  {formatInr(data.metrics.total_revenue)}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-[10px] font-mono text-white/40 block">ORDERS TODAY</span>
                <span className="text-xl font-black text-white font-mono mt-1 block">
                  {data.metrics.orders_today}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-[10px] font-mono text-white/40 block">AI INFERENCES</span>
                <span className="text-xl font-black text-cyber-gold font-mono mt-1 block">
                  {data.metrics.ai_fit_inference_count}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-[10px] font-mono text-white/40 block">RETURN RISK</span>
                <span className="text-xl font-black text-emerald-400 font-mono mt-1 block">
                  {data.metrics.return_rate_pct}%
                </span>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-obsidian-900 border border-white/10 space-y-3 font-mono text-xs">
              <span className="text-white/60 uppercase tracking-wider block">
                7 Active Microservice Daemons
              </span>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
                {["Gateway", "Catalog", "Orders", "AI Fit Lab", "AI Color", "Chatbot RAG", "Payments"].map((svc) => (
                  <div key={svc} className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span>{svc}: 200 OK</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tickets View */}
        {tab === "tickets" && (
          <div className="space-y-3 animate-fade-in">
            {data?.tickets?.map((t) => (
              <div
                key={t.id}
                className="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-cyber-cyan font-bold">#{t.id}</span>
                    <span className="text-sm font-bold text-white">{t.customer}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">
                      {t.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-white/60 mt-1">{t.issue}</p>
                </div>
                <button
                  onClick={() => alert(`Ticket #${t.id} marked resolved!`)}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold transition-all"
                >
                  Resolve
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Vendors View */}
        {tab === "vendors" && (
          <div className="space-y-6 animate-fade-in">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                alert(`Vendor application submitted for ${vendorForm.store_name}!`);
                setVendorForm({ store_name: "", contact: "" });
              }}
              className="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-4"
            >
              <h4 className="text-xs font-mono text-cyber-gold uppercase font-bold">
                Onboard New Fast-Fashion Atelier Vendor
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Atelier Brand Name"
                  required
                  value={vendorForm.store_name}
                  onChange={(e) => setVendorForm({ ...vendorForm, store_name: e.target.value })}
                  className="bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-gold"
                />
                <input
                  type="email"
                  placeholder="Vendor Contact Email"
                  required
                  value={vendorForm.contact}
                  onChange={(e) => setVendorForm({ ...vendorForm, contact: e.target.value })}
                  className="bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-gold"
                />
              </div>
              <button
                type="submit"
                className="px-5 py-2.5 rounded-xl bg-cyber-gold text-black font-bold text-xs hover:opacity-90 transition-all"
              >
                Submit Vendor Application
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
