"use client";

const SUGGESTION_CHIPS = [
  "What size for 80kg athletic frame?",
  "How to wash 750-fill down puffers?",
  "Track ORD-SNITCH-88219",
  "Explain 7-day return policy",
];

export default function AiChatbotDrawer({ chatbot }) {
  const {
    isOpen,
    setIsOpen,
    messages,
    input,
    setInput,
    isLoading,
    sendMessage,
    resetChat,
    messagesEndRef,
  } = chatbot;

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 left-6 z-40 px-5 py-3 rounded-full bg-gradient-to-r from-cyber-cyan via-teal-400 to-cyber-cyan text-black font-black text-xs shadow-cyber-cyan hover:scale-105 active:scale-95 transition-all flex items-center gap-2 group border border-white/20"
        title="Open AI Stylist HUD"
      >
        <span className="w-2.5 h-2.5 rounded-full bg-black animate-ping" />
        <span>💬 AI STYLIST HUD</span>
      </button>
    );
  }

  const formatText = (text) => {
    if (!text) return null;
    const lines = text.split("\n");
    return lines.map((line, lIdx) => {
      if (!line.trim()) return <div key={lIdx} className="h-1.5" />;
      const isBullet = line.trim().startsWith("•") || line.trim().startsWith("-");
      const cleanLine = isBullet ? line.trim().replace(/^[•\-]\s*/, "") : line;
      const parts = cleanLine.split(/(\*\*.*?\*\*|`.*?`)/g);

      const formatted = parts.map((part, pIdx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={pIdx} className="text-white font-bold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <code key={pIdx} className="px-1.5 py-0.5 rounded bg-white/10 text-cyber-cyan font-mono text-[11px]">
              {part.slice(1, -1)}
            </code>
          );
        }
        return part;
      });

      if (isBullet) {
        return (
          <div key={lIdx} className="flex items-start gap-2 my-1 text-xs">
            <span className="text-cyber-cyan mt-1">▪</span>
            <span className="text-white/80">{formatted}</span>
          </div>
        );
      }
      return (
        <p key={lIdx} className="text-xs text-white/80 my-1 leading-relaxed">
          {formatted}
        </p>
      );
    });
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-obsidian-950/95 border-l border-cyber-cyan/30 backdrop-blur-2xl shadow-[0_0_80px_rgba(0,240,255,0.2)] flex flex-col justify-between text-white animate-slide-left select-none">
      
      {/* Drawer Header */}
      <div className="p-5 border-b border-white/10 flex items-center justify-between bg-obsidian-900/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-cyber-cyan/15 border border-cyber-cyan/40 flex items-center justify-center text-cyber-cyan font-bold text-xs">
            ✨
          </div>
          <div>
            <h3 className="text-sm font-bold text-white font-heading">
              Snitch AI Fashion Assistant
            </h3>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ONLINE // RAG AGENT v2.6
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={resetChat}
            className="text-[10px] font-mono text-white/40 hover:text-white px-2 py-1 rounded bg-white/5 border border-white/10"
            title="Reset Chat History"
          >
            Reset
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/60 hover:text-white text-xs"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-grow overflow-y-auto p-5 space-y-4 scrollbar-none">
        {messages.map((m, idx) => {
          const isBot = m.sender === "bot";
          return (
            <div
              key={idx}
              className={`flex flex-col ${isBot ? "items-start" : "items-end"}`}
            >
              <span className="text-[10px] font-mono text-white/30 mb-1">
                {isBot ? "SNITCH AI STYLIST" : "YOU"}
              </span>
              <div
                className={`max-w-[88%] p-3.5 rounded-2xl ${
                  isBot
                    ? "bg-obsidian-900 border border-white/10 text-white rounded-tl-sm shadow-md"
                    : "bg-cyber-cyan text-black font-medium rounded-tr-sm shadow-cyber-cyan"
                }`}
              >
                {isBot ? formatText(m.text) : <p className="text-xs">{m.text}</p>}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-obsidian-900/60 border border-white/10 w-fit">
            <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-bounce" />
            <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-bounce [animation-delay:0.2s]" />
            <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-bounce [animation-delay:0.4s]" />
            <span className="text-[11px] font-mono text-white/50 ml-1">AI Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Chips */}
      <div className="px-5 py-2.5 bg-obsidian-900/40 border-t border-white/5 flex items-center gap-2 overflow-x-auto scrollbar-none">
        {SUGGESTION_CHIPS.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => sendMessage(chip)}
            className="text-[11px] font-mono whitespace-nowrap px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 text-white/70 hover:text-white transition-all flex-shrink-0"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-white/10 bg-obsidian-900/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask about body sizing, returns, orders..."
            className="flex-grow bg-obsidian-950 border border-white/15 focus:border-cyber-cyan rounded-xl px-4 py-2.5 text-xs text-white outline-none transition-all placeholder-white/30"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2.5 rounded-xl bg-cyber-cyan hover:bg-cyan-300 text-black font-black text-xs transition-all disabled:opacity-40"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
