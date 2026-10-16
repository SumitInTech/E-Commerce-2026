"use client";

import { useState, useCallback } from "react";
import { api } from "../lib/api";
import { analyzeSkinHex, getSeasonalPalette } from "../lib/utils";

export function useAiColor(showToast, onOutfitMatch) {
  const [isOpen, setIsOpen] = useState(false);
  const [skinHex, setSkinHex] = useState("#E0AC69");
  const [selfiePhoto, setSelfiePhoto] = useState(null);
  const [colorGender, setColorGender] = useState("male");
  const [colorResult, setColorResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const runColorAnalysis = useCallback(
    async (hexOverride, photoOverride, genderOverride) => {
      setIsLoading(true);
      try {
        const activeHex = hexOverride || skinHex;
        const activePhoto = photoOverride !== undefined ? photoOverride : selfiePhoto;
        const activeGender = genderOverride !== undefined ? genderOverride : colorGender;

        const payload = activePhoto
          ? { image_base64: activePhoto, gender: activeGender }
          : { hex_color: activeHex, gender: activeGender };

        const data = await api.analyzeColorPalette(payload);

        // Calculate client-side seasonal classification and target outfit match
        const localAnalysis = analyzeSkinHex(data.detected_skin_hex || activeHex);
        const seasonal = getSeasonalPalette(localAnalysis.undertone, localAnalysis.lum);

        const enriched = {
          ...data,
          localAnalysis,
          seasonal,
          matchingOutfitIndex: seasonal.matchingOutfitIndex,
        };

        setColorResult(enriched);
        if (data.detected_skin_hex) setSkinHex(data.detected_skin_hex);

        if (onOutfitMatch && typeof seasonal.matchingOutfitIndex === "number") {
          onOutfitMatch(seasonal.matchingOutfitIndex);
        }

        if (showToast) {
          showToast(`✨ Photometric Skin Harmonization: Matched with ${seasonal.season}!`);
        }
      } catch (e) {
        if (showToast) showToast(`Skin Tone Engine Error: ${e.message}`, "error");
      } finally {
        setIsLoading(false);
      }
    },
    [skinHex, selfiePhoto, colorGender, showToast, onOutfitMatch]
  );

  const handleSelfieUpload = useCallback(
    (file) => {
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result;
        setSelfiePhoto(dataUrl);
        runColorAnalysis(null, dataUrl, colorGender);
      };
      reader.readAsDataURL(file);
    },
    [colorGender, runColorAnalysis]
  );

  return {
    isOpen,
    setIsOpen,
    skinHex,
    setSkinHex: (hex) => {
      setSkinHex(hex);
      runColorAnalysis(hex, null, colorGender);
    },
    selfiePhoto,
    handleSelfieUpload,
    colorGender,
    setColorGender,
    colorResult,
    isLoading,
    runColorAnalysis,
  };
}
