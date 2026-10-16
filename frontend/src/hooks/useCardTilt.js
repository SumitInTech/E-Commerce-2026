"use client";

import { useCallback } from "react";

/**
 * High-performance 3D perspective tilt physics with radial light sheen
 * As specified in the Antigravity UI Designer Skill.
 */
export function useCardTilt(maxRotation = 8) {
  const handleMouseMove = useCallback((e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -maxRotation;
    const rotateY = ((x - centerX) / centerX) * maxRotation;

    card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;

    const sheen = card.querySelector(".hologram-sheen");
    if (sheen) {
      sheen.style.opacity = "1";
      sheen.style.background = `radial-gradient(circle at ${(x / rect.width) * 100}% ${(y / rect.height) * 100}%, rgba(0, 240, 255, 0.28) 0%, rgba(212, 175, 55, 0.15) 35%, transparent 70%)`;
    }
  }, [maxRotation]);

  const handleMouseLeave = useCallback((e) => {
    const card = e.currentTarget;
    card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
    const sheen = card.querySelector(".hologram-sheen");
    if (sheen) sheen.style.opacity = "0";
  }, []);

  return { handleMouseMove, handleMouseLeave };
}
