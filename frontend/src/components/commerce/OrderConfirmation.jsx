"use client";

import { formatInr } from "../../lib/utils";

export default function OrderConfirmation({ order, onClose }) {
  if (!order) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-lg rounded-[32px] border border-emerald-500/40 bg-obsidian-950 p-6 md:p-10 text-white shadow-[0_0_80px_rgba(16,185,129,0.2)] text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-3xl mx-auto text-emerald-400">
          ✓
        </div>

        <div>
          <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest block">
            PAYMENT SETTLED & VERIFIED
          </span>
          <h3 className="text-2xl font-black font-heading mt-1">
            Order Successfully Placed!
          </h3>
          <p className="text-xs text-white/50 mt-1">
            Thank you, <strong className="text-white">{order.customer_name}</strong>. Your runway package is being dispatched via Express Air.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 text-xs font-mono space-y-2 text-left">
          <div className="flex justify-between">
            <span className="text-white/40">ORDER REFERENCE:</span>
            <span className="text-white font-bold">{order.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-white/40">TRACKING NUMBER:</span>
            <span className="text-cyber-cyan font-bold">{order.tracking_number}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-white/40">TOTAL PAID:</span>
            <span className="text-emerald-400 font-bold">{formatInr(order.total_amount || 3499)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-white/40">ESTIMATED DISPATCH:</span>
            <span className="text-white font-bold">Today, Within 4 Hours</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-3.5 rounded-xl bg-white text-black font-bold text-xs hover:bg-white/90 shadow-xl transition-all"
        >
          Return to Atelier Runway
        </button>
      </div>
    </div>
  );
}
