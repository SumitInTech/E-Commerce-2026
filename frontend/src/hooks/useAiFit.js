"use client";

import { useState, useCallback } from "react";
import { api } from "../lib/api";

export function useAiFit(showToast) {
  const [isOpen, setIsOpen] = useState(false);
  const [tab, setTab] = useState("manual"); // "manual" | "scan"
  const [heightCm, setHeightCm] = useState(178.0);
  const [weightKg, setWeightKg] = useState(75.0);
  const [bodyFatCategory, setBodyFatCategory] = useState("athletic"); // "slim" | "athletic" | "robust" | "curvy"
  const [gender, setGender] = useState("male");
  const [productId, setProductId] = useState(1);
  const [frontPhoto, setFrontPhoto] = useState(null);
  const [sidePhoto, setSidePhoto] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [detectedNotice, setDetectedNotice] = useState(null);

  const runFitAnalysis = useCallback(async () => {
    setIsLoading(true);
    try {
      const payload = {
        height_cm: parseFloat(heightCm),
        weight_kg: parseFloat(weightKg),
        gender: gender,
      };

      const isImageMode = tab === "scan" && !!frontPhoto;
      if (isImageMode) {
        payload.front_photo_base64 = frontPhoto;
        if (sidePhoto) payload.side_photo_base64 = sidePhoto;
      }

      // Step 1: Biometric measurements regression
      const m1 = await api.predictMeasurements(payload);

      if (m1.detected_gender && m1.detected_gender !== gender) {
        setGender(m1.detected_gender);
        setDetectedNotice(
          m1.detected_gender === "female"
            ? "Auto-detected Female Curvature Profile"
            : "Auto-detected Male Athletic V-Taper Profile"
        );
      }

      // Step 2: Garment kinematic ease evaluation
      const m2 = await api.evaluateGarmentFit({
        chest_cm: m1.predictions.chest_cm,
        waist_cm: m1.predictions.waist_cm,
        hip_cm: m1.predictions.hip_cm,
        product_id: parseInt(productId),
      });

      const finalResult = {
        ...m1,
        ...m2,
        measurements: m1.predictions,
        recommended_size: m2.recommended_size || m1.recommended_shirt_size || "38",
        recommended_pant_size: m1.recommended_pant_size || "32",
        body_morphology: m1.body_morphology,
        gender_morphology_label: m1.gender_morphology_label,
        inferenceMode: isImageMode
          ? "Computer Vision Contour Segmentation (Single-Photo Silhouette Depth Synthesis)"
          : `Precision Anthropometric Statistical Prior (${heightCm}cm, ${weightKg}kg, ${gender.toUpperCase()})`,
      };

      setResult(finalResult);

      if (showToast) {
        showToast(
          isImageMode
            ? "✨ AI Fit Sizing computed via Computer Vision Silhouette!"
            : "✨ AI Sizing computed via Anthropometric Biometrics!"
        );
      }
    } catch (e) {
      if (showToast) showToast(`AI Fit Engine Error: ${e.message}`, "error");
    } finally {
      setIsLoading(false);
    }
  }, [tab, heightCm, weightKg, gender, frontPhoto, sidePhoto, productId, showToast]);

  const handlePhotoUpload = useCallback((file, setter) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setter(reader.result);
    reader.readAsDataURL(file);
  }, []);

  return {
    isOpen,
    setIsOpen,
    tab,
    setTab,
    heightCm,
    setHeightCm,
    weightKg,
    setWeightKg,
    bodyFatCategory,
    setBodyFatCategory,
    gender,
    setGender,
    productId,
    setProductId,
    frontPhoto,
    setFrontPhoto: (file) => handlePhotoUpload(file, setFrontPhoto),
    sidePhoto,
    setSidePhoto: (file) => handlePhotoUpload(file, setSidePhoto),
    isLoading,
    result,
    detectedNotice,
    runFitAnalysis,
    resetPhoto: () => {
      setFrontPhoto(null);
      setSidePhoto(null);
    },
  };
}
