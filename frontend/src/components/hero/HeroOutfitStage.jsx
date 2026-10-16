"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { OUTFIT_LOOKS } from "../../lib/outfitData";
import { formatUsd, formatInr } from "../../lib/utils";

export default function HeroOutfitStage({
  activeLookIndex = 0,
  onSelectLookIndex,
  onAddToCart,
  onOpenAiFit,
  onOpenAiColor,
  onOpenChat,
  selectedSize,
  setSelectedSize,
  aiRecommendedSize,
  userSkinToneResult,
}) {
  const [currentIndex, setCurrentIndex] = useState(activeLookIndex);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState("next"); // "next" | "prev"
  const [currencyMode, setCurrencyMode] = useState("USD"); // "USD" | "INR"

  // Sync external index changes (e.g., from Skin Tone Harmonizer)
  useEffect(() => {
    if (activeLookIndex !== currentIndex && activeLookIndex >= 0 && activeLookIndex < OUTFIT_LOOKS.length) {
      triggerTransition(activeLookIndex, activeLookIndex > currentIndex ? "next" : "prev");
    }
  }, [activeLookIndex]);

  const currentLook = OUTFIT_LOOKS[currentIndex];
  const totalLooks = OUTFIT_LOOKS.length;

  // Previous and Next indices for dual-thumbnail navigation
  const prevIndex = (currentIndex - 1 + totalLooks) % totalLooks;
  const nextIndex = (currentIndex + 1) % totalLooks;
  const prevLook = OUTFIT_LOOKS[prevIndex];
  const nextLook = OUTFIT_LOOKS[nextIndex];

  // Active Size handling
  const activeSize = selectedSize || aiRecommendedSize || currentLook.sizes[1].label;

  const triggerTransition = (targetIndex, direction = "next") => {
    if (isTransitioning || targetIndex === currentIndex) return;
    setTransitionDirection(direction);
    setIsTransitioning(true);

    // Switch data midway through animation
    setTimeout(() => {
      setCurrentIndex(targetIndex);
      if (onSelectLookIndex) onSelectLookIndex(targetIndex);
    }, 280);

    // Reset transition lock
    setTimeout(() => {
      setIsTransitioning(false);
    }, 600);
  };

  const handleNext = () => triggerTransition(nextIndex, "next");
  const handlePrev = () => triggerTransition(prevIndex, "prev");

  return (
    <section className="relative w-full min-h-[92vh] flex items-center justify-center py-10 px-4 md:px-8 overflow-hidden select-none">
      {/* ------------------------------------------------------------------- */}
      {/* 1. Dynamic Ambient Radiant Gradient Backdrop (Matches Video)        */}
      {/* ------------------------------------------------------------------- */}
      <div
        className="absolute inset-0 transition-all duration-1000 ease-out pointer-events-none"
        style={{
          background: currentLook.ambientGradient,
          opacity: 0.95,
        }}
      />

      {/* Cyber Grid Lines Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.06)_1px,transparent_1px)] bg-[size:32px_32px] opacity-40 pointer-events-none" />

      {/* ------------------------------------------------------------------- */}
      {/* 2. Floating Rounded Luxury Viewport Canvas (The Video UI Frame)     */}
      {/* ------------------------------------------------------------------- */}
      <div className="relative w-full max-w-6xl rounded-[32px] border border-white/15 bg-obsidian-950/75 backdrop-blur-3xl shadow-[0_30px_100px_rgba(0,0,0,0.85)] p-6 md:p-12 overflow-hidden z-10 transition-all duration-500">
        
        {/* Dynamic Edge Aura Glow */}
        <div
          className="absolute -top-32 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full blur-[100px] pointer-events-none transition-all duration-1000"
          style={{ background: currentLook.cardGlow }}
        />

        {/* ----------------------------------------------------------------- */}
        {/* Top Floating Pill Menu Bar (Jacket Masters / Snitch Luxe)          */}
        {/* ----------------------------------------------------------------- */}
        <div className="flex items-center justify-between pb-8 border-b border-white/10 relative z-20">
          {/* Brand Mark on Left */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 flex items-center justify-center font-black text-xs text-white tracking-widest">
              JM
            </div>
            <span className="text-xs font-bold tracking-[0.2em] text-white/90 uppercase font-mono">
              JACKET MASTERS
            </span>
          </div>

          {/* Center Frosted Glass Pill Tabs (From Video) */}
          <nav className="hidden md:flex items-center bg-black/40 border border-white/10 rounded-full p-1.5 backdrop-blur-xl">
            <button className="px-5 py-2 rounded-full text-xs font-bold bg-white text-black shadow-lg transition-all">
              PUFFER JACKET
            </button>
            <a
              href="#catalog"
              className="px-5 py-2 rounded-full text-xs font-medium text-white/70 hover:text-white transition-colors"
            >
              ALL PRODUCTS
            </a>
            <button
              onClick={onOpenAiFit}
              className="px-5 py-2 rounded-full text-xs font-medium text-cyber-cyan hover:text-white transition-colors flex items-center gap-1.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyber-cyan animate-pulse"></span>
              AI FIT LAB
            </button>
            <button
              onClick={onOpenAiColor}
              className="px-5 py-2 rounded-full text-xs font-medium text-cyber-gold hover:text-white transition-colors"
            >
              COLOR HARMONY
            </button>
            <button
              onClick={onOpenChat}
              className="px-5 py-2 rounded-full text-xs font-medium text-white/70 hover:text-white transition-colors"
            >
              CONTACT
            </button>
          </nav>

          {/* Currency Toggle & Quick Status */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrencyMode(currencyMode === "USD" ? "INR" : "USD")}
              className="px-3 py-1 rounded-full text-[11px] font-mono font-bold bg-white/5 border border-white/10 text-white/80 hover:border-white/30 transition-all"
              title="Toggle Currency Display"
            >
              {currencyMode === "USD" ? "$ USD" : "₹ INR"}
            </button>
            <button
              onClick={onOpenChat}
              className="p-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/80 transition-all"
              title="AI Stylist Chatbot"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </button>
          </div>
        </div>

        {/* ----------------------------------------------------------------- */}
        {/* Main 3-Column Interactive Layout                                  */}
        {/* ----------------------------------------------------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center pt-8 md:pt-12 min-h-[520px] relative z-20">
          
          {/* Column 1 (Left): Controls, Headline, Description & CTAs (Span 4) */}
          <div className="lg:col-span-4 flex flex-col justify-between h-full space-y-6">
            <div>
              {/* Navigation Chevron Buttons (< >) */}
              <div className="flex items-center gap-2 mb-6">
                <button
                  onClick={handlePrev}
                  className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/80 hover:text-white transition-all active:scale-95"
                  aria-label="Previous Outfit"
                >
                  ‹
                </button>
                <button
                  onClick={handleNext}
                  className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/80 hover:text-white transition-all active:scale-95"
                  aria-label="Next Outfit"
                >
                  ›
                </button>
                <span className="text-[11px] font-mono text-white/40 ml-2">
                  0{currentIndex + 1} / 0{totalLooks}
                </span>
              </div>

              {/* Bold Headline (Animated on change) */}
              <div
                className={`transition-all duration-400 transform ${
                  isTransitioning
                    ? transitionDirection === "next"
                      ? "-translate-y-3 opacity-0"
                      : "translate-y-3 opacity-0"
                    : "translate-y-0 opacity-100"
                }`}
              >
                <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-[1.08] font-heading">
                  {currentLook.titleLine1}
                  <br />
                  <span className="text-white/85 font-extrabold">
                    {currentLook.titleLine2}
                  </span>
                </h1>

                {/* Subtitle Paragraph */}
                <p className="mt-4 text-xs md:text-sm text-white/60 leading-relaxed font-body max-w-sm">
                  {currentLook.description}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex flex-wrap items-center gap-3">
                <button
                  onClick={() =>
                    onAddToCart(
                      {
                        id: currentLook.id,
                        name: `${currentLook.colorName} Puffer`,
                        price: currencyMode === "USD" ? currentLook.price : currentLook.priceInr,
                        image: currentLook.image,
                      },
                      activeSize
                    )
                  }
                  className="px-6 py-3 rounded-full bg-white text-black font-bold text-xs hover:bg-white/90 hover:shadow-[0_0_25px_rgba(255,255,255,0.4)] transition-all flex items-center gap-2 group active:scale-95"
                >
                  <span>Get the look</span>
                  <span className="group-hover:translate-x-0.5 transition-transform">›</span>
                </button>

                <button
                  onClick={onOpenAiFit}
                  className="px-5 py-3 rounded-full bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/40 text-cyber-cyan font-semibold text-xs transition-all flex items-center gap-1.5"
                >
                  <span>✨ 3D AI Fit</span>
                </button>
              </div>

              {/* AI Skin Tone Compatibility Badge */}
              {userSkinToneResult && (
                <div className="mt-5 p-3 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded-full border border-white/30"
                    style={{ background: userSkinToneResult.detected_skin_hex || "#E0AC69" }}
                  />
                  <div className="text-[11px] text-white/80">
                    <span className="text-cyber-gold font-bold">Skin Match:</span>{" "}
                    {currentLook.harmonicSkinTones.includes(userSkinToneResult.localAnalysis?.undertone)
                      ? "High Harmonic Glow Match"
                      : "Balanced Contrast"}
                  </div>
                </div>
              )}
            </div>

            {/* Social Icons at Bottom Left (From Video) */}
            <div className="flex items-center gap-4 text-white/40 text-xs pt-4">
              <a href="#" className="hover:text-white transition-colors" title="Instagram">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                </svg>
              </a>
              <a href="#" className="hover:text-white transition-colors" title="Facebook">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path>
                </svg>
              </a>
              <a href="#" className="hover:text-white transition-colors" title="Platform Web">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                </svg>
              </a>
              <a href="#" className="hover:text-white transition-colors font-bold font-mono text-[11px]">
                Bē
              </a>
            </div>
          </div>

          {/* Column 2 (Center): The 3D Floating Garment Showcase (Span 5) */}
          <div className="lg:col-span-5 relative flex flex-col items-center justify-center min-h-[360px] md:min-h-[440px]">
            
            {/* Top-Left Previous Look Floating Mini Thumbnail (Morphing Video Animation) */}
            <button
              onClick={handlePrev}
              className={`absolute top-0 left-0 z-30 p-1.5 rounded-2xl bg-black/40 border border-white/10 hover:border-white/30 backdrop-blur-md transition-all duration-500 hover:scale-105 active:scale-95 group ${
                isTransitioning ? "opacity-30 scale-90" : "opacity-80 scale-100"
              }`}
              title={`Switch back to ${prevLook.colorName}`}
            >
              <div className="relative w-14 h-14 md:w-16 md:h-16 rounded-xl overflow-hidden bg-obsidian-900/60">
                <Image
                  src={prevLook.image}
                  alt={prevLook.colorName}
                  fill
                  className="object-contain p-1 group-hover:scale-110 transition-transform"
                />
              </div>
              <span className="text-[9px] font-mono text-white/50 block text-center mt-1">
                PREV
              </span>
            </button>

            {/* Central Floating 3D Garment */}
            <div className="relative w-full flex flex-col items-center justify-center">
              <div
                className={`relative w-64 h-64 md:w-80 md:h-80 transition-all duration-600 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                  isTransitioning
                    ? transitionDirection === "next"
                      ? "scale-75 -translate-y-8 opacity-0"
                      : "scale-75 translate-y-8 opacity-0"
                    : "scale-100 translate-y-0 opacity-100 animate-float-gentle"
                }`}
              >
                <Image
                  src={currentLook.image}
                  alt={currentLook.colorName}
                  fill
                  priority
                  className="object-contain drop-shadow-[0_20px_45px_rgba(0,0,0,0.9)] select-none"
                />
              </div>

              {/* Dynamic Ground Elliptical Shadow */}
              <div
                className={`w-48 md:w-56 h-6 rounded-full blur-md bg-black/80 transition-all duration-700 mt-2 ${
                  isTransitioning ? "scale-50 opacity-20" : "scale-100 opacity-70 animate-pulse-glow"
                }`}
              />

              {/* Tagline Beneath Jacket (From Video) */}
              <p
                className={`mt-4 text-xs md:text-sm text-center text-white/70 font-medium tracking-wide transition-all duration-500 ${
                  isTransitioning ? "opacity-0 translate-y-2" : "opacity-100 translate-y-0"
                }`}
              >
                {currentLook.tagline}
              </p>
            </div>
          </div>

          {/* Column 3 (Right): Pricing, Sizing & Next Outfit Thumbnail (Span 3) */}
          <div className="lg:col-span-3 flex flex-col justify-between h-full space-y-8 text-right lg:pl-4">
            
            {/* Price Display */}
            <div>
              <div className="flex items-baseline justify-end gap-3">
                <span className="text-3xl md:text-4xl font-black text-white font-mono tracking-tight">
                  {currencyMode === "USD"
                    ? formatUsd(currentLook.price)
                    : formatInr(currentLook.priceInr)}
                </span>
                <span className="text-lg md:text-xl font-medium text-white/40 line-through font-mono">
                  {currencyMode === "USD"
                    ? formatUsd(currentLook.originalPrice)
                    : formatInr(currentLook.originalPriceInr)}
                </span>
              </div>
              <span className="inline-block mt-1 text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {currentLook.discountBadge}
              </span>
            </div>

            {/* Size Selector (From Video: Circular 36, 38, 40) */}
            <div className="space-y-3">
              <div className="flex items-center justify-end gap-2 text-xs text-white/60 font-medium">
                <span>Choose your size:</span>
              </div>

              <div className="flex items-center justify-end gap-2.5">
                {currentLook.sizes.map((s) => {
                  const isSelected = activeSize === s.label;
                  const isAiRec = aiRecommendedSize === s.label || s.aiRecommended;

                  return (
                    <button
                      key={s.label}
                      onClick={() => setSelectedSize(s.label)}
                      className={`relative w-11 h-11 rounded-full text-xs font-bold transition-all flex items-center justify-center active:scale-95 ${
                        isSelected
                          ? "bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.4)] scale-105"
                          : "bg-white/5 border border-white/10 text-white/70 hover:border-white/30 hover:text-white"
                      }`}
                    >
                      <span>{s.label}</span>
                      {isAiRec && !isSelected && (
                        <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyber-cyan animate-ping" />
                      )}
                    </button>
                  );
                })}
              </div>

              {aiRecommendedSize && (
                <div className="text-[10px] font-mono text-cyber-cyan flex items-center justify-end gap-1">
                  <span>✨ AI Rec: Size {aiRecommendedSize}</span>
                </div>
              )}
            </div>

            {/* Bottom-Right Next Look Interactive Thumbnail (From Video!) */}
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-mono text-white/40 mb-1.5 uppercase tracking-wider">
                Next Outfit
              </span>
              <button
                onClick={handleNext}
                className="relative w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-black/40 border border-white/15 hover:border-cyber-cyan/50 backdrop-blur-xl p-1.5 transition-all duration-300 hover:scale-105 active:scale-95 group shadow-xl"
                title={`Click to preview ${nextLook.colorName}`}
              >
                <div className="relative w-full h-full rounded-xl overflow-hidden bg-obsidian-900/50">
                  <Image
                    src={nextLook.image}
                    alt={nextLook.colorName}
                    fill
                    className="object-contain group-hover:scale-110 transition-transform duration-300"
                  />
                </div>
                <div className="absolute inset-0 rounded-2xl border border-cyber-cyan/0 group-hover:border-cyber-cyan/40 transition-colors" />
              </button>
            </div>
          </div>
        </div>

        {/* ----------------------------------------------------------------- */}
        {/* Quick AI & Telemetry HUD Ticker                                   */}
        {/* ----------------------------------------------------------------- */}
        <div className="mt-10 pt-6 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-white/50">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-white/30">INSULATION: </span>
              <span className="text-white/80 font-bold">{currentLook.hudSpecs.thermalRating}</span>
            </div>
            <div>
              <span className="text-white/30">WEATHER: </span>
              <span className="text-white/80 font-bold">{currentLook.hudSpecs.waterproof}</span>
            </div>
            <div className="hidden sm:block">
              <span className="text-white/30">RETURN RISK: </span>
              <span className="text-emerald-400 font-bold">{currentLook.hudSpecs.returnRisk}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onOpenAiFit}
              className="text-[11px] text-cyber-cyan hover:underline flex items-center gap-1 font-sans"
            >
              <span>Launch Morphology Studio</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
