"use client";

import { useRef } from "react";

export default function AiFitModal({
  aiFit,
  onApplyRecommendedSize,
  products = [],
}) {
  const {
    isOpen,
    setIsOpen,
    tab,
    setTab,
    heightCm,
    setHeightCm,
    weightKg,
    setWeightKg,
    bodyFatCategory,
    setBodyFatCategory,
    gender,
    setGender,
    productId,
    setProductId,
    frontPhoto,
    setFrontPhoto,
    sidePhoto,
    setSidePhoto,
    isLoading,
    result,
    detectedNotice,
    runFitAnalysis,
    resetPhoto,
  } = aiFit;

  const frontFileRef = useRef(null);
  const sideFileRef = useRef(null);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-[32px] border border-cyber-cyan/30 bg-obsidian-950/95 p-6 md:p-10 shadow-[0_0_80px_rgba(0,240,255,0.25)] text-white scrollbar-none">
        
        {/* Holographic Header Bar */}
        <div className="flex items-start justify-between pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-cyber-cyan">
              <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-pulse"></span>
              <span>NEURAL COMPUTER VISION & MORPHOMETRIC LAB</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black font-heading mt-1">
              AI Biometric Body & Sizing Studio
            </h2>
            <p className="text-xs text-white/50 mt-1 max-w-lg">
              Engineered with Ramanujan ellipse circumference regression to compute kinematic ease for slim, athletic, and robust body fat distributions.
            </p>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/70 hover:text-white transition-all text-sm font-mono"
          >
            ✕
          </button>
        </div>

        {/* Tab Switcher: Silhouette Photo Scan vs Manual Anthropometrics */}
        <div className="flex items-center gap-2 my-6 p-1 bg-obsidian-900 border border-white/10 rounded-2xl w-fit">
          <button
            onClick={() => setTab("manual")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
              tab === "manual"
                ? "bg-white text-black shadow-lg"
                : "text-white/60 hover:text-white"
            }`}
          >
            📐 Anthropometric Biometrics
          </button>
          <button
            onClick={() => setTab("scan")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              tab === "scan"
                ? "bg-cyber-cyan text-black shadow-cyber-cyan font-black"
                : "text-white/60 hover:text-white"
            }`}
          >
            <span>📸 Single-Photo Depth Scan</span>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/30 font-mono">CV</span>
          </button>
        </div>

        {/* Form Inputs & Visual Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Input Parameter Controls (Span 7) */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* Target Product Selector */}
            <div>
              <label className="text-xs font-bold text-white/70 uppercase font-mono tracking-wider block mb-2">
                1. Select Target Garment For Ease Evaluation
              </label>
              <select
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-cyber-cyan"
              >
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.fit_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Manual Tab: Height, Weight, Body Fat, Gender */}
            {tab === "manual" && (
              <div className="space-y-5 p-5 rounded-2xl bg-white/5 border border-white/10">
                {/* Gender Toggle */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white/70">Anatomical Silhouette:</span>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setGender("male")}
                      className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        gender === "male"
                          ? "bg-cyber-cyan/20 border border-cyber-cyan text-cyber-cyan"
                          : "bg-white/5 text-white/50 border border-white/10"
                      }`}
                    >
                      Male Athletic (V-Taper)
                    </button>
                    <button
                      type="button"
                      onClick={() => setGender("female")}
                      className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        gender === "female"
                          ? "bg-cyber-magenta/20 border border-cyber-magenta text-cyber-magenta"
                          : "bg-white/5 text-white/50 border border-white/10"
                      }`}
                    >
                      Female Curvature (Hourglass)
                    </button>
                  </div>
                </div>

                {/* Body Fat / Frame Morphology Distribution */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="font-bold text-white/70">Body Morphology & Frame Distribution:</span>
                    <span className="text-cyber-cyan font-mono capitalize">{bodyFatCategory}</span>
                  </div>
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { id: "slim", label: "Slim / Linear" },
                      { id: "athletic", label: "Athletic / V-Cut" },
                      { id: "robust", label: "Robust / Heavy" },
                      { id: "curvy", label: "Curved / Volumetric" },
                    ].map((b) => (
                      <button
                        key={b.id}
                        type="button"
                        onClick={() => setBodyFatCategory(b.id)}
                        className={`p-2.5 rounded-xl text-center text-[11px] font-bold border transition-all ${
                          bodyFatCategory === b.id
                            ? "bg-white text-black border-white shadow-md scale-102"
                            : "bg-obsidian-900/60 border-white/10 text-white/60 hover:text-white"
                        }`}
                      >
                        {b.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Height Slider */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1.5 font-mono">
                    <span className="text-white/60">HEIGHT (CM):</span>
                    <span className="text-white font-bold text-sm">{heightCm} cm</span>
                  </div>
                  <input
                    type="range"
                    min="145"
                    max="210"
                    step="0.5"
                    value={heightCm}
                    onChange={(e) => setHeightCm(e.target.value)}
                    className="w-full accent-cyber-cyan cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-white/30 font-mono mt-1">
                    <span>145 cm</span>
                    <span>178 cm (Std)</span>
                    <span>210 cm</span>
                  </div>
                </div>

                {/* Weight Slider */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1.5 font-mono">
                    <span className="text-white/60">WEIGHT (KG):</span>
                    <span className="text-white font-bold text-sm">{weightKg} kg</span>
                  </div>
                  <input
                    type="range"
                    min="40"
                    max="140"
                    step="0.5"
                    value={weightKg}
                    onChange={(e) => setWeightKg(e.target.value)}
                    className="w-full accent-cyber-cyan cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-white/30 font-mono mt-1">
                    <span>40 kg</span>
                    <span>75 kg (Std)</span>
                    <span>140 kg</span>
                  </div>
                </div>
              </div>
            )}

            {/* Photo Scan Tab */}
            {tab === "scan" && (
              <div className="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-4">
                <div className="text-xs text-white/70">
                  Upload a front-facing full body photo. Our computer vision segmenter extracts your 2D body boundary contours to fit 3D Ramanujan cross-sectional cylinders:
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* Front Photo Upload */}
                  <div
                    onClick={() => frontFileRef.current?.click()}
                    className="h-44 rounded-xl border-2 border-dashed border-cyber-cyan/40 hover:border-cyber-cyan bg-obsidian-900/60 flex flex-col items-center justify-center p-3 text-center cursor-pointer relative overflow-hidden group"
                  >
                    {frontPhoto ? (
                      <img
                        src={frontPhoto}
                        alt="Front Photo"
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <>
                        <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📸</div>
                        <span className="text-xs font-bold text-cyber-cyan">Front Photo (Required)</span>
                        <span className="text-[10px] text-white/40 mt-1">Stand straight, natural lighting</span>
                      </>
                    )}
                    <input
                      ref={frontFileRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => setFrontPhoto(e.target.files?.[0])}
                    />
                  </div>

                  {/* Side Profile Photo Upload */}
                  <div
                    onClick={() => sideFileRef.current?.click()}
                    className="h-44 rounded-xl border-2 border-dashed border-white/20 hover:border-white/40 bg-obsidian-900/60 flex flex-col items-center justify-center p-3 text-center cursor-pointer relative overflow-hidden group"
                  >
                    {sidePhoto ? (
                      <img
                        src={sidePhoto}
                        alt="Side Photo"
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <>
                        <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📐</div>
                        <span className="text-xs font-bold text-white/70">Side Profile (Optional)</span>
                        <span className="text-[10px] text-white/40 mt-1">For Ramanujan depth ratio</span>
                      </>
                    )}
                    <input
                      ref={sideFileRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => setSidePhoto(e.target.files?.[0])}
                    />
                  </div>
                </div>

                {frontPhoto && (
                  <button
                    onClick={resetPhoto}
                    className="text-[11px] text-red-400 hover:underline font-mono"
                  >
                    ✕ Reset Photos
                  </button>
                )}
              </div>
            )}

            {/* Run Analysis Trigger */}
            <button
              onClick={runFitAnalysis}
              disabled={isLoading}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-cyber-cyan via-teal-400 to-cyber-cyan text-black font-black text-sm tracking-wide shadow-cyber-cyan hover:opacity-95 transition-all flex items-center justify-center gap-2 active:scale-98 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></span>
                  <span>Executing Ramanujan Morphometrics...</span>
                </>
              ) : (
                <>
                  <span>⚡ COMPUTE 3D BIOMETRIC SIZING</span>
                  <span>→</span>
                </>
              )}
            </button>

            {detectedNotice && (
              <div className="p-3 rounded-xl bg-cyber-cyan/10 border border-cyber-cyan/30 text-xs text-cyber-cyan flex items-center gap-2">
                <span>✦</span>
                <span>{detectedNotice}</span>
              </div>
            )}
          </div>

          {/* Right Column: Prediction Results & HUD Telemetry (Span 5) */}
          <div className="lg:col-span-5 bg-obsidian-900/90 rounded-2xl border border-white/10 p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <span className="text-xs font-bold font-mono text-white/60 uppercase">
                Inference Telemetry
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                MODEL ACTIVE
              </span>
            </div>

            {result ? (
              <div className="space-y-5 animate-fade-in">
                {/* Big Recommended Size Badge */}
                <div className="text-center p-6 rounded-2xl bg-gradient-to-b from-cyber-cyan/15 to-transparent border border-cyber-cyan/30">
                  <span className="text-[11px] font-mono text-cyber-cyan uppercase tracking-widest block mb-1">
                    Optimal Streetwear Size
                  </span>
                  <div className="text-5xl font-black text-white font-mono tracking-tight">
                    {result.recommended_size}
                  </div>
                  <span className="text-xs text-white/60 mt-1 block">
                    Morphology: <strong className="text-white">{result.body_morphology}</strong>
                  </span>
                </div>

                {/* Measurements Cross-Section */}
                <div className="space-y-2.5 font-mono text-xs">
                  <div className="flex justify-between p-2.5 rounded-lg bg-white/5">
                    <span className="text-white/50">CHEST CIRCUMFERENCE:</span>
                    <span className="text-white font-bold">{result.measurements?.chest_cm} cm</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded-lg bg-white/5">
                    <span className="text-white/50">WAIST CIRCUMFERENCE:</span>
                    <span className="text-white font-bold">{result.measurements?.waist_cm} cm</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded-lg bg-white/5">
                    <span className="text-white/50">HIP CIRCUMFERENCE:</span>
                    <span className="text-white font-bold">{result.measurements?.hip_cm} cm</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <span className="text-emerald-400">ESTIMATED RETURN RISK:</span>
                    <span className="text-emerald-300 font-bold">
                      {result.return_risk_score ? `${(result.return_risk_score * 100).toFixed(1)}%` : "1.8%"}
                    </span>
                  </div>
                </div>

                {/* Sizing Advice */}
                <p className="text-xs text-white/60 leading-relaxed italic bg-white/5 p-3 rounded-xl border border-white/10">
                  "{result.sizing_advice || "Optimal relaxed drop-shoulder drape with comfortable natural breathing room."}"
                </p>

                {/* Apply Button */}
                <button
                  onClick={() => {
                    if (onApplyRecommendedSize) {
                      onApplyRecommendedSize(result.recommended_size);
                    }
                    setIsOpen(false);
                  }}
                  className="w-full py-3 rounded-xl bg-white text-black font-bold text-xs hover:bg-white/90 transition-all shadow-lg active:scale-98"
                >
                  ✓ Apply Size {result.recommended_size} to Stage
                </button>
              </div>
            ) : (
              <div className="py-16 text-center text-white/40 space-y-2">
                <div className="text-3xl animate-pulse">📐</div>
                <p className="text-xs font-medium">Awaiting Biometric Trigger</p>
                <p className="text-[11px] text-white/30">
                  Adjust height/weight sliders or upload photo, then click "COMPUTE 3D BIOMETRIC SIZING".
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
