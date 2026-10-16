"use client";

import { useRef } from "react";

const PRESET_SKIN_TONES = [
  { name: "Fair Ivory", hex: "#F7D6BD", undertone: "Cool Pink" },
  { name: "Warm Peach", hex: "#ECC09E", undertone: "Warm Neutral" },
  { name: "Golden Wheatish", hex: "#E0AC69", undertone: "Warm Golden" },
  { name: "Olive Honey", hex: "#C68642", undertone: "Warm Olive" },
  { name: "Deep Bronze", hex: "#8D5524", undertone: "Warm Amber" },
  { name: "Rich Ebony", hex: "#3B2219", undertone: "Cool Deep" },
];

export default function AiColorStylistModal({
  aiColor,
  onApplyLookToStage,
}) {
  const {
    isOpen,
    setIsOpen,
    skinHex,
    setSkinHex,
    selfiePhoto,
    handleSelfieUpload,
    colorGender,
    setColorGender,
    colorResult,
    isLoading,
    runColorAnalysis,
  } = aiColor;

  const selfieInputRef = useRef(null);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-[32px] border border-cyber-gold/30 bg-obsidian-950/95 p-6 md:p-10 shadow-[0_0_80px_rgba(212,175,55,0.2)] text-white scrollbar-none">
        
        {/* Holographic Header Bar */}
        <div className="flex items-start justify-between pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-cyber-gold">
              <span className="w-2 h-2 rounded-full bg-cyber-gold animate-pulse"></span>
              <span>CIELAB + MONK SKIN TONE CHROMATIC HARMONIZER</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black font-heading mt-1">
              AI Photometric Skin & Palette Stylist
            </h2>
            <p className="text-xs text-white/50 mt-1 max-w-lg">
              Extracts melanin pigmentation and Individual Typology Angle (ITA) from selfies to harmonize wardrobe chromatic palettes.
            </p>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/70 hover:text-white transition-all text-sm font-mono"
          >
            ✕
          </button>
        </div>

        {/* Form Controls & Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-6">
          
          {/* Left Column: Selfie Camera & Palette Picker (Span 6) */}
          <div className="lg:col-span-6 space-y-6">
            
            {/* Selfie Photo Upload Box */}
            <div>
              <label className="text-xs font-bold text-white/70 uppercase font-mono tracking-wider block mb-2">
                1. Upload Selfie Or Headshot (Facial ROI Sampling)
              </label>
              <div
                onClick={() => selfieInputRef.current?.click()}
                className="h-44 rounded-2xl border-2 border-dashed border-cyber-gold/40 hover:border-cyber-gold bg-obsidian-900/60 flex flex-col items-center justify-center p-4 text-center cursor-pointer relative overflow-hidden group transition-all"
              >
                {selfiePhoto ? (
                  <img
                    src={selfiePhoto}
                    alt="Selfie Preview"
                    className="w-full h-full object-cover rounded-xl"
                  />
                ) : (
                  <>
                    <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">🤳</div>
                    <span className="text-xs font-bold text-cyber-gold">Upload Selfie For Auto-Detection</span>
                    <span className="text-[10px] text-white/40 mt-1">Samples cheek & forehead pixels in CIELAB</span>
                  </>
                )}
                <input
                  ref={selfieInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleSelfieUpload(e.target.files?.[0])}
                />
              </div>
            </div>

            {/* Quick Skin Tone Presets (Monk Scale Spectrum) */}
            <div>
              <label className="text-xs font-bold text-white/70 uppercase font-mono tracking-wider block mb-2">
                2. Or Select From Standard Spectrum Swatches
              </label>
              <div className="grid grid-cols-3 gap-2.5">
                {PRESET_SKIN_TONES.map((tone) => {
                  const isSelected = skinHex.toLowerCase() === tone.hex.toLowerCase();
                  return (
                    <button
                      key={tone.hex}
                      onClick={() => setSkinHex(tone.hex)}
                      className={`p-3 rounded-xl border flex items-center gap-2.5 transition-all ${
                        isSelected
                          ? "border-cyber-gold bg-cyber-gold/15 shadow-[0_0_15px_rgba(212,175,55,0.3)]"
                          : "border-white/10 bg-white/5 hover:border-white/20"
                      }`}
                    >
                      <span
                        className="w-6 h-6 rounded-full border border-white/20 flex-shrink-0"
                        style={{ background: tone.hex }}
                      />
                      <div className="text-left">
                        <span className="text-[11px] font-bold text-white block leading-tight">
                          {tone.name}
                        </span>
                        <span className="text-[9px] text-white/40 font-mono">
                          {tone.undertone}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Custom Hex Picker Input */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
              <input
                type="color"
                value={skinHex}
                onChange={(e) => setSkinHex(e.target.value)}
                className="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0"
              />
              <div className="flex-grow">
                <span className="text-[10px] font-mono text-white/40 block">CUSTOM HEX TONE</span>
                <span className="text-xs font-mono font-bold text-white">{skinHex.toUpperCase()}</span>
              </div>
              <button
                onClick={() => runColorAnalysis(skinHex)}
                disabled={isLoading}
                className="px-4 py-1.5 rounded-lg bg-cyber-gold/20 hover:bg-cyber-gold/30 border border-cyber-gold/50 text-cyber-gold text-xs font-bold transition-all"
              >
                Analyze
              </button>
            </div>
          </div>

          {/* Right Column: Harmonic Palettes & Seasonal Match (Span 6) */}
          <div className="lg:col-span-6 bg-obsidian-900/90 rounded-2xl border border-white/10 p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <span className="text-xs font-bold font-mono text-white/60 uppercase">
                Chromatic Harmony Engine
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                CIELAB READY
              </span>
            </div>

            {colorResult ? (
              <div className="space-y-5 animate-fade-in">
                {/* Seasonal Badge */}
                <div className="p-5 rounded-2xl bg-gradient-to-br from-cyber-gold/15 to-transparent border border-cyber-gold/30">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-mono text-cyber-gold uppercase tracking-widest block">
                        Seasonal Palette Classification
                      </span>
                      <h4 className="text-xl font-black text-white font-heading mt-0.5">
                        {colorResult.seasonal?.season || colorResult.seasonal_classification}
                      </h4>
                    </div>
                    <div
                      className="w-9 h-9 rounded-full border-2 border-white/30 shadow-lg"
                      style={{ background: colorResult.detected_skin_hex || skinHex }}
                    />
                  </div>
                  <p className="text-xs text-white/60 mt-2 italic">
                    {colorResult.seasonal?.vibe || colorResult.styling_tip}
                  </p>
                </div>

                {/* Recommended Colorway Harmonies */}
                <div>
                  <span className="text-xs font-mono text-white/60 uppercase tracking-wider block mb-3">
                    Wardrobe Harmony Matches
                  </span>
                  <div className="space-y-2">
                    {colorResult.recommended_harmonies?.map((harm) => (
                      <div
                        key={harm.name}
                        className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 border border-white/10"
                      >
                        <div className="flex items-center gap-3">
                          <span
                            className="w-5 h-5 rounded-md border border-white/20"
                            style={{ background: harm.hex }}
                          />
                          <span className="text-xs font-bold text-white">{harm.name}</span>
                        </div>
                        <span className="text-[11px] font-mono text-emerald-400 font-semibold">
                          {harm.compatibility}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Instant Apply Button */}
                <button
                  onClick={() => {
                    if (onApplyLookToStage && typeof colorResult.matchingOutfitIndex === "number") {
                      onApplyLookToStage(colorResult.matchingOutfitIndex);
                    }
                    setIsOpen(false);
                  }}
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyber-gold via-amber-300 to-cyber-gold text-black font-black text-xs shadow-cyber-gold hover:opacity-95 transition-all active:scale-98"
                >
                  ✨ Illuminate Matching Look on Hero Stage
                </button>
              </div>
            ) : (
              <div className="py-16 text-center text-white/40 space-y-2">
                <div className="text-3xl animate-pulse">🎨</div>
                <p className="text-xs font-medium">Select a swatch or upload selfie</p>
                <p className="text-[11px] text-white/30">
                  Our CIELAB engine calculates seasonal harmonic matches in &lt;15ms.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
