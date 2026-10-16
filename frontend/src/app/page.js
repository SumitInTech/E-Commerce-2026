"use client";

import { useState, useEffect } from "react";
import AnnouncementBar from "../components/layout/AnnouncementBar";
import Navbar from "../components/layout/Navbar";
import HeroOutfitStage from "../components/hero/HeroOutfitStage";
import ProductGrid from "../components/catalog/ProductGrid";
import Footer from "../components/layout/Footer";

// AI Modals & Drawers
import AiFitModal from "../components/ai/AiFitModal";
import AiColorStylistModal from "../components/ai/AiColorStylistModal";
import AiChatbotDrawer from "../components/ai/AiChatbotDrawer";

// Commerce & Admin Modals
import CartDrawer from "../components/commerce/CartDrawer";
import CheckoutModal from "../components/commerce/CheckoutModal";
import OrderConfirmation from "../components/commerce/OrderConfirmation";
import AdminDashboardModal from "../components/admin/AdminDashboardModal";
import AuthModal from "../components/auth/AuthModal";
import Toast from "../components/common/Toast";

// Custom Hooks & Services
import { useCart } from "../hooks/useCart";
import { useAiFit } from "../hooks/useAiFit";
import { useAiColor } from "../hooks/useAiColor";
import { useChatbot } from "../hooks/useChatbot";
import { api } from "../lib/api";
import { DEFAULT_PRODUCTS } from "../lib/constants";

export default function HomePage() {
  // 1. Toast Notification State
  const [toast, setToast] = useState(null);
  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3800);
  };

  // 2. Custom Business Logic Hooks
  const cartHook = useCart(showToast);
  const aiFit = useAiFit(showToast);
  const chatbot = useChatbot();

  // Outfit Look & Size States for the Hero Stage
  const [activeHeroLookIndex, setActiveHeroLookIndex] = useState(0);
  const [heroSelectedSize, setHeroSelectedSize] = useState("38");
  const [aiRecommendedSize, setAiRecommendedSize] = useState(null);

  // AI Color Stylist hook with callback to illuminate matching look on Hero Stage
  const aiColor = useAiColor(showToast, (matchedIndex) => {
    setActiveHeroLookIndex(matchedIndex);
  });

  // 3. Modals & Drawers State
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [confirmedOrder, setConfirmedOrder] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  // 4. Products & Catalog State
  const [products, setProducts] = useState(DEFAULT_PRODUCTS);
  const [searchQuery, setSearchQuery] = useState("");

  // Initialize data on mount
  useEffect(() => {
    async function initCatalog() {
      const data = await api.getProducts();
      if (data && data.length > 0) setProducts(data);
    }
    initCatalog();
  }, []);

  // Sync AI Fit recommended size to hero stage and catalog
  const handleApplyRecommendedSize = (size) => {
    setAiRecommendedSize(size);
    setHeroSelectedSize(size);
    showToast(`✨ AI Recommended Size ${size} applied across your wardrobe!`);
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-white font-body selection:bg-cyber-cyan selection:text-black">
      {/* 1. Global Announcement Marquee */}
      <AnnouncementBar />

      {/* 2. Main Navigation Header */}
      <Navbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onOpenAiFit={() => aiFit.setIsOpen(true)}
        onOpenAiColor={() => {
          aiColor.setIsOpen(true);
          aiColor.runColorAnalysis();
        }}
        onOpenAdmin={() => setIsAdminOpen(true)}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenCart={() => cartHook.setIsOpen(true)}
        cartCount={cartHook.totalCount}
        currentUser={currentUser}
      />

      <main id="home">
        {/* 3. SIGNATURE INTERACTIVE HERO OUTFIT STAGE (Reference Video Showcase) */}
        <HeroOutfitStage
          activeLookIndex={activeHeroLookIndex}
          onSelectLookIndex={setActiveHeroLookIndex}
          onAddToCart={cartHook.addToCart}
          onOpenAiFit={() => aiFit.setIsOpen(true)}
          onOpenAiColor={() => {
            aiColor.setIsOpen(true);
            aiColor.runColorAnalysis();
          }}
          onOpenChat={() => chatbot.setIsOpen(true)}
          selectedSize={heroSelectedSize}
          setSelectedSize={setHeroSelectedSize}
          aiRecommendedSize={aiRecommendedSize}
          userSkinToneResult={aiColor.colorResult}
        />

        {/* 4. Complete Apparel Catalog Grid with 3D Tilt Physics */}
        <ProductGrid
          products={products}
          searchQuery={searchQuery}
          onAddToCart={cartHook.addToCart}
          onOpenAiFit={(prodId) => {
            aiFit.setProductId(prodId);
            aiFit.setIsOpen(true);
          }}
          aiRecommendedSize={aiRecommendedSize}
        />
      </main>

      {/* 5. Luxury Streetwear Footer */}
      <Footer
        onOpenAiFit={() => aiFit.setIsOpen(true)}
        onOpenAiColor={() => {
          aiColor.setIsOpen(true);
          aiColor.runColorAnalysis();
        }}
        onOpenChat={() => chatbot.setIsOpen(true)}
      />

      {/* ----------------------------------------------------------------- */}
      {/* MODALS, DRAWERS & FLOATING TELEMETRY                               */}
      {/* ----------------------------------------------------------------- */}

      {/* Modal 1: AI Fit & Body Morphology Lab (Fat, Weight, Height, Silhouette) */}
      <AiFitModal
        aiFit={aiFit}
        onApplyRecommendedSize={handleApplyRecommendedSize}
        products={products}
      />

      {/* Modal 2: AI Color & Skin Tone Stylist (CIELAB + Monk Scale) */}
      <AiColorStylistModal
        aiColor={aiColor}
        onApplyLookToStage={(matchedIndex) => setActiveHeroLookIndex(matchedIndex)}
      />

      {/* Modal 3: Slide-Over Shopping Cart Bag */}
      <CartDrawer
        cart={cartHook.cart}
        isOpen={cartHook.isOpen}
        setIsOpen={cartHook.setIsOpen}
        onRemoveItem={cartHook.removeFromCart}
        onProceedCheckout={() => setIsCheckoutOpen(true)}
      />

      {/* Modal 4: Idempotent Anti-Duplicate Checkout */}
      <CheckoutModal
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        cart={cartHook.cart}
        onOrderSuccess={(order) => {
          setConfirmedOrder(order);
          cartHook.reloadCart();
        }}
        showToast={showToast}
      />

      {/* Modal 5: Order Confirmation Receipt */}
      <OrderConfirmation
        order={confirmedOrder}
        onClose={() => setConfirmedOrder(null)}
      />

      {/* Modal 6: Executive Control & Microservice Health */}
      <AdminDashboardModal
        isOpen={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
      />

      {/* Modal 7: User Profile & One-Click Demo Personas */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        currentUser={currentUser}
        setCurrentUser={setCurrentUser}
        showToast={showToast}
      />

      {/* Floating AI Stylist Chatbot Drawer HUD */}
      <AiChatbotDrawer chatbot={chatbot} />

      {/* Floating Luxury Notification Toast */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
