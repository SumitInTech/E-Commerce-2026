"use client";

export default function Footer({ onOpenAiFit, onOpenAiColor, onOpenChat }) {
  return (
    <footer className="w-full bg-obsidian-950 border-t border-white/10 pt-16 pb-12 px-4 md:px-8 text-white select-none">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-10 pb-12 border-b border-white/10">
        
        {/* Brand & Mission (Span 5) */}
        <div className="md:col-span-5 space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-black tracking-tighter">SNITCH</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/70">
              NEXT.JS 16 // FAST-FASHION
            </span>
          </div>
          <p className="text-xs text-white/50 leading-relaxed max-w-sm">
            Unapologetic modern streetwear engineered with 3D anthropometric silhouette vision, kinematic ease fitting algorithms, and CIELAB seasonal chromatic harmonies.
          </p>
          <div className="pt-2 flex items-center gap-2 text-xs font-mono text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>7 ENTERPRISE MICROSERVICES HEALTH: 100% OPERATIONAL</span>
          </div>
        </div>

        {/* AI Fitting Suite (Span 3) */}
        <div className="md:col-span-3 space-y-3">
          <span className="text-xs font-mono text-cyber-cyan uppercase tracking-widest font-bold block">
            AI Technology Suite
          </span>
          <ul className="space-y-2 text-xs text-white/60">
            <li>
              <button onClick={onOpenAiFit} className="hover:text-white transition-colors">
                ✨ 3D Ramanujan Biometric Sizing
              </button>
            </li>
            <li>
              <button onClick={onOpenAiColor} className="hover:text-white transition-colors">
                🎨 CIELAB + Monk Skin Tone Stylist
              </button>
            </li>
            <li>
              <button onClick={onOpenChat} className="hover:text-white transition-colors">
                💬 Contextual AI Stylist RAG
              </button>
            </li>
            <li>
              <span className="text-white/30">⚡ Single-Photo Depth Segmentation</span>
            </li>
          </ul>
        </div>

        {/* Collections & Policies (Span 4) */}
        <div className="md:col-span-4 space-y-3">
          <span className="text-xs font-mono text-white/40 uppercase tracking-widest font-bold block">
            Atelier Standards
          </span>
          <div className="grid grid-cols-2 gap-4 text-xs text-white/60">
            <div className="space-y-2">
              <span className="text-white font-semibold block">Policies</span>
              <p className="text-[11px] text-white/40">7-Day Free Reverse Logistics</p>
              <p className="text-[11px] text-white/40">Cryptographic Payment Safety</p>
              <p className="text-[11px] text-white/40">Zero Return-Rate Protocol</p>
            </div>
            <div className="space-y-2">
              <span className="text-white font-semibold block">Runway Drops</span>
              <p className="text-[11px] text-white/40">Gloss Puffer Chambers</p>
              <p className="text-[11px] text-white/40">240 GSM Oversized Cotton</p>
              <p className="text-[11px] text-white/40">Normandy Linen Notch Shirts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto pt-8 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-white/40 gap-4">
        <span>© 2026 SNITCH LUXE FAST-FASHION TECHNOLOGIES. ALL RIGHTS RESERVED.</span>
        <span>ENGINEERED WITH NEXT.JS 16, TAILWIND CSS & ANTIGRAVITY UI SPEC</span>
      </div>
    </footer>
  );
}
