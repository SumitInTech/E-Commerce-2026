"use client";

import Image from "next/image";
import { formatInr } from "../../lib/utils";

export default function CartDrawer({
  cart,
  isOpen,
  setIsOpen,
  onRemoveItem,
  onProceedCheckout,
}) {
  if (!isOpen) return null;

  const { items = [], subtotal = 0, tax = 0, shipping = 0, total = 0 } = cart;
  const freeShippingThreshold = 1499;
  const freeShippingPct = Math.min(100, Math.round((subtotal / freeShippingThreshold) * 100));
  const remainingForFree = Math.max(0, freeShippingThreshold - subtotal);

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/80 backdrop-blur-md animate-fade-in select-none">
      <div className="relative w-full max-w-md h-full bg-obsidian-950 border-l border-white/10 p-6 flex flex-col justify-between text-white shadow-2xl animate-slide-left">
        
        {/* Drawer Header */}
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <span className="text-lg">🛍️</span>
              <h3 className="text-base font-bold font-heading">Your Shopping Bag</h3>
              <span className="text-xs font-mono text-white/40">
                ({items.reduce((s, it) => s + it.quantity, 0)} items)
              </span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/60 hover:text-white text-xs font-mono"
            >
              ✕
            </button>
          </div>

          {/* Free Shipping Progress Meter */}
          <div className="mt-4 p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-white/70">
                {remainingForFree === 0
                  ? "🎉 You unlocked FREE Express Delivery!"
                  : `Add ${formatInr(remainingForFree)} more for FREE Express Delivery`}
              </span>
              <span className="font-mono font-bold text-cyber-cyan">{freeShippingPct}%</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyber-cyan to-emerald-400 transition-all duration-500 rounded-full"
                style={{ width: `${freeShippingPct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Cart Items List */}
        <div className="flex-grow overflow-y-auto py-6 space-y-4 scrollbar-none">
          {items.length === 0 ? (
            <div className="py-20 text-center text-white/40 space-y-3">
              <div className="text-4xl">🛒</div>
              <p className="text-sm font-bold text-white/70">Your shopping bag is empty</p>
              <p className="text-xs text-white/40 max-w-xs mx-auto">
                Explore our SS'26 puffers and use the 3D AI Fit Lab to pick your size.
              </p>
            </div>
          ) : (
            items.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-4 p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
              >
                <div className="relative w-16 h-16 rounded-xl overflow-hidden bg-obsidian-900 flex-shrink-0">
                  <Image
                    src={item.image_url || "/outfits/puffer_amber.jpg"}
                    alt={item.name}
                    fill
                    className="object-contain p-1"
                  />
                </div>
                <div className="flex-grow">
                  <h4 className="text-xs font-bold text-white line-clamp-1">{item.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/80">
                      Size {item.size_label}
                    </span>
                    <span className="text-[11px] font-mono text-white/40">
                      Qty: {item.quantity}
                    </span>
                  </div>
                  <div className="text-xs font-mono font-black text-white mt-1">
                    {formatInr(item.unit_price * item.quantity)}
                  </div>
                </div>
                <button
                  onClick={() => onRemoveItem(item.id)}
                  className="text-white/30 hover:text-red-400 transition-colors p-2 text-sm"
                  title="Remove item"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>

        {/* Drawer Footer & Checkout Summary */}
        {items.length > 0 && (
          <div className="pt-4 border-t border-white/10 space-y-3">
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between text-white/60">
                <span>SUBTOTAL:</span>
                <span>{formatInr(subtotal)}</span>
              </div>
              <div className="flex justify-between text-white/60">
                <span>ESTIMATED TAX (12%):</span>
                <span>{formatInr(tax)}</span>
              </div>
              <div className="flex justify-between text-white/60">
                <span>EXPRESS DELIVERY:</span>
                <span className={shipping === 0 ? "text-emerald-400 font-bold" : ""}>
                  {shipping === 0 ? "FREE" : formatInr(shipping)}
                </span>
              </div>
              <div className="flex justify-between text-sm font-bold text-white pt-2 border-t border-white/5">
                <span>TOTAL:</span>
                <span className="text-base text-cyber-cyan font-black">{formatInr(total)}</span>
              </div>
            </div>

            <button
              onClick={() => {
                setIsOpen(false);
                onProceedCheckout();
              }}
              className="w-full py-3.5 rounded-xl bg-white text-black font-black text-xs hover:bg-white/90 shadow-xl transition-all flex items-center justify-center gap-2 active:scale-98"
            >
              <span>PROCEED TO SECURE CHECKOUT</span>
              <span>→</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
