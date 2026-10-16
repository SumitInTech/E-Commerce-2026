"use client";

export default function Navbar({
  searchQuery,
  setSearchQuery,
  onOpenAiFit,
  onOpenAiColor,
  onOpenAdmin,
  onOpenAuth,
  onOpenCart,
  cartCount,
  currentUser,
}) {
  return (
    <header className="main-header select-none">
      <div className="header-container">
        {/* Brand Identity */}
        <div className="brand-area">
          <a href="#home" className="brand-logo flex items-center gap-2">
            <span className="brand-name tracking-tighter text-2xl font-black text-white">
              SNITCH
            </span>
            <span className="brand-badge bg-cyber-cyan/10 text-cyber-cyan border border-cyber-cyan/30 text-[10px] px-2 py-0.5 rounded font-mono font-bold tracking-widest">
              NEXT.JS LUXE
            </span>
          </a>
        </div>

        {/* Global Search Bar (Amazon / Flipkart Inspired) */}
        <div className="header-search flex items-center bg-obsidian-850/80 border border-white/10 rounded-full px-4 py-2 w-full max-w-md focus-within:border-cyber-cyan/50 focus-within:ring-2 focus-within:ring-cyber-cyan/20 transition-all">
          <svg
            className="search-icon text-white/40 mr-2 flex-shrink-0"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            placeholder="Search Cuban shirts, 240 GSM tees, puffers..."
            className="search-input bg-transparent text-sm text-white placeholder-white/40 w-full outline-none"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="text-xs text-white/40 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* AI & Executive Navigation */}
        <nav className="nav-links flex items-center gap-2">
          <button
            className="nav-btn ai-nav-btn text-xs font-semibold px-3 py-1.5 rounded-full border border-cyber-cyan/40 bg-cyber-cyan/10 text-cyber-cyan hover:bg-cyber-cyan/20 hover:shadow-cyber-cyan transition-all"
            onClick={onOpenAiFit}
          >
            ✨ AI FIT LAB
          </button>
          <button
            className="nav-btn ai-nav-btn text-xs font-semibold px-3 py-1.5 rounded-full border border-cyber-gold/40 bg-cyber-gold/10 text-cyber-gold hover:bg-cyber-gold/20 hover:shadow-cyber-gold transition-all"
            onClick={onOpenAiColor}
          >
            🎨 COLOR STYLIST
          </button>
          <button
            className="nav-btn admin-nav-btn text-xs font-medium px-3 py-1.5 rounded-full border border-white/10 text-white/70 hover:text-white hover:border-white/30 transition-all"
            onClick={onOpenAdmin}
          >
            📊 ADMIN & METRICS
          </button>
        </nav>

        {/* User & Commerce Controls */}
        <div className="header-actions flex items-center gap-3">
          <div
            className="action-btn hidden md:flex items-center gap-1.5 text-xs text-emerald-400/90 font-mono bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full cursor-default"
            title="Gateway Connected"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>7 SERVICES OK</span>
          </div>

          <button
            className="action-btn flex items-center gap-1.5 text-xs font-medium text-white/80 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 px-3.5 py-1.5 rounded-full transition-all"
            onClick={onOpenAuth}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span>{currentUser ? currentUser.full_name.split(" ")[0].toUpperCase() : "SIGN IN"}</span>
          </button>

          <button
            className="action-btn cart-btn relative flex items-center justify-center p-2 rounded-full bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/40 text-cyber-cyan transition-all"
            onClick={onOpenCart}
            aria-label="View Shopping Cart"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="9" cy="21" r="1"></circle>
              <circle cx="20" cy="21" r="1"></circle>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
            </svg>
            <span className="cart-count absolute -top-1.5 -right-1.5 bg-cyber-cyan text-obsidian-950 text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center shadow-lg">
              {cartCount}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
