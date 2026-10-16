"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { api } from "../lib/api";

const INITIAL_MESSAGES = [
  {
    sender: "bot",
    text: "Hello! I'm your **Snitch AI Stylist**.\n\nAsk me about:\n• **Fit & Body Sizing:** Recommendations for any weight or frame\n• **Skin Tone Color Match:** Best matching palettes for your complexion\n• **Order Status:** e.g., `ORD-SNITCH-88219`\n• **Return & Care Policies:** 7-day pickup & thermal care guidelines.",
  },
];

export function useChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = useCallback(
    async (queryText) => {
      const q = queryText || input;
      if (!q.trim()) return;

      setMessages((prev) => [...prev, { sender: "user", text: q }]);
      setInput("");
      setIsLoading(true);

      try {
        const res = await api.queryChatbot(q);
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: res.response || "I could not find an answer." },
        ]);
      } catch (e) {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: `Connection error: ${e.message}` },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [input]
  );

  const resetChat = useCallback(() => {
    setMessages(INITIAL_MESSAGES);
  }, []);

  return {
    isOpen,
    setIsOpen,
    messages,
    input,
    setInput,
    isLoading,
    sendMessage,
    resetChat,
    messagesEndRef,
  };
}
