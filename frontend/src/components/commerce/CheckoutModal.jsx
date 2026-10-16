"use client";

import { useState } from "react";
import { formatInr } from "../../lib/utils";
import { api } from "../../lib/api";

export default function CheckoutModal({
  isOpen,
  onClose,
  cart,
  onOrderSuccess,
  showToast,
}) {
  const [formData, setFormData] = useState({
    name: "Aryan Sharma",
    email: "buyer@snitch.com",
    address: "402 Skylark Apts, Indiranagar, Bangalore, 560038",
    method: "UPI",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const orderPayload = {
        customer_name: formData.name,
        customer_email: formData.email,
        shipping_address: formData.address,
        payment_method: formData.method,
        cart_items: cart.items.map((it) => ({
          product_id: it.product_id,
          size_label: it.size_label,
          quantity: it.quantity,
        })),
        idempotency_key: `idem_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      };

      const order = await api.checkout(orderPayload);
      if (showToast) showToast("🎉 Order Confirmed! Payment Authenticated.");
      onOrderSuccess(order);
      onClose();
    } catch (err) {
      if (showToast) showToast(`Checkout Error: ${err.message}`, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-xl rounded-[32px] border border-white/15 bg-obsidian-950 p-6 md:p-10 text-white shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <div>
              <h3 className="text-base font-bold font-heading">Secure Idempotent Checkout</h3>
              <span className="text-[10px] font-mono text-emerald-400">
                100% ANTI-DUPLICATE PAYMENT ASSURANCE
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/60 hover:text-white text-xs font-mono"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-mono text-white/60 block mb-1">CUSTOMER FULL NAME</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-cyan"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-white/60 block mb-1">EMAIL ADDRESS FOR DISPATCH NOTICES</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-cyan"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-white/60 block mb-1">SHIPPING DESTINATION</label>
            <textarea
              rows="2"
              required
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-cyan resize-none"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-white/60 block mb-2">PAYMENT PROTOCOL</label>
            <div className="grid grid-cols-3 gap-2">
              {["UPI", "CARD", "COD"].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setFormData({ ...formData, method: m })}
                  className={`py-2.5 rounded-xl text-xs font-bold font-mono border transition-all ${
                    formData.method === m
                      ? "bg-white text-black border-white shadow-md"
                      : "bg-white/5 border-white/10 text-white/60 hover:text-white"
                  }`}
                >
                  {m === "UPI" ? "⚡ Instant UPI" : m === "CARD" ? "💳 Card Gateway" : "💵 COD"}
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-white/5 border border-white/10 flex justify-between items-center text-xs font-mono mt-4">
            <span className="text-white/60">PAYABLE AMOUNT:</span>
            <span className="text-base font-black text-cyber-cyan font-mono">
              {formatInr(cart.total || 3499)}
            </span>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-400 to-teal-400 text-black font-black text-xs hover:opacity-95 shadow-xl transition-all flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
          >
            {isSubmitting ? (
              <span>Authenticating Cryptographic Key...</span>
            ) : (
              <span>PAY & CONFIRM ORDER ({formData.method}) →</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
