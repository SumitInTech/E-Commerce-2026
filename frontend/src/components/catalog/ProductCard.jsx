"use client";

import { useState } from "react";
import Image from "next/image";
import { useCardTilt } from "../../hooks/useCardTilt";
import { formatInr } from "../../lib/utils";

export default function ProductCard({
  product,
  onAddToCart,
  onOpenAiFit,
  aiRecommendedSize,
}) {
  const { handleMouseMove, handleMouseLeave } = useCardTilt(6);
  const [selectedSize, setSelectedSize] = useState(
    aiRecommendedSize || product.sizes[0] || "38"
  );

  return (
    <div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="group relative rounded-2xl border border-white/10 bg-obsidian-900/80 p-4 transition-all duration-300 hover:border-cyber-cyan/40 hover:shadow-[0_15px_40px_rgba(0,0,0,0.7)] flex flex-col justify-between overflow-hidden cursor-pointer"
    >
      {/* Hologram Light Reflection Sheen */}
      <div className="hologram-sheen absolute inset-0 pointer-events-none opacity-0 transition-opacity duration-300 rounded-2xl z-10" />

      {/* Top Badges */}
      <div className="flex items-center justify-between z-20 mb-3">
        <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/70">
          {product.garment_type.toUpperCase()}
        </span>
        {product.discount_pct && (
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
            {product.discount_pct}% OFF
          </span>
        )}
      </div>

      {/* Image Showcase */}
      <div className="relative w-full h-64 rounded-xl overflow-hidden bg-obsidian-950/60 mb-4 flex items-center justify-center">
        <Image
          src={product.image}
          alt={product.name}
          fill
          className="object-contain p-2 group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950/80 via-transparent to-transparent opacity-60" />

        {/* Quick AI Fit Trigger Pill */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onOpenAiFit(product.id);
          }}
          className="absolute bottom-2.5 right-2.5 z-20 px-3 py-1 rounded-full bg-black/70 hover:bg-black border border-cyber-cyan/40 text-cyber-cyan text-[11px] font-semibold backdrop-blur-md transition-all flex items-center gap-1 shadow-lg"
        >
          <span>✨ AI Fit</span>
        </button>
      </div>

      {/* Product Details */}
      <div className="space-y-2 z-20 flex-grow">
        <h3 className="text-sm font-bold text-white group-hover:text-cyber-cyan transition-colors leading-snug">
          {product.name}
        </h3>
        <p className="text-xs text-white/50 line-clamp-2">
          {product.description || product.tagline}
        </p>

        {/* Pricing */}
        <div className="flex items-baseline gap-2 pt-1">
          <span className="text-base font-black text-white font-mono">
            {formatInr(product.price)}
          </span>
          {product.original_price && (
            <span className="text-xs text-white/40 line-through font-mono">
              {formatInr(product.original_price)}
            </span>
          )}
        </div>
      </div>

      {/* Size Selector & Add to Bag */}
      <div className="pt-4 border-t border-white/5 mt-3 space-y-3 z-20">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {product.sizes.map((s) => {
            const isSelected = selectedSize === s;
            const isAiRec = aiRecommendedSize === s;

            return (
              <button
                key={s}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedSize(s);
                }}
                className={`relative px-2.5 py-1 rounded text-[11px] font-bold font-mono transition-all ${
                  isSelected
                    ? "bg-white text-black shadow-md"
                    : "bg-white/5 text-white/60 hover:text-white border border-white/10"
                }`}
              >
                <span>{s}</span>
                {isAiRec && !isSelected && (
                  <span className="absolute -top-1 -right-0.5 w-2 h-2 rounded-full bg-cyber-cyan" />
                )}
              </button>
            );
          })}
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart(product, selectedSize);
          }}
          className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white text-white hover:text-black font-bold text-xs transition-all duration-200 border border-white/15 flex items-center justify-center gap-1.5 active:scale-98"
        >
          <span>Add to Bag</span>
          <span className="text-xs">→</span>
        </button>
      </div>
    </div>
  );
}
