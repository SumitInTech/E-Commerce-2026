"use client";

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const isError = toast.type === "error";
  const isInfo = toast.type === "info";

  return (
    <div className="fixed bottom-6 right-6 z-[999] animate-bounce-subtle pointer-events-auto">
      <div
        className={`flex items-center gap-3 px-5 py-3.5 rounded-full border backdrop-blur-2xl shadow-2xl transition-all duration-300 ${
          isError
            ? "bg-red-950/90 border-red-500/50 text-red-200 shadow-red-500/20"
            : isInfo
            ? "bg-cyan-950/90 border-cyan-500/50 text-cyan-200 shadow-cyan-500/20"
            : "bg-obsidian-900/90 border-cyber-cyan/50 text-white shadow-cyber-cyan/20"
        }`}
      >
        <div className="w-2.5 h-2.5 rounded-full bg-cyber-cyan animate-pulse"></div>
        <p className="text-sm font-medium tracking-wide">{toast.msg}</p>
        <button
          onClick={onClose}
          className="ml-2 text-white/50 hover:text-white transition-colors text-xs font-mono"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
