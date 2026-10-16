"use client";

import { useState } from "react";

export default function AuthModal({
  isOpen,
  onClose,
  currentUser,
  setCurrentUser,
  showToast,
}) {
  const [email, setEmail] = useState("buyer@snitch.com");
  const [password, setPassword] = useState("Buyer@12345");
  const [mode, setMode] = useState("signin"); // "signin" | "signup"

  if (!isOpen) return null;

  const handleDemoSignIn = (role, name, userEmail) => {
    const user = {
      full_name: name,
      email: userEmail,
      role: role,
      token: "demo_jwt_token_" + Math.random().toString(36).substring(2, 8),
    };
    setCurrentUser(user);
    if (showToast) showToast(`Signed in as ${name} (${role.toUpperCase()})`);
    onClose();
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    if (showToast) showToast("Signed out successfully", "info");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-md rounded-[32px] border border-white/15 bg-obsidian-950 p-6 md:p-8 text-white shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">🔐</span>
            <h3 className="text-base font-bold font-heading">
              {currentUser ? "User Profile" : mode === "signin" ? "Sign In to Snitch" : "Create Account"}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/60 hover:text-white text-xs font-mono"
          >
            ✕
          </button>
        </div>

        {currentUser ? (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
              <div className="text-xs font-mono text-white/40">AUTHENTICATED PERSONA</div>
              <div className="text-lg font-black text-white">{currentUser.full_name}</div>
              <div className="text-xs text-white/60 font-mono">{currentUser.email}</div>
              <span className="inline-block mt-2 text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-cyan/20 text-cyber-cyan border border-cyber-cyan/30">
                ROLE: {currentUser.role?.toUpperCase()}
              </span>
            </div>

            <button
              onClick={handleSignOut}
              className="w-full py-3 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 text-xs font-bold transition-all"
            >
              Sign Out
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Quick Demo Switcher */}
            <div>
              <span className="text-[10px] font-mono text-cyber-cyan uppercase tracking-wider block mb-2">
                Fast One-Click Demo Personas:
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleDemoSignIn("buyer", "Aryan Sharma", "buyer@snitch.com")}
                  className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-center text-xs font-bold"
                >
                  <span className="block text-base mb-1">🛍️</span>
                  <span>Shopper</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoSignIn("vendor", "Atelier Noir", "vendor@snitch.com")}
                  className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-center text-xs font-bold"
                >
                  <span className="block text-base mb-1">🏬</span>
                  <span>Vendor</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoSignIn("admin", "Platform Lead", "admin@snitch.com")}
                  className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-center text-xs font-bold"
                >
                  <span className="block text-base mb-1">⚡</span>
                  <span>Admin</span>
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3 text-white/30 text-xs font-mono">
              <span className="h-px bg-white/10 flex-grow" />
              <span>OR ENTER CREDENTIALS</span>
              <span className="h-px bg-white/10 flex-grow" />
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleDemoSignIn("buyer", "Aryan Sharma", email);
              }}
              className="space-y-3"
            >
              <input
                type="email"
                required
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-cyan"
              />
              <input
                type="password"
                required
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-obsidian-900 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-cyber-cyan"
              />
              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-white text-black font-bold text-xs hover:bg-white/90 shadow-lg transition-all"
              >
                {mode === "signin" ? "Sign In" : "Sign Up"}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
