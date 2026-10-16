# MASTER FRONTEND ARCHITECTURAL FLOW & ENGINEERING SYSTEM GUIDE

**Classification:** Enterprise Next.js 16 (React 19) Luxury Fast-Fashion E-Commerce Architecture  
**Author:** Senior Principal UI/UX & Web Systems Architect (15+ Years Experience)  
**Standard Compliance:** Antigravity UI Designer Standard (`antigravity-ui-designer`)  
**Design Reference:** Klickpin Luxury Puffer Showcase (Pin ID: 1093671090781192414)  
**Target Repository Directory:** `frontend/`  
**API Gateway Target:** `http://127.0.0.1:8000/api/v1`  
**Updated:** 2026-10-16T23:15:00+05:30  

---

## 1. Executive System Architecture Overview

The `frontend/` application is an enterprise-grade, high-performance web application built with **Next.js 16 App Router**, **React 19**, and **Tailwind CSS 3.4**. It transforms conventional apparel browsing into an interactive, 3D animated fitting room by replicating the luxury floating viewport and dynamic color space mechanics of the Klickpin outfit video while seamlessly integrating three proprietary AI microservice engines:
1. **Fat & Body Morphology Biometric Lab** (Ramanujan ellipse circumference regression & silhouette depth synthesis).
2. **Photometric Skin Tone & Seasonal Harmonizer** (CIELAB ITA angle and Monk Scale classification).
3. **Conversational AI Stylist HUD** (RAG knowledge retrieval for apparel care, sizing, and live order tracking).

```
====================================================================================================
                               NEXT.JS FRONTEND ARCHITECTURAL TOPOLOGY
====================================================================================================
                                    
                                    [ Root Layout: layout.js ]
                               (Outfit, Syne, Space Grotesk Fonts)
                                                |
                                                v
                                 [ Master Client Orchestrator ]
                                       (src/app/page.js)
                                                |
        +---------------------------------------+---------------------------------------+
        |                                       |                                       |
        v                                       v                                       v
[ Global Navigation ]               [ Interactive Hero Stage ]             [ Curated Apparel Catalog ]
  • AnnouncementBar.jsx               • HeroOutfitStage.jsx                  • ProductGrid.jsx
  • Navbar.jsx                          - Ambient Gradient Mesh                • ProductCard.jsx
  • Footer.jsx                          - Floating 3D Garment (Float Physics)  • Search & Filters
                                        - Dual-Thumbnail Morphing Dynamics
                                        - Size Selector & Live Pricing
                                                |
        +---------------------------------------+---------------------------------------+
        |                                       |                                       |
        v                                       v                                       v
[ AI Modal Ecosystem ]              [ Commerce Operations ]                [ Executive Suite ]
  • AiFitModal.jsx                    • CartDrawer.jsx                       • AdminDashboardModal.jsx
  • AiColorStylistModal.jsx           • CheckoutModal.jsx (Idempotency Key)  • AuthModal.jsx
  • AiChatbotDrawer.jsx               • OrderConfirmation.jsx                • Toast.jsx
        |                                       |                                       |
        +---------------------------------------+---------------------------------------+
                                                |
                                                v
                                  [ Custom Hooks & State ]
                     • useCardTilt.js  • useCart.js  • useAiFit.js
                     • useAiColor.js   • useChatbot.js
                                                |
                                                v
                                   [ Unified API Client ]
                                      (src/lib/api.js)
                     (Automatic Offline Resilience & Fallback Simulator)
                                                |
                                                v (REST / HTTP CORS)
====================================================================================================
                       FASTAPI MICROSERVICES GATEWAY (PORT 8000 / API V1)
====================================================================================================
```

---

## 2. Directory Structure & Complete File Responsibility Matrix

The application follows a modular, developer-understandable folder structure. Every folder, file, and export has an isolated, single responsibility.

```
frontend/
├── CHANGELOG.md                         # Detailed timestamped log of all changes and impact rationale
├── FRONTEND_ARCHITECTURE_FLOW.md        # [This File] Master architectural blueprint and developer guide
├── package.json                         # Next.js 16, React 19, Tailwind CSS, Lucide icons dependencies
├── package-lock.json                    # Deterministic dependency lock
├── tailwind.config.js                   # Custom Obsidian theme, cyber accents, shadows, and keyframes
├── postcss.config.mjs                   # PostCSS plugins (tailwindcss, autoprefixer)
├── next.config.mjs                      # Turbopack options, caching, and remote image domain rules
├── jsconfig.json                        # Path aliases (@/* mapping to ./src/*)
├── eslint.config.mjs                    # ESLint 9 configuration
│
├── public/                              # Static public assets
│   ├── outfits/                         # High-resolution 3D garment renders extracted and generated
│   │   ├── puffer_amber.jpg             # Sunset Amber Gloss Puffer (Look 0)
│   │   ├── puffer_charcoal.jpg          # Obsidian Matte Stealth Puffer (Look 1)
│   │   ├── puffer_silver.jpg            # Arctic Frost Liquid Silver Puffer (Look 2)
│   │   └── puffer_ruby.jpg              # Neon Cyber Ruby Puffer (Look 3)
│   ├── favicon.ico                      # Brand favicon
│   └── *.svg                            # Vector logos and icons
│
└── src/
    ├── app/
    │   ├── layout.js                    # HTML root layout, Google Fonts injection (Outfit/Inter/Syne), SEO
    │   ├── page.js                      # Root client orchestrator: connects state hooks to components
    │   └── globals.css                  # Tailwind directives, CSS variables, keyframe animations, glassmorphism
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Navbar.jsx               # Floating glass pill header, live search, 7-service status, demo auth
    │   │   ├── AnnouncementBar.jsx      # Continuous marquee ticker for SS'26 drops and platform guarantees
    │   │   └── Footer.jsx               # Luxury streetwear footer, atelier standards, technology suite links
    │   │
    │   ├── hero/
    │   │   └── HeroOutfitStage.jsx      # SIGNATURE SHOWCASE (From Video):
    │   │                                # - Ambient dynamic radial gradient backdrop
    │   │                                # - Floating luxury rounded viewport canvas
    │   │                                # - Top pill navigation (PUFFER JACKET, ALL PRODUCTS, ABOUT, CONTACT)
    │   │                                # - Chevron controls (< >) with counter
    │   │                                # - Floating 3D Garment with breathing float animation
    │   │                                # - Dynamic ground elliptical shadow
    │   │                                # - Top-left previous outfit thumbnail
    │   │                                # - Bottom-right next outfit preview thumbnail
    │   │                                # - Circular size pills (36, 38, 40, 42) with AI highlight
    │   │                                # - Strikethrough pricing & currency switch ($ USD / ₹ INR)
    │   │                                # - Direct "Get the look >" and "✨ 3D AI Fit" CTAs
    │   │
    │   ├── catalog/
    │   │   ├── ProductGrid.jsx          # Department switcher (All/Men/Women), category pills, responsive grid
    │   │   └── ProductCard.jsx          # 3D mouse tilt physics, holographic sheen reflection, instant bag add
    │   │
    │   ├── ai/
    │   │   ├── AiFitModal.jsx           # Fat & Body Morphology Biometrics Studio:
    │   │   │                            # - Single photo contour segmentation / manual biometrics
    │   │   │                            # - Height (cm), Weight (kg), Body Fat % (Slim/Athletic/Robust/Curvy)
    │   │   │                            # - Ramanujan ellipse chest/waist/hip circumference regression
    │   │   │                            # - Return risk score and recommended shirt/pant sizing
    │   │   │
    │   │   ├── AiColorStylistModal.jsx  # Skin Tone Color Harmony Studio:
    │   │   │                            # - Selfie facial ROI photo upload or Monk Scale hex swatches
    │   │   │                            # - CIELAB Individual Typology Angle (ITA) classification
    │   │   │                            # - Seasonal palette (Warm Autumn, Cool Summer, Bold Winter, Spring)
    │   │   │                            # - "Illuminate Look" action that triggers hero stage look switch
    │   │   │
    │   │   └── AiChatbotDrawer.jsx      # AI Stylist HUD Drawer:
    │   │                                # - Floating slide-over assistant with real-time markdown answers
    │   │                                # - Suggestion chips for sizing, care, returns, order tracking
    │   │                                # - RAG platform query integration
    │   │
    │   ├── commerce/
    │   │   ├── CartDrawer.jsx           # Slide-over shopping bag, free delivery meter, subtotal/tax/shipping
    │   │   ├── CheckoutModal.jsx        # Idempotent anti-duplicate checkout, UUIDv4 key, UPI/Card/COD
    │   │   └── OrderConfirmation.jsx    # Order receipt, tracking code, dispatch estimation
    │   │
    │   ├── admin/
    │   │   └── AdminDashboardModal.jsx  # Executive telemetry, microservice health daemons, ticket resolver
    │   │
    │   ├── auth/
    │   │   └── AuthModal.jsx            # One-click demo personas (Shopper, Vendor, Admin) and login
    │   │
    │   └── common/
    │       └── Toast.jsx                # Floating luxury notification pill with glowing indicator
    │
    ├── hooks/
    │   ├── useCardTilt.js               # 3D perspective mouse-tracking tilt physics with radial glare sheen
    │   ├── useCart.js                   # Shopping bag state, optimistic updates, session persistence
    │   ├── useAiFit.js                  # Biometric body morphology regression and garment ease evaluation
    │   ├── useAiColor.js                # Photometric skin tone extraction and seasonal color matching
    │   └── useChatbot.js                # AI Stylist conversation history and RAG query lifecycle
    │
    └── lib/
        ├── api.js                       # Microservices Gateway REST client with fallback simulations
        ├── outfitData.js                # Curated outfit dataset with video animation specs and gradients
        ├── constants.js                 # App constants, mock catalog, sizes, departments, and API endpoints
        └── utils.js                     # Currency formatters, Ramanujan perimeter math, and CIELAB helpers
```

---

## 3. Function & File Operational Specification

### 3.1. `src/hooks/useCardTilt.js`
- **Function:** `useCardTilt(maxRotation = 8)`
- **Behavior:** Attaches mousemove and mouseleave listeners to DOM card surfaces. Calculates normalized offsets from the card center:
  $$\text{rotateX} = \frac{y - \text{centerY}}{\text{centerY}} \times -\text{maxRotation}$$
  $$\text{rotateY} = \frac{x - \text{centerX}}{\text{centerX}} \times \text{maxRotation}$$
- **Hologram Glare:** Moves a radial gradient light reflection across `.hologram-sheen` following mouse coordinates. On mouseleave, smoothly resets to identity via CSS transitions.

### 3.2. `src/components/hero/HeroOutfitStage.jsx`
- **Function:** `HeroOutfitStage(props)`
- **Animation Engine:**
  1. **Ambient Background Shift:** When `activeLookIndex` changes, the parent section updates `style.background = currentLook.ambientGradient` with a 1000ms transition.
  2. **Jacket Hover Physics:** The central jacket executes `@keyframes float` ($y$: -14px to +0px, rotate: 1deg) over a 5s cubic loop.
  3. **Elliptical Shadow Pulse:** A black radial blur below the jacket executes `@keyframes pulseGlow`, scaling down to 0.9 when the jacket rises, creating true physical depth.
  4. **Dual-Thumbnail Transitions:**
     - **Top-Left (Previous Look):** Renders `OUTFIT_LOOKS[(currentIndex - 1 + length) % length]`. Clicking it cycles backwards.
     - **Bottom-Right (Next Look):** Renders `OUTFIT_LOOKS[(currentIndex + 1) % length]`. Clicking it triggers the forward animation.
     - **State Locking:** `isTransitioning` locks user input for 600ms, transforms the outgoing garment upward/downward (`scale(0.75)` + translation), swaps the data at 280ms, and settles the incoming garment.

### 3.3. `src/hooks/useAiFit.js` & `src/components/ai/AiFitModal.jsx`
- **Function:** `runFitAnalysis()`
- **Morphometrics Mode:**
  - In **Manual Mode**, reads `heightCm`, `weightKg`, `gender`, and `bodyFatCategory` ("slim", "athletic", "robust", "curvy").
  - In **Photo Scan Mode**, converts uploaded front and side photos into base64 data payloads for 2D silhouette boundary segmentation.
- **Ease Evaluation:** Queries `/ai-fit/predict-measurements` and `/ai-fit/evaluate-garment-fit`. In fallback mode, evaluates Ramanujan elliptical cross-sections:
  $$\text{Perimeter} \approx \pi (a + b) \left(1 + \frac{3h}{10 + \sqrt{4 - 3h}}\right), \quad h = \frac{(a-b)^2}{(a+b)^2}$$
- **Return Value:** Computes exact chest/waist/hip circumferences, recommended shirt size (e.g. 38/M), recommended pant waist (e.g. 32"), and return risk percentage.

### 3.4. `src/hooks/useAiColor.js` & `src/components/ai/AiColorStylistModal.jsx`
- **Function:** `runColorAnalysis(hex, photo, gender)`
- **Behavior:** Samples facial skin pixels or takes a preset Monk Scale swatch. Calculates CIELAB luminance $L^*$ and undertone ($R$ vs $B$ delta). Classifies seasonal quadrant:
  - Warm undertone + high luminance $\rightarrow$ Warm Spring
  - Warm undertone + deep luminance $\rightarrow$ Deep Autumn
  - Cool undertone + high luminance $\rightarrow$ Cool Summer
  - Cool undertone + deep luminance $\rightarrow$ Bold Winter
- **Hero Synchronization:** Calling "Illuminate Look" triggers `onApplyLookToStage(matchingOutfitIndex)`, causing the hero stage to immediately rotate to the user's best matching look!

### 3.5. `src/lib/api.js`
- **Behavior:** Wraps all fetch requests with `cache: "no-store"` for real-time reactivity.
- **Degraded Fallback Resilience:** If the FastAPI backend is offline or unbooted, every method catches network errors and gracefully resolves with local deterministic data. The UI never crashes, never throws unhandled promise rejections, and displays clean telemetry indicators.

---

## 4. How to Start the Frontend Application

### 4.1. Prerequisites
- **Node.js:** v18.17.0+ or v20+ (Node v22 / v23 tested)
- **Package Manager:** `npm` (included with Node.js)
- **Port Availability:** Default port `3000`

### 4.2. Development Mode
Run the development server with Turbopack acceleration:
```bash
cd c:\Users\ADMIN\Downloads\E-Commerce-2026-main\frontend
npm run dev
```
- Open your browser at: `http://localhost:3000`
- The dev server supports Fast Refresh and instant hot module replacement.

### 4.3. Production Build Validation
To validate production compilation and tree-shaking:
```bash
cd c:\Users\ADMIN\Downloads\E-Commerce-2026-main\frontend
npm run build
npm run start
```
- Output verifies: `Route (app) / (Static) prerendered as static content` with 0 compilation errors.

---

## 5. Architectural Guarantees & "What Happens If You Don't Do This"

| Architecture Decision | What Happens If You DON'T Do This? (Consequences & Failure Modes) |
|---|---|
| **Decoupled API Client (`lib/api.js`) with Fallback Simulator** | If the backend gateway on port 8000 is stopped or rebuilding, direct `fetch()` calls crash the React component lifecycle with unhandled `TypeError: Failed to fetch`. The user is met with a white screen of death. Our architecture guarantees a 100% resilient UI with simulated data. |
| **Component Modularization (Separate Hero, AI, Catalog, Commerce)** | Placing 2,500 lines of state and JSX in a single `page.js` file destroys React reconciliation performance, causes unnecessary re-renders of the entire DOM tree on every keystroke, makes unit testing impossible, and creates high-risk merge conflicts. |
| **Hardware-Accelerated CSS Transforms (`perspective`, `translate3d`)** | Applying card tilt via `top`/`left` or non-transform CSS triggers browser layout reflows and paint repainting on every mouse move frame (60Hz/120Hz), causing severe frame drops and jank. Using `transform: perspective() rotateX() rotateY()` offloads computation directly to the GPU. |
| **Dual-Thumbnail State Locking (`isTransitioning`)** | Rapidly clicking `<` or `>` without transition debouncing causes race conditions where image elements unmount midway through CSS keyframe animations, leading to visual flickering, broken spring states, and mismatched index counters. |
| **Idempotency Keys (`Idempotency-Key: idem_...`)** | If a customer clicks "PAY & CONFIRM" twice due to network latency, standard REST endpoints process duplicate charges, resulting in duplicate credit card transactions, chargebacks, and angry users. The unique UUIDv4 token ensures the backend deduplicates requests. |
| **Next.js Image Domain Configuration (`next.config.mjs`)** | Next.js 16 enforces strict security on remote image URLs. Omitting `images.remotePatterns` crashes the runtime with `Invalid src prop on next/image`, breaking the catalog grid completely. |
