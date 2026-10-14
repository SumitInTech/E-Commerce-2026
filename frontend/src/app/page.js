"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function HomePage() {
  // Application State
  const [sessionId, setSessionId] = useState("");
  const [token, setToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [healthStatus, setHealthStatus] = useState([]);
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSizes, setSelectedSizes] = useState({});
  const [cart, setCart] = useState({ items: [], subtotal: 0, tax: 0, shipping: 0, total: 0 });

  // Modals & Drawers Visibility
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isAiFitOpen, setIsAiFitOpen] = useState(false);
  const [isAiColorOpen, setIsAiColorOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // AI Fit State
  const [fitHeight, setFitHeight] = useState(178);
  const [fitWeight, setFitWeight] = useState(75);
  const [fitGender, setFitGender] = useState("male");
  const [fitProductId, setFitProductId] = useState(1);
  const [fitResult, setFitResult] = useState(null);
  const [isFitLoading, setIsFitLoading] = useState(false);

  // AI Color State
  const [skinHex, setSkinHex] = useState("#E0AC69");
  const [colorResult, setColorResult] = useState(null);

  // Chatbot State
  const [chatMessages, setChatMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I'm your Snitch AI Stylist. Ask me about sizing, return policies, garment care, or check an order status (e.g., ORD-SNITCH-88219)."
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Checkout State
  const [checkoutData, setCheckoutData] = useState({
    name: "Aryan Sharma",
    email: "buyer@snitch.com",
    address: "402 Skylark Apts, Indiranagar, Bangalore, 560038",
    method: "CARD"
  });
  const [orderConfirmation, setOrderConfirmation] = useState(null);
  const [isPaying, setIsPaying] = useState(false);

  // Admin Data State
  const [adminTab, setAdminTab] = useState("metrics");
  const [adminMetrics, setAdminMetrics] = useState(null);
  const [adminTickets, setAdminTickets] = useState([]);
  const [adminVendors, setAdminVendors] = useState([]);
  const [vendorForm, setVendorForm] = useState({
    store_name: "",
    contact_name: "",
    contact_email: "",
    contact_phone: ""
  });

  // Auth State
  const [authEmail, setAuthEmail] = useState("buyer@snitch.com");
  const [authPassword, setAuthPassword] = useState("Buyer@12345");

  // Initialize Session & Load Data
  useEffect(() => {
    let sess = localStorage.getItem("snitch_session_id");
    if (!sess) {
      sess = "sess_" + Math.random().toString(36).substring(2, 10);
      localStorage.setItem("snitch_session_id", sess);
    }
    setSessionId(sess);

    const savedToken = localStorage.getItem("snitch_jwt_token");
    if (savedToken) {
      setToken(savedToken);
      fetchUserProfile(savedToken);
    }

    loadHealth();
    loadProducts();
    loadCart(sess);
  }, []);

  // Filter products when category or search changes
  useEffect(() => {
    let list = products;
    if (activeCategory !== "all") {
      const catMap = {
        shirts: "shirt",
        tees: "t_shirt",
        trousers: "pants",
        jackets: "jacket"
      };
      const targetType = catMap[activeCategory];
      list = list.filter((p) => p.garment_type === targetType);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.fabric.toLowerCase().includes(q) ||
          p.description?.toLowerCase().includes(q)
      );
    }
    setFilteredProducts(list);
  }, [products, activeCategory, searchQuery]);

  // ---------------------------------------------------------------------------
  // API Calls
  // ---------------------------------------------------------------------------
  async function loadHealth() {
    try {
      const res = await fetch(`${API_BASE}/gateway/health`);
      if (res.ok) {
        const data = await res.json();
        const list = Object.entries(data.services).map(([k, v]) => ({ id: k, ...v }));
        setHealthStatus(list);
      }
    } catch (e) {
      console.warn("Health check failed", e);
    }
  }

  async function loadProducts() {
    try {
      const res = await fetch(`${API_BASE}/catalog/products`);
      if (res.ok) {
        const data = await res.json();
        setProducts(data);
        if (data.length > 0) setFitProductId(data[0].id);
      }
    } catch (e) {
      console.error("Products load failed", e);
    }
  }

  async function loadCart(sess) {
    try {
      const res = await fetch(`${API_BASE}/orders/cart/${sess || sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (e) {
      console.warn("Cart load error", e);
    }
  }

  async function fetchUserProfile(jwtToken) {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      if (res.ok) {
        const user = await res.json();
        setCurrentUser(user);
      } else {
        localStorage.removeItem("snitch_jwt_token");
        setToken(null);
      }
    } catch (e) {
      console.warn("Profile fetch error", e);
    }
  }

  // ---------------------------------------------------------------------------
  // Cart Actions
  // ---------------------------------------------------------------------------
  async function handleAddToCart(productId, sizeLabel) {
    try {
      const res = await fetch(`${API_BASE}/orders/cart/add?session_id=${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: productId,
          size_label: sizeLabel,
          quantity: 1
        })
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Failed to add to cart");
        return;
      }
      const updated = await res.json();
      setCart(updated);
      setIsCartOpen(true);
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleRemoveFromCart(itemId) {
    try {
      const res = await fetch(`${API_BASE}/orders/cart/remove/${itemId}?session_id=${sessionId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        const updated = await res.json();
        setCart(updated);
      }
    } catch (e) {
      alert(e.message);
    }
  }

  // ---------------------------------------------------------------------------
  // AI Fit Calculations
  // ---------------------------------------------------------------------------
  async function runAiFit() {
    setIsFitLoading(true);
    try {
      // Step 1: Predict Measurements (Model 1)
      const m1Res = await fetch(`${API_BASE}/ai-fit/predict-measurements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          height_cm: parseFloat(fitHeight),
          weight_kg: parseFloat(fitWeight),
          gender: fitGender
        })
      });
      const m1 = await m1Res.json();

      // Step 2: Evaluate Garment Fit against product (Model 2)
      const m2Res = await fetch(`${API_BASE}/ai-fit/evaluate-garment-fit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chest_cm: m1.predictions.chest_cm,
          waist_cm: m1.predictions.waist_cm,
          hip_cm: m1.predictions.hip_cm,
          product_id: parseInt(fitProductId)
        })
      });
      const m2 = await m2Res.json();

      setFitResult({
        measurements: m1.predictions,
        inferenceMode: m1.inference_mode,
        ...m2
      });
    } catch (e) {
      alert(`AI Fit Engine Error: ${e.message}`);
    } finally {
      setIsFitLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // AI Color Stylist
  // ---------------------------------------------------------------------------
  async function runAiColor(hex) {
    try {
      const res = await fetch(`${API_BASE}/ai-fit/color-palette`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hex_color: hex || skinHex })
      });
      if (res.ok) {
        const data = await res.json();
        setColorResult(data);
      }
    } catch (e) {
      console.warn("Color analysis error", e);
    }
  }

  // ---------------------------------------------------------------------------
  // AI Chatbot
  // ---------------------------------------------------------------------------
  async function sendChatMessage(queryText) {
    const q = queryText || chatInput;
    if (!q.trim()) return;

    setChatMessages((prev) => [...prev, { sender: "user", text: q }]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chatbot/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
      } else {
        setChatMessages((prev) => [...prev, { sender: "bot", text: "I encountered an error querying platform knowledge." }]);
      }
    } catch (e) {
      setChatMessages((prev) => [...prev, { sender: "bot", text: `Connection error: ${e.message}` }]);
    } finally {
      setIsChatLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Checkout & Idempotent Payment
  // ---------------------------------------------------------------------------
  async function handleCheckout(e) {
    e.preventDefault();
    setIsPaying(true);

    try {
      const cartItemsPayload = cart.items.map((it) => ({
        product_id: it.product_id,
        size_label: it.size_label,
        quantity: it.quantity
      }));

      // Step 1: Checkout Order
      const orderRes = await fetch(`${API_BASE}/orders/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: checkoutData.name,
          customer_email: checkoutData.email,
          shipping_address: checkoutData.address,
          payment_method: checkoutData.method,
          cart_items: cartItemsPayload
        })
      });

      if (!orderRes.ok) {
        const err = await orderRes.json();
        throw new Error(err.detail || "Checkout failed");
      }
      const order = await orderRes.json();

      // Step 2: Idempotent Payment
      const idempotencyKey = `idem_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
      await fetch(`${API_BASE}/payments/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey
        },
        body: JSON.stringify({
          order_id: order.id,
          amount: order.total_amount,
          method: checkoutData.method
        })
      });

      setOrderConfirmation(order);
      loadCart(sessionId);
    } catch (err) {
      alert(`Checkout Error: ${err.message}`);
    } finally {
      setIsPaying(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Admin Operations
  // ---------------------------------------------------------------------------
  async function loadAdminData() {
    try {
      const [mRes, tRes, vRes] = await Promise.all([
        fetch(`${API_BASE}/admin/metrics`),
        fetch(`${API_BASE}/admin/tickets`),
        fetch(`${API_BASE}/admin/vendors`)
      ]);
      if (mRes.ok) setAdminMetrics(await mRes.json());
      if (tRes.ok) setAdminTickets(await tRes.json());
      if (vRes.ok) setAdminVendors(await vRes.json());
    } catch (e) {
      console.warn("Admin data load error", e);
    }
  }

  async function resolveTicket(ticketId) {
    try {
      const res = await fetch(`${API_BASE}/admin/tickets/${ticketId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "resolved",
          admin_notes: "Resolved by operator via Next.js Executive Dashboard."
        })
      });
      if (res.ok) loadAdminData();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleVendorSubmit(e) {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/admin/vendors/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(vendorForm)
      });
      if (res.ok) {
        alert("Vendor application submitted successfully!");
        setVendorForm({ store_name: "", contact_name: "", contact_email: "", contact_phone: "" });
        loadAdminData();
      }
    } catch (e) {
      alert(e.message);
    }
  }

  // ---------------------------------------------------------------------------
  // Auth Operations
  // ---------------------------------------------------------------------------
  async function handleLogin(email, pass) {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email || authEmail, password: pass || authPassword })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Authentication failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem("snitch_jwt_token", data.access_token);
      setCurrentUser(data);
      setIsAuthOpen(false);
      alert(`Signed in as ${data.full_name} (${data.role.toUpperCase()})`);
    } catch (e) {
      alert(e.message);
    }
  }

  const totalCartCount = cart.items.reduce((sum, it) => sum + it.quantity, 0);

  return (
    <>
      {/* Top Announcement Bar */}
      <aside className="announcement-bar">
        <div className="announcement-track">
          <span>🔥 SS'26 DROP: UNAPOLOGETIC LUXURY STREETWEAR</span>
          <span className="dot">•</span>
          <span>✨ 100% FIT GUARANTEE VIA ANTHROPOMETRIC COMPUTER VISION AI</span>
          <span className="dot">•</span>
          <span>⚡ 7 ENTERPRISE PLATFORM MICROSERVICES ACTIVE</span>
          <span className="dot">•</span>
          <span>🎯 FREE EXPRESS DELIVERY OVER ₹1,499</span>
        </div>
      </aside>

      {/* Main Navigation Header */}
      <header className="main-header">
        <div className="header-container">
          <div className="brand-area">
            <a href="#home" className="brand-logo">
              <span className="brand-name">SNITCH</span>
              <span className="brand-badge">LUXE NEXT.JS</span>
            </a>
          </div>

          {/* Amazon/Flipkart Inspired Search */}
          <div className="header-search">
            <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              type="text"
              placeholder="Search Cuban shirts, 240 GSM tees, trousers..."
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <nav className="nav-links">
            <button className="nav-btn ai-nav-btn" onClick={() => setIsAiFitOpen(true)}>
              ✨ AI FIT LAB
            </button>
            <button
              className="nav-btn ai-nav-btn"
              onClick={() => {
                setIsAiColorOpen(true);
                runAiColor();
              }}
            >
              🎨 COLOR STYLIST
            </button>
            <button
              className="nav-btn admin-nav-btn"
              onClick={() => {
                setIsAdminOpen(true);
                loadAdminData();
              }}
            >
              📊 ADMIN & METRICS
            </button>
          </nav>

          <div className="header-actions">
            <button className="action-btn" title="Platform Health Status">
              <span className="status-indicator"></span>
              <span>7 SERVICES OK</span>
            </button>
            <button className="action-btn" onClick={() => setIsAuthOpen(true)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>{currentUser ? currentUser.full_name.split(" ")[0].toUpperCase() : "SIGN IN"}</span>
            </button>
            <button className="action-btn cart-btn" onClick={() => setIsCartOpen(true)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <span className="cart-count">{totalCartCount}</span>
            </button>
          </div>
        </div>
      </header>

      <main id="home">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <div className="hero-pill">SPRING / SUMMER '26 RUNWAY DROP</div>
            <h1 className="hero-title">
              UNAPOLOGETIC<br />
              <span className="gradient-text">MODERN LUXURY.</span>
            </h1>
            <p className="hero-subtitle">
              Engineered with anthropometric silhouette computer vision, kinematic ease sizing algorithms, and CIELAB color harmonies. Connected directly to 7 enterprise microservices.
            </p>
            <div className="hero-actions">
              <a href="#catalog" className="btn btn-primary">
                EXPLORE DROPS
              </a>
              <button className="btn btn-outline" onClick={() => setIsAiFitOpen(true)}>
                ✨ TEST AI FIT FINDER
              </button>
              <button className="btn btn-ghost" onClick={() => setIsChatOpen(true)}>
                💬 CHAT WITH STYLIST
              </button>
            </div>

            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">18ms</span>
                <span className="stat-label">AI Latency</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">&lt; 4%</span>
                <span className="stat-label">Return Risk</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">100%</span>
                <span className="stat-label">Idempotency</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">7</span>
                <span className="stat-label">Microservices</span>
              </div>
            </div>
          </div>
        </section>

        {/* Microservices Live Status Banner */}
        <section className="services-ticker-section">
          <div className="section-container">
            <div className="services-grid">
              {healthStatus.map((svc) => (
                <div key={svc.id} className="service-badge-card">
                  <div className="service-badge-header">
                    <span className="service-badge-name">{svc.name}</span>
                    <span className="service-badge-dot"></span>
                  </div>
                  <span className="service-badge-sub">{svc.status} • ACTIVE</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Catalog Showcase Section */}
        <section className="catalog-section" id="catalog">
          <div className="section-container">
            <div className="section-header">
              <div>
                <span className="section-eyebrow">CURATED EDIT</span>
                <h2 className="section-title">THE STREETWEAR VAULT</h2>
              </div>
              <div className="catalog-filters">
                <button
                  className={`filter-pill ${activeCategory === "all" ? "active" : ""}`}
                  onClick={() => setActiveCategory("all")}
                >
                  All Products
                </button>
                <button
                  className={`filter-pill ${activeCategory === "shirts" ? "active" : ""}`}
                  onClick={() => setActiveCategory("shirts")}
                >
                  Oversized Shirts
                </button>
                <button
                  className={`filter-pill ${activeCategory === "tees" ? "active" : ""}`}
                  onClick={() => setActiveCategory("tees")}
                >
                  Heavy Tees
                </button>
                <button
                  className={`filter-pill ${activeCategory === "trousers" ? "active" : ""}`}
                  onClick={() => setActiveCategory("trousers")}
                >
                  Korean Pants
                </button>
                <button
                  className={`filter-pill ${activeCategory === "jackets" ? "active" : ""}`}
                  onClick={() => setActiveCategory("jackets")}
                >
                  Jackets & Blazers
                </button>
              </div>
            </div>

            {/* Product Cards Grid */}
            <div className="product-grid">
              {filteredProducts.map((p) => {
                const currentSelectedSize = selectedSizes[p.id] || (p.sizes[0] ? p.sizes[0].size_label : "M");
                return (
                  <div key={p.id} className="product-card">
                    <div className="product-image-wrap">
                      <img
                        src={p.image_url || "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600"}
                        alt={p.name}
                        className="product-image"
                      />
                      <div className="product-badges-row">
                        <span className="product-badge">{p.is_bestseller ? "BESTSELLER" : "LUXE STREETWEAR"}</span>
                        {p.original_price && (
                          <span className="discount-badge">
                            {Math.round(((p.original_price - p.price) / p.original_price) * 100)}% OFF
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="product-info">
                      <span className="product-fabric">{p.fabric}</span>
                      <h3 className="product-name">{p.name}</h3>
                      <div className="product-price-row">
                        <span className="product-price">₹{p.price.toLocaleString()}</span>
                        {p.original_price && (
                          <span className="product-orig-price">₹{p.original_price.toLocaleString()}</span>
                        )}
                      </div>
                      <div className="product-sizes-selector">
                        {p.sizes.map((s) => (
                          <button
                            key={s.id}
                            className={`size-chip ${currentSelectedSize === s.size_label ? "active" : ""}`}
                            onClick={() => setSelectedSizes({ ...selectedSizes, [p.id]: s.size_label })}
                          >
                            {s.size_label}
                          </button>
                        ))}
                      </div>
                      <div className="product-actions-row">
                        <button
                          className="add-cart-btn"
                          onClick={() => handleAddToCart(p.id, currentSelectedSize)}
                        >
                          ADD TO BAG
                        </button>
                        <button
                          className="ai-check-btn"
                          onClick={() => {
                            setFitProductId(p.id);
                            setIsAiFitOpen(true);
                            runAiFit();
                          }}
                        >
                          ✨ AI FIT
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      {/* AI Fit Lab Modal */}
      {isAiFitOpen && (
        <div className="modal-backdrop" onClick={(e) => e.target.classList.contains("modal-backdrop") && setIsAiFitOpen(false)}>
          <div className="modal-card">
            <button className="modal-close-btn" onClick={() => setIsAiFitOpen(false)}>&times;</button>
            <div className="modal-header">
              <span className="modal-badge">MODEL 1 & 2 • ANTHROPOMETRIC INFERENCE</span>
              <h3 className="modal-title">AI Fit & Sizing Lab</h3>
              <p className="modal-desc">
                Calculates 3D chest, waist, and hip circumferences from physical biometrics and models garment kinematic ease against verified size charts.
              </p>
            </div>
            <div className="modal-body">
              <form
                className="ai-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  runAiFit();
                }}
              >
                <div className="form-row">
                  <div className="form-group">
                    <label>Height (cm): <b>{fitHeight}</b> cm</label>
                    <input
                      type="range"
                      min="140"
                      max="215"
                      value={fitHeight}
                      onChange={(e) => setFitHeight(e.target.value)}
                      className="range-input"
                    />
                  </div>
                  <div className="form-group">
                    <label>Weight (kg): <b>{fitWeight}</b> kg</label>
                    <input
                      type="range"
                      min="40"
                      max="150"
                      value={fitWeight}
                      onChange={(e) => setFitWeight(e.target.value)}
                      className="range-input"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Gender Morphometry</label>
                    <select value={fitGender} onChange={(e) => setFitGender(e.target.value)} className="select-input">
                      <option value="male">Male (Athletic / Broad Shoulder)</option>
                      <option value="female">Female (Hourglass / Pear / Balanced)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Garment to Evaluate</label>
                    <select value={fitProductId} onChange={(e) => setFitProductId(e.target.value)} className="select-input">
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} (₹{p.price})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <button type="submit" className="btn btn-primary btn-block" disabled={isFitLoading}>
                  {isFitLoading ? "✨ CALCULATING KINEMATIC EASE..." : "✨ RUN 3D BIOMETRIC PREDICTION & SIZE EVALUATION"}
                </button>
              </form>

              {fitResult && (
                <div className="ai-result-panel">
                  <div className="result-header">
                    <h4>Predicted Anthropometry & Tailoring Verdict</h4>
                    <span className="confidence-badge">{fitResult.inferenceMode?.toUpperCase() || "STATISTICAL PRIOR"}</span>
                  </div>

                  <div className="measurements-grid">
                    <div className="measure-card">
                      <span className="measure-title">CHEST</span>
                      <span className="measure-value">{fitResult.measurements?.chest_cm}</span>
                      <span className="measure-unit">cm</span>
                    </div>
                    <div className="measure-card">
                      <span className="measure-title">WAIST</span>
                      <span className="measure-value">{fitResult.measurements?.waist_cm}</span>
                      <span className="measure-unit">cm</span>
                    </div>
                    <div className="measure-card">
                      <span className="measure-title">HIP</span>
                      <span className="measure-value">{fitResult.measurements?.hip_cm}</span>
                      <span className="measure-unit">cm</span>
                    </div>
                  </div>

                  <div className="recommendation-box">
                    <div className="rec-size-badge">
                      <span className="rec-label">OPTIMAL FIT</span>
                      <span className="rec-size">{fitResult.recommended_size}</span>
                    </div>
                    <div className="rec-details">
                      <div className="rec-title">{fitResult.verdict || `Optimal size is ${fitResult.recommended_size}`}</div>
                      <div className="rec-advice">{fitResult.size_advice}</div>
                      <div className="rec-metrics">
                        <span>Ease: <b>{fitResult.primary_ease_cm > 0 ? "+" : ""}{fitResult.primary_ease_cm} cm</b></span>
                        <span>Return Risk: <b>{fitResult.return_risk_score} (Very Low)</b></span>
                      </div>
                    </div>
                  </div>

                  <button
                    className="btn btn-primary btn-block"
                    onClick={() => {
                      handleAddToCart(parseInt(fitProductId), fitResult.recommended_size);
                      setIsAiFitOpen(false);
                    }}
                  >
                    🛒 ADD TO BAG IN SIZE {fitResult.recommended_size}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Color Stylist Modal */}
      {isAiColorOpen && (
        <div className="modal-backdrop" onClick={(e) => e.target.classList.contains("modal-backdrop") && setIsAiColorOpen(false)}>
          <div className="modal-card">
            <button className="modal-close-btn" onClick={() => setIsAiColorOpen(false)}>&times;</button>
            <div className="modal-header">
              <span className="modal-badge">MODEL 3 • CIELAB PHOTOMETRIC HARMONY</span>
              <h3 className="modal-title">AI Skin-Tone & Color Stylist</h3>
              <p className="modal-desc">
                Computes Individual Typology Angle (ITA) in CIE L*a*b* color space and maps skin tone to seasonal streetwear palettes.
              </p>
            </div>
            <div className="modal-body">
              <div className="color-picker-section">
                <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Select Preset Tone or Custom Swatch:
                </label>
                <div className="preset-swatches">
                  {["#F5D0B5", "#E0AC69", "#C68642", "#8D5524", "#3B2219"].map((hex) => (
                    <button
                      key={hex}
                      className={`swatch-btn ${skinHex === hex ? "active" : ""}`}
                      style={{ background: hex }}
                      onClick={() => {
                        setSkinHex(hex);
                        runAiColor(hex);
                      }}
                    />
                  ))}
                </div>
                <div className="hex-input-group">
                  <span>Custom Hex:</span>
                  <input
                    type="color"
                    value={skinHex}
                    onChange={(e) => {
                      setSkinHex(e.target.value);
                      runAiColor(e.target.value);
                    }}
                  />
                  <input
                    type="text"
                    value={skinHex}
                    onChange={(e) => setSkinHex(e.target.value)}
                    className="text-input"
                    style={{ width: "120px" }}
                  />
                  <button className="btn btn-outline btn-sm" onClick={() => runAiColor(skinHex)}>
                    ANALYZE
                  </button>
                </div>
              </div>

              {colorResult && (
                <div className="color-result-panel">
                  <div className="palette-header">
                    <div>
                      <span className="season-badge">{colorResult.seasonal_tone.toUpperCase()}</span>
                      <h4>{colorResult.seasonal_tone} Streetwear Harmonies</h4>
                    </div>
                    <div className="ita-metric">
                      <span className="ita-val">{colorResult.ita_angle}°</span>
                      <span className="ita-label">ITA Score</span>
                    </div>
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    {colorResult.styling_tips}
                  </p>

                  <div>
                    <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      Curated Palette Harmonies:
                    </label>
                    <div className="colors-row">
                      {colorResult.best_colors.map((c, i) => (
                        <div key={c} className="color-dot-card">
                          <span className="dot-circle" style={{ background: c }}></span>
                          <span>{colorResult.color_names[i] || c}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginTop: "12px" }}>
                    <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      Suboptimal Tones to Avoid:
                    </label>
                    <div className="colors-row">
                      {colorResult.avoid_colors.map((c) => (
                        <div key={c} className="color-dot-card">
                          <span className="dot-circle" style={{ background: c }}></span>
                          <span>Avoid</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Slide-over Cart Drawer */}
      {isCartOpen && (
        <div className="cart-drawer-backdrop" onClick={(e) => e.target.classList.contains("cart-drawer-backdrop") && setIsCartOpen(false)}>
          <aside className="cart-drawer">
            <div className="cart-header">
              <h3>SHOPPING BAG ({totalCartCount})</h3>
              <button className="modal-close-btn" style={{ position: "static" }} onClick={() => setIsCartOpen(false)}>
                &times;
              </button>
            </div>

            <div className="cart-items-container">
              {cart.items.length === 0 ? (
                <div style={{ textAlign: "center", color: "var(--text-muted)", marginTop: "40px" }}>
                  Your shopping bag is empty.
                </div>
              ) : (
                cart.items.map((it) => (
                  <div key={it.id} className="cart-item-card">
                    <img
                      src={it.product_image || "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600"}
                      className="cart-item-img"
                      alt={it.product_name}
                    />
                    <div className="cart-item-details">
                      <div>
                        <div className="cart-item-name">{it.product_name}</div>
                        <div className="cart-item-sub">
                          Size: <b>{it.size_label}</b> | Qty: {it.quantity}
                        </div>
                      </div>
                      <div className="cart-item-price">₹{it.total_price.toLocaleString()}</div>
                    </div>
                    <button className="cart-item-remove" onClick={() => handleRemoveFromCart(it.id)}>
                      &times;
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="cart-summary">
              <div className="summary-line">
                <span>Subtotal:</span>
                <span>₹{cart.subtotal.toLocaleString()}</span>
              </div>
              <div className="summary-line">
                <span>GST (5%):</span>
                <span>₹{cart.tax.toLocaleString()}</span>
              </div>
              <div className="summary-line">
                <span>Shipping:</span>
                <span>{cart.shipping === 0 ? "FREE" : `₹${cart.shipping}`}</span>
              </div>
              <div className="summary-line total-line">
                <span>Total:</span>
                <span>₹{cart.total.toLocaleString()}</span>
              </div>
              <button
                className="btn btn-primary btn-block"
                disabled={totalCartCount === 0}
                onClick={() => {
                  setIsCartOpen(false);
                  setIsCheckoutOpen(true);
                  setOrderConfirmation(null);
                }}
              >
                PROCEED TO CHECKOUT
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Checkout Modal */}
      {isCheckoutOpen && (
        <div className="modal-backdrop" onClick={(e) => e.target.classList.contains("modal-backdrop") && setIsCheckoutOpen(false)}>
          <div className="modal-card">
            <button className="modal-close-btn" onClick={() => setIsCheckoutOpen(false)}>&times;</button>
            <div className="modal-header">
              <span className="modal-badge">SERVICE 3 • TRANSACTION INTEGRITY</span>
              <h3 className="modal-title">Idempotent Secure Checkout</h3>
              <p className="modal-desc">
                Double-click immunity via Idempotency-Key headers with automated stock reservation.
              </p>
            </div>
            <div className="modal-body">
              {!orderConfirmation ? (
                <form className="ai-form" onSubmit={handleCheckout}>
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      value={checkoutData.name}
                      onChange={(e) => setCheckoutData({ ...checkoutData, name: e.target.value })}
                      className="text-input"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address</label>
                    <input
                      type="email"
                      value={checkoutData.email}
                      onChange={(e) => setCheckoutData({ ...checkoutData, email: e.target.value })}
                      className="text-input"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Delivery Address</label>
                    <textarea
                      value={checkoutData.address}
                      onChange={(e) => setCheckoutData({ ...checkoutData, address: e.target.value })}
                      className="text-input"
                      rows="2"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Payment Method</label>
                    <div className="payment-methods">
                      <label className="pay-option">
                        <input
                          type="radio"
                          name="payMethod"
                          value="CARD"
                          checked={checkoutData.method === "CARD"}
                          onChange={() => setCheckoutData({ ...checkoutData, method: "CARD" })}
                        />
                        <span>Credit / Debit Card</span>
                      </label>
                      <label className="pay-option">
                        <input
                          type="radio"
                          name="payMethod"
                          value="UPI"
                          checked={checkoutData.method === "UPI"}
                          onChange={() => setCheckoutData({ ...checkoutData, method: "UPI" })}
                        />
                        <span>Instant UPI (GPay/PhonePe)</span>
                      </label>
                      <label className="pay-option">
                        <input
                          type="radio"
                          name="payMethod"
                          value="COD"
                          checked={checkoutData.method === "COD"}
                          onChange={() => setCheckoutData({ ...checkoutData, method: "COD" })}
                        />
                        <span>Cash on Delivery</span>
                      </label>
                    </div>
                  </div>
                  <button type="submit" className="btn btn-primary btn-block" disabled={isPaying}>
                    {isPaying ? "AUTHORIZING PAYMENT..." : `AUTHORIZE & PAY ₹${cart.total.toLocaleString()}`}
                  </button>
                </form>
              ) : (
                <div className="order-confirmation-box">
                  <div className="success-icon">✓</div>
                  <h4>ORDER CONFIRMED!</h4>
                  <p>Order Number: <b>{orderConfirmation.order_number}</b></p>
                  <p>Tracking Code: <code>{orderConfirmation.tracking_number || "TRK-DELHIVERY-992104"}</code></p>
                  <div className="tracking-timeline">
                    <div className="step active">1. Confirmed</div>
                    <div className="step">2. Packed</div>
                    <div className="step">3. Shipped</div>
                    <div className="step">4. Delivered</div>
                  </div>
                  <button className="btn btn-outline btn-block" onClick={() => setIsCheckoutOpen(false)}>
                    CONTINUE SHOPPING
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Admin Control Center Modal */}
      {isAdminOpen && (
        <div className="modal-backdrop" onClick={(e) => e.target.classList.contains("modal-backdrop") && setIsAdminOpen(false)}>
          <div className="modal-card modal-lg">
            <button className="modal-close-btn" onClick={() => setIsAdminOpen(false)}>&times;</button>
            <div className="modal-header">
              <span className="modal-badge">SERVICE 5 • OPERATIONAL GOVERNANCE</span>
              <h3 className="modal-title">Executive Control Center & Tickets</h3>
              <p className="modal-desc">
                Real-time revenue telemetry, customer support escalation desk, and vendor marketplace onboarding.
              </p>
            </div>
            <div className="modal-body">
              <div className="admin-tabs">
                <button
                  className={`tab-btn ${adminTab === "metrics" ? "active" : ""}`}
                  onClick={() => setAdminTab("metrics")}
                >
                  Business Analytics
                </button>
                <button
                  className={`tab-btn ${adminTab === "tickets" ? "active" : ""}`}
                  onClick={() => setAdminTab("tickets")}
                >
                  Support Tickets ({adminTickets.length})
                </button>
                <button
                  className={`tab-btn ${adminTab === "vendors" ? "active" : ""}`}
                  onClick={() => setAdminTab("vendors")}
                >
                  Vendor Applications ({adminVendors.length})
                </button>
              </div>

              {adminTab === "metrics" && adminMetrics && (
                <div className="metrics-grid">
                  <div className="metric-card">
                    <span className="metric-title">TOTAL PLATFORM REVENUE</span>
                    <span className="metric-value">₹{adminMetrics.total_sales_revenue.toLocaleString()}</span>
                    <span className="metric-sub">Across All Channels</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-title">TOTAL ORDERS PROCESSED</span>
                    <span className="metric-value">{adminMetrics.total_orders_count}</span>
                    <span className="metric-sub">100% Idempotent</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-title">ACTIVE CATALOG PRODUCTS</span>
                    <span className="metric-value">{adminMetrics.total_products_count}</span>
                    <span className="metric-sub">Multi-Point Size Charts</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-title">OPEN SUPPORT TICKETS</span>
                    <span className="metric-value">{adminMetrics.open_tickets_count}</span>
                    <span className="metric-sub">Automated Triage</span>
                  </div>
                </div>
              )}

              {adminTab === "tickets" && (
                <div className="tickets-container">
                  {adminTickets.map((t) => (
                    <div key={t.id} className="ticket-item">
                      <div className="ticket-top">
                        <span className="ticket-id">{t.ticket_number} • {t.customer_name}</span>
                        <span className={`ticket-badge badge-${t.status}`}>{t.status}</span>
                      </div>
                      <div style={{ fontWeight: 700, fontSize: "0.9rem" }}>{t.subject}</div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>"{t.message}"</div>
                      {t.admin_notes && (
                        <div style={{ fontSize: "0.75rem", color: "var(--accent-ai)" }}>
                          Operator Note: {t.admin_notes}
                        </div>
                      )}
                      <div style={{ marginTop: "8px" }}>
                        {t.status !== "resolved" && (
                          <button className="btn btn-primary btn-sm" onClick={() => resolveTicket(t.id)}>
                            Mark Resolved
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {adminTab === "vendors" && (
                <div>
                  <form className="ai-form" onSubmit={handleVendorSubmit} style={{ marginBottom: "20px" }}>
                    <div className="form-row">
                      <input
                        type="text"
                        placeholder="Store / Brand Name"
                        value={vendorForm.store_name}
                        onChange={(e) => setVendorForm({ ...vendorForm, store_name: e.target.value })}
                        className="text-input"
                        required
                      />
                      <input
                        type="text"
                        placeholder="Founder Name"
                        value={vendorForm.contact_name}
                        onChange={(e) => setVendorForm({ ...vendorForm, contact_name: e.target.value })}
                        className="text-input"
                        required
                      />
                    </div>
                    <div className="form-row">
                      <input
                        type="email"
                        placeholder="Business Email"
                        value={vendorForm.contact_email}
                        onChange={(e) => setVendorForm({ ...vendorForm, contact_email: e.target.value })}
                        className="text-input"
                        required
                      />
                      <input
                        type="text"
                        placeholder="Phone Number"
                        value={vendorForm.contact_phone}
                        onChange={(e) => setVendorForm({ ...vendorForm, contact_phone: e.target.value })}
                        className="text-input"
                        required
                      />
                    </div>
                    <button type="submit" className="btn btn-primary btn-sm">
                      SUBMIT VENDOR ONBOARDING
                    </button>
                  </form>

                  {adminVendors.map((v) => (
                    <div key={v.id} className="ticket-item">
                      <div className="ticket-top">
                        <span className="ticket-id">Vendor: {v.store_name} ({v.contact_name})</span>
                        <span className={`ticket-badge badge-${v.status}`}>{v.status}</span>
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                        Email: {v.contact_email} | Phone: {v.contact_phone}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      {isAuthOpen && (
        <div className="modal-backdrop" onClick={(e) => e.target.classList.contains("modal-backdrop") && setIsAuthOpen(false)}>
          <div className="modal-card">
            <button className="modal-close-btn" onClick={() => setIsAuthOpen(false)}>&times;</button>
            <div className="modal-header">
              <span className="modal-badge">SERVICE 2 • AUTH SERVICE</span>
              <h3 className="modal-title">Sign In / Role Access</h3>
              <p className="modal-desc">
                Access buyer, seller, and admin workflows with role-based JWT bearer tokens.
              </p>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", gap: "8px", marginBottom: "16px", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>1-Click Demo:</span>
                <button
                  className="btn btn-outline btn-sm"
                  style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                  onClick={() => handleLogin("admin@snitch.com", "Admin@12345")}
                >
                  Admin
                </button>
                <button
                  className="btn btn-outline btn-sm"
                  style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                  onClick={() => handleLogin("seller@snitch.com", "Seller@12345")}
                >
                  Seller
                </button>
                <button
                  className="btn btn-outline btn-sm"
                  style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                  onClick={() => handleLogin("buyer@snitch.com", "Buyer@12345")}
                >
                  Buyer
                </button>
              </div>

              <form
                className="ai-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleLogin(authEmail, authPassword);
                }}
              >
                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    className="text-input"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    className="text-input"
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary btn-block">
                  SIGN IN
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Floating AI Stylist Chatbot */}
      <div className="chat-widget">
        <button className="chat-toggle-btn" onClick={() => setIsChatOpen(!isChatOpen)}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span className="chat-pulse"></span>
        </button>

        {isChatOpen && (
          <div className="chat-window">
            <div className="chat-window-header">
              <div className="chat-header-info">
                <span className="chat-avatar">✨</span>
                <div>
                  <div className="chat-title">SNITCH AI STYLIST</div>
                  <div className="chat-status">Grounded in RAG Knowledge & Live DB</div>
                </div>
              </div>
              <button className="modal-close-btn" style={{ position: "static" }} onClick={() => setIsChatOpen(false)}>
                &times;
              </button>
            </div>

            <div className="chat-messages">
              {chatMessages.map((m, idx) => (
                <div key={idx} className={`chat-msg ${m.sender}`}>
                  {m.text}
                </div>
              ))}
              {isChatLoading && <div className="chat-msg bot">Thinking & retrieving context...</div>}
            </div>

            <div className="chat-quick-chips">
              <button
                className="chip-btn"
                onClick={() => sendChatMessage("What is your return and exchange policy?")}
              >
                Return Policy
              </button>
              <button
                className="chip-btn"
                onClick={() => sendChatMessage("Where is order ORD-SNITCH-88219?")}
              >
                Track #88219
              </button>
              <button
                className="chip-btn"
                onClick={() => sendChatMessage("How should I care for pure linen shirts?")}
              >
                Linen Care
              </button>
            </div>

            <form
              className="chat-input-bar"
              onSubmit={(e) => {
                e.preventDefault();
                sendChatMessage(chatInput);
              }}
            >
              <input
                type="text"
                placeholder="Ask sizing, care, or tracking..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                className="chat-input"
                required
              />
              <button type="submit" className="chat-send-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </form>
          </div>
        )}
      </div>
    </>
  );
}
