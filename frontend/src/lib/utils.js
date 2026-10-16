/**
 * Utility functions for formatting, math, and color science
 */

export function formatInr(amount) {
  if (typeof amount !== "number") return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatUsd(amount) {
  if (typeof amount !== "number") return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Ramanujan's Second Approximation for Ellipse Perimeter (Anthropometric Cross-Section)
 * Used to cross-validate chest/waist circumference from 2D orthogonal camera silhouettes.
 */
export function ramanujanPerimeter(majorA, minorB) {
  const h = Math.pow(majorA - minorB, 2) / Math.pow(majorA + minorB, 2);
  return Math.PI * (majorA + minorB) * (1 + (3 * h) / (10 + Math.sqrt(4 - 3 * h)));
}

/**
 * Approximate Skin Tone undertone & category from Hex code
 */
export function analyzeSkinHex(hex) {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);

  // Luminance
  const lum = 0.299 * r + 0.587 * g + 0.114 * b;

  // Undertone detection (R vs B balance)
  let undertone = "Warm";
  if (r - b < 30) undertone = "Cool";
  else if (Math.abs(r - g - (g - b)) < 15) undertone = "Neutral";

  // Category
  let category = "Wheatish / Warm Medium";
  if (lum > 200) category = "Fair Porcelain";
  else if (lum > 165) category = "Light Sand / Peach";
  else if (lum > 130) category = "Wheatish Golden";
  else if (lum > 95) category = "Deep Warm Bronze";
  else category = "Rich Deep Ebony";

  return { r, g, b, lum, undertone, category };
}

/**
 * Classify seasonal palette based on undertone and luminance
 */
export function getSeasonalPalette(undertone, lum) {
  if (undertone === "Warm") {
    return lum > 140
      ? { season: "Warm Spring", vibe: "Vivid, energetic, golden undertones", matchingOutfitIndex: 0 }
      : { season: "Deep Autumn", vibe: "Earthy, rich, amber & burnished bronze", matchingOutfitIndex: 0 };
  } else if (undertone === "Cool") {
    return lum > 140
      ? { season: "Cool Summer", vibe: "Delicate, soft platinum, silver glacier", matchingOutfitIndex: 2 }
      : { season: "Bold Winter", vibe: "High-contrast, pure obsidian, ruby scarlet", matchingOutfitIndex: 1 };
  } else {
    return lum > 130
      ? { season: "Neutral Radiant", vibe: "Balanced versatility, looks radiant in all drops", matchingOutfitIndex: 3 }
      : { season: "Deep Universal", vibe: "Dramatic high contrast, obsidian and crimson", matchingOutfitIndex: 1 };
  }
}
