"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";

export function useCart(showToast) {
  const [sessionId, setSessionId] = useState("");
  const [cart, setCart] = useState({ items: [], subtotal: 0, tax: 0, shipping: 0, total: 0 });
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize or restore session
  useEffect(() => {
    let sess = localStorage.getItem("snitch_session_id");
    if (!sess) {
      sess = "sess_" + Math.random().toString(36).substring(2, 10);
      localStorage.setItem("snitch_session_id", sess);
    }
    setSessionId(sess);
    loadCart(sess);
  }, []);

  const loadCart = useCallback(async (sess) => {
    setIsLoading(true);
    try {
      const data = await api.getCart(sess);
      if (data && data.items) setCart(data);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addToCart = useCallback(
    async (product, sizeLabel = "38", quantity = 1) => {
      // Optimistic UI Update
      setCart((prev) => {
        const existingIdx = prev.items.findIndex(
          (it) => it.product_id === product.id && it.size_label === sizeLabel
        );
        let updatedItems = [...prev.items];
        if (existingIdx > -1) {
          updatedItems[existingIdx].quantity += quantity;
        } else {
          updatedItems.push({
            id: `item_${Date.now()}`,
            product_id: product.id,
            name: product.name,
            size_label: sizeLabel,
            unit_price: product.price,
            quantity: quantity,
            image_url: product.image,
          });
        }
        const subtotal = updatedItems.reduce((acc, it) => acc + it.unit_price * it.quantity, 0);
        const tax = Math.round(subtotal * 0.12);
        const shipping = subtotal > 1499 ? 0 : 150;
        return {
          items: updatedItems,
          subtotal,
          tax,
          shipping,
          total: subtotal + tax + shipping,
        };
      });

      if (showToast) {
        showToast(`🛍️ Added ${product.name} (Size ${sizeLabel}) to Bag!`);
      }
      setIsOpen(true);

      // Background API sync
      if (sessionId) {
        const backendCart = await api.addToCart(sessionId, product.id, sizeLabel, quantity);
        if (backendCart && backendCart.items) {
          setCart(backendCart);
        }
      }
    },
    [sessionId, showToast]
  );

  const removeFromCart = useCallback(
    async (itemId) => {
      setCart((prev) => {
        const updated = prev.items.filter((it) => it.id !== itemId);
        const subtotal = updated.reduce((acc, it) => acc + it.unit_price * it.quantity, 0);
        const tax = Math.round(subtotal * 0.12);
        const shipping = subtotal > 1499 || subtotal === 0 ? 0 : 150;
        return {
          items: updated,
          subtotal,
          tax,
          shipping,
          total: subtotal + tax + shipping,
        };
      });

      if (showToast) showToast("Item removed from bag", "info");

      if (sessionId) {
        const backendCart = await api.removeFromCart(sessionId, itemId);
        if (backendCart && backendCart.items) setCart(backendCart);
      }
    },
    [sessionId, showToast]
  );

  const totalCount = cart.items.reduce((sum, it) => sum + it.quantity, 0);

  return {
    sessionId,
    cart,
    isOpen,
    setIsOpen,
    isLoading,
    addToCart,
    removeFromCart,
    totalCount,
    reloadCart: () => loadCart(sessionId),
  };
}
