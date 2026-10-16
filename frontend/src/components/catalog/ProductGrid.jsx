"use client";

import { useState, useMemo } from "react";
import ProductCard from "./ProductCard";
import { WARDROBE_DEPARTMENTS, GARMENT_CATEGORIES } from "../../lib/constants";

export default function ProductGrid({
  products = [],
  searchQuery = "",
  onAddToCart,
  onOpenAiFit,
  aiRecommendedSize,
}) {
  const [activeDepartment, setActiveDepartment] = useState("all");
  const [activeCategory, setActiveCategory] = useState("all");

  const filteredProducts = useMemo(() => {
    let list = products;

    // 1. Department Filter
    if (activeDepartment === "men") {
      list = list.filter((p) => {
        const name = p.name.toLowerCase();
        return !name.includes("corset") && !name.includes("bodysuit");
      });
    } else if (activeDepartment === "women") {
      list = list.filter((p) => {
        const name = p.name.toLowerCase();
        return (
          name.includes("corset") ||
          name.includes("fluid") ||
          name.includes("bodysuit") ||
          name.includes("puffer") ||
          name.includes("linen")
        );
      });
    }

    // 2. Category Filter
    if (activeCategory !== "all") {
      const catMap = {
        jackets: "jacket",
        shirts: "shirt",
        tees: "t_shirt",
        trousers: "pants",
      };
      const target = catMap[activeCategory];
      if (target) {
        list = list.filter((p) => p.garment_type === target);
      }
    }

    // 3. Search Query Filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.fabric?.toLowerCase().includes(q) ||
          p.description?.toLowerCase().includes(q)
      );
    }

    return list;
  }, [products, activeDepartment, activeCategory, searchQuery]);

  return (
    <section id="catalog" className="w-full max-w-7xl mx-auto px-4 md:px-8 py-16">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 pb-6 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyber-cyan tracking-widest uppercase mb-2">
            <span>SS'26 DROP MATRIX</span>
            <span>//</span>
            <span>{filteredProducts.length} APPARELS READY</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-black text-white font-heading tracking-tight">
            Curated Urban Runway
          </h2>
          <p className="text-sm text-white/50 mt-1 max-w-md">
            Engineered with high-tensile fabrics, structured drop-shoulders, and thermal down chambers.
          </p>
        </div>

        {/* Department Switcher Pills */}
        <div className="flex items-center bg-obsidian-900 border border-white/10 rounded-full p-1 self-start md:self-auto">
          {WARDROBE_DEPARTMENTS.map((dept) => (
            <button
              key={dept.id}
              onClick={() => setActiveDepartment(dept.id)}
              className={`px-4 py-2 rounded-full text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeDepartment === dept.id
                  ? "bg-white text-black shadow-lg"
                  : "text-white/60 hover:text-white"
              }`}
            >
              <span>{dept.icon}</span>
              <span>{dept.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Category Pills Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-8 scrollbar-none">
        {GARMENT_CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 rounded-full text-xs font-medium whitespace-nowrap transition-all border ${
              activeCategory === cat.id
                ? "bg-cyber-cyan/15 border-cyber-cyan text-cyber-cyan shadow-[0_0_15px_rgba(0,240,255,0.25)]"
                : "bg-obsidian-900/60 border-white/10 text-white/70 hover:border-white/20 hover:text-white"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Product Cards Grid */}
      {filteredProducts.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-white/10 rounded-3xl bg-obsidian-950/40">
          <div className="text-3xl mb-3">🔍</div>
          <p className="text-white font-bold text-base">No garments match your filters</p>
          <p className="text-white/40 text-xs mt-1">Try resetting the search query or category filters</p>
          <button
            onClick={() => {
              setActiveDepartment("all");
              setActiveCategory("all");
            }}
            className="mt-4 px-4 py-2 rounded-full bg-white/10 hover:bg-white text-white hover:text-black text-xs font-bold transition-all"
          >
            Reset All Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
              onOpenAiFit={onOpenAiFit}
              aiRecommendedSize={aiRecommendedSize}
            />
          ))}
        </div>
      )}
    </section>
  );
}
