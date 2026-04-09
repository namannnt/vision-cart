"use client";

import { useState, useEffect } from "react";
import { Camera, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function RegistrationPage() {
  const [formData, setFormData] = useState({ name: "", price: "", stock: "", parentId: "" });
  const [isCylindrical, setIsCylindrical] = useState(false);
  const [requireCoin, setRequireCoin] = useState(false);
  const [status, setStatus] = useState<"idle" | "capturing" | "success" | "error" | "partial">("idle");
  const [message, setMessage] = useState("");
  const [captureStep, setCaptureStep] = useState(1);
  const [streamKey, setStreamKey] = useState(0);

  useEffect(() => {
    setStreamKey(Date.now());
    const t = setInterval(() => setStreamKey(Date.now()), 30000);
    return () => clearInterval(t);
  }, []);

  const handleReset = () => {
    setStatus("idle"); setMessage(""); setCaptureStep(1);
    setFormData({ name: "", price: "", stock: "", parentId: "" });
    setRequireCoin(false);
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.name || !formData.price || !formData.stock) return;
    setStatus("capturing");
    setMessage(isCylindrical ? `Capturing angle ${captureStep} of 3...` : "Analyzing product...");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: formData.name, price: parseFloat(formData.price),
          stock: parseInt(formData.stock), is_cylindrical: isCylindrical,
          capture_step: captureStep, parent_id: formData.parentId.trim(),
          require_coin: requireCoin,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        if (data.status === "partial") {
          setStatus("partial"); setMessage(data.message); setCaptureStep(captureStep + 1);
        } else if (data.status === "success") {
          setStatus("success"); setMessage(`Registered: ${formData.name}`);
          setFormData({ name: "", price: "", stock: "", parentId: "" }); setIsCylindrical(false); setCaptureStep(1);
          setTimeout(() => { setStatus("idle"); setMessage(""); }, 5000);
        } else { setStatus("error"); setMessage(data.error || "Registration failed."); }
      } else { setStatus("error"); setMessage(data.error || "Server error."); }
    } catch { setStatus("error"); setMessage("Cannot connect to AI server. Is it running?"); }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}>
        <div className="flex items-center gap-4 mb-2">
          <div className="h-px flex-1" style={{ background: "linear-gradient(90deg, rgba(184,160,144,0.5), transparent)" }} />
          <span className="text-xs font-bold tracking-[0.3em] uppercase text-dust">Registration</span>
        </div>
        <h1 className="text-4xl font-black tracking-tighter text-gold">Add Product</h1>
        <p className="mt-1 text-sm text-dust">Place the item under the camera and fill in the details.</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── Camera feed ── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.7 }}
          className="relative overflow-hidden rounded-2xl flex flex-col panel-glow">

          {/* Top horizon */}
          <div className="horizon" />

          {/* Header bar */}
          <div className="flex items-center justify-between px-5 py-3 flex-shrink-0"
            style={{ borderBottom: "1px solid rgba(194,140,60,0.08)", background: "rgba(194,140,60,0.03)" }}>
            <div className="flex items-center gap-2">
              <Camera className="h-4 w-4 text-amber" />
              <span className="font-semibold text-sm" style={{ color: "#e8dcc8" }}>Live Camera</span>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={() => setStreamKey(Date.now())}
                className="p-1.5 rounded-lg transition-all text-dust hover:text-star"
                style={{ border: "1px solid rgba(194,140,60,0.1)" }}>
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full"
                style={{ background: "rgba(143,188,143,0.08)", border: "1px solid rgba(143,188,143,0.2)" }}>
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: "#8fbc8f" }} />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5" style={{ background: "#8fbc8f" }} />
                </span>
                <span className="text-xs font-semibold" style={{ color: "#8fbc8f" }}>LIVE</span>
              </div>
            </div>
          </div>

          {/* Feed */}
          <div className="relative flex-1 min-h-[320px] bg-black">
            {/* Corner accents */}
            {[
              "top-0 left-0 border-t-2 border-l-2 rounded-tl-none",
              "top-0 right-0 border-t-2 border-r-2 rounded-tr-none",
              "bottom-0 left-0 border-b-2 border-l-2 rounded-bl-none",
              "bottom-0 right-0 border-b-2 border-r-2 rounded-br-none",
            ].map((cls, i) => (
              <div key={i} className={`absolute w-6 h-6 z-10 pointer-events-none ${cls}`}
                style={{ borderColor: "rgba(194,140,60,0.4)" }} />
            ))}

            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img key={streamKey} src={`http://127.0.0.1:8000/video_feed?t=${streamKey}`}
              alt="Camera Feed" className="w-full h-full object-cover"
              onError={() => { setTimeout(() => setStreamKey(Date.now()), 3000); }} />

            <AnimatePresence>
              {status === "capturing" && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="absolute inset-0 flex flex-col items-center justify-center"
                  style={{ background: "rgba(5,3,1,0.75)", backdropFilter: "blur(4px)" }}>
                  {/* Scanning animation */}
                  <div className="relative mb-5">
                    <motion.div className="w-20 h-20 rounded-full"
                      style={{ border: "2px solid rgba(194,140,60,0.3)" }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }} />
                    <motion.div className="absolute inset-2 rounded-full"
                      style={{ border: "1px solid rgba(194,140,60,0.5)" }}
                      animate={{ rotate: -360 }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }} />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 className="h-8 w-8 text-amber animate-spin" />
                    </div>
                  </div>
                  <p className="font-bold text-star text-sm">Analyzing...</p>
                  {isCylindrical && (
                    <p className="text-xs text-dust mt-1">Angle {captureStep} of 3</p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Scan line overlay */}
            {status !== "capturing" && (
              <motion.div className="absolute inset-x-0 h-px pointer-events-none"
                style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.4), transparent)" }}
                animate={{ top: ["0%", "100%"] }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }} />
            )}
          </div>

          <div className="horizon" />
        </motion.div>

        {/* ── Form ── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.7 }}
          className="rounded-2xl p-6 panel-glow">

          <div className="horizon mb-6" />

          <form onSubmit={handleRegister} className="space-y-5">

            {/* Product name */}
            <div className="space-y-2">
              <label className="text-xs font-bold tracking-widest uppercase text-dust">Product Name</label>
              <input type="text" value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. vaseline 20gm"
                disabled={status === "capturing"}
                className="w-full rounded-xl px-4 py-3 text-sm placeholder:text-stone-800 focus:outline-none transition-all duration-300 disabled:opacity-50"
                style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(194,140,60,0.1)", color: "#e8dcc8" }}
                onFocus={e => { e.target.style.borderColor = "rgba(194,140,60,0.4)"; e.target.style.boxShadow = "0 0 20px rgba(194,140,60,0.08)"; }}
                onBlur={e => { e.target.style.borderColor = "rgba(194,140,60,0.1)"; e.target.style.boxShadow = "none"; }}
                required />
            </div>

            {/* Parent Group (optional) */}
            <div className="space-y-2">
              <label className="text-xs font-bold tracking-widest uppercase text-dust">
                Parent Group <span style={{ color: "#5a4a38", fontWeight: "normal" }}>(optional — for size variants)</span>
              </label>
              <input type="text" value={formData.parentId}
                onChange={e => setFormData({ ...formData, parentId: e.target.value })}
                placeholder="e.g. vaseline  (same for 20gm & 50gm)"
                disabled={status === "capturing"}
                className="w-full rounded-xl px-4 py-3 text-sm placeholder:text-stone-800 focus:outline-none transition-all duration-300 disabled:opacity-50"
                style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(126,184,201,0.15)", color: "#e8dcc8" }}
                onFocus={e => { e.target.style.borderColor = "rgba(126,184,201,0.4)"; e.target.style.boxShadow = "0 0 20px rgba(126,184,201,0.08)"; }}
                onBlur={e => { e.target.style.borderColor = "rgba(126,184,201,0.15)"; e.target.style.boxShadow = "none"; }} />
            </div>

            {/* Price + Stock */}
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Price (₹)", key: "price" as const, type: "number", min: "0", step: "0.5", placeholder: "0.00" },
                { label: "Stock",     key: "stock" as const, type: "number", min: "1", step: "1",   placeholder: "10"   },
              ].map(({ label, key, ...rest }) => (
                <div key={key} className="space-y-2">
                  <label className="text-xs font-bold tracking-widest uppercase text-dust">{label}</label>
                  <input {...rest} value={formData[key]}
                    onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                    disabled={status === "capturing"}
                    className="w-full rounded-xl px-4 py-3 text-sm placeholder:text-stone-800 focus:outline-none transition-all duration-300 disabled:opacity-50"
                    style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(194,140,60,0.1)", color: "#e8dcc8" }}
                    onFocus={e => { e.target.style.borderColor = "rgba(194,140,60,0.4)"; e.target.style.boxShadow = "0 0 20px rgba(194,140,60,0.08)"; }}
                    onBlur={e => { e.target.style.borderColor = "rgba(194,140,60,0.1)"; e.target.style.boxShadow = "none"; }}
                    required />
                </div>
              ))}
            </div>

            {/* Multi-angle toggle */}
            <label className="flex items-start gap-3 cursor-pointer p-4 rounded-xl transition-all duration-200"
              style={{ background: "rgba(255,255,255,0.01)", border: `1px solid ${isCylindrical ? "rgba(194,140,60,0.25)" : "rgba(194,140,60,0.08)"}` }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.2)"}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = isCylindrical ? "rgba(194,140,60,0.25)" : "rgba(194,140,60,0.08)"}>
              <div className="relative mt-0.5 flex-shrink-0">
                <input type="checkbox" checked={isCylindrical}
                  onChange={e => { setIsCylindrical(e.target.checked); setCaptureStep(1); }}
                  disabled={status === "capturing"}
                  className="sr-only" />
                <div className="w-10 h-5 rounded-full transition-all duration-300"
                  style={{ background: isCylindrical ? "linear-gradient(135deg, #8b5e1a, #c28c3c)" : "rgba(255,255,255,0.05)", border: `1px solid ${isCylindrical ? "rgba(194,140,60,0.5)" : "rgba(194,140,60,0.1)"}` }}>
                  <motion.div className="w-3.5 h-3.5 rounded-full mt-0.5"
                    style={{ background: isCylindrical ? "#f5e6c0" : "#3a2e22", boxShadow: isCylindrical ? "0 0 8px rgba(194,140,60,0.6)" : "none" }}
                    animate={{ x: isCylindrical ? 18 : 2 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }} />
                </div>
              </div>
              <div>
                <p className="font-semibold text-sm" style={{ color: isCylindrical ? "#e8dcc8" : "#5a4a38" }}>
                  Multi-Angle Capture (3 Photos)
                </p>
                <p className="text-xs mt-0.5 text-dust">For bottles, cans, or cylindrical products</p>
              </div>
            </label>

            {/* Coin size toggle */}
            <label className="flex items-start gap-3 cursor-pointer p-4 rounded-xl transition-all duration-200"
              style={{ background: "rgba(255,255,255,0.01)", border: `1px solid ${requireCoin ? "rgba(126,184,201,0.3)" : "rgba(126,184,201,0.08)"}` }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(126,184,201,0.2)"}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = requireCoin ? "rgba(126,184,201,0.3)" : "rgba(126,184,201,0.08)"}>
              <div className="relative mt-0.5 flex-shrink-0">
                <input type="checkbox" checked={requireCoin}
                  onChange={e => setRequireCoin(e.target.checked)}
                  disabled={status === "capturing"}
                  className="sr-only" />
                <div className="w-10 h-5 rounded-full transition-all duration-300"
                  style={{ background: requireCoin ? "linear-gradient(135deg, #2a5a6a, #7eb8c9)" : "rgba(255,255,255,0.05)", border: `1px solid ${requireCoin ? "rgba(126,184,201,0.5)" : "rgba(126,184,201,0.1)"}` }}>
                  <motion.div className="w-3.5 h-3.5 rounded-full mt-0.5"
                    style={{ background: requireCoin ? "#e0f4ff" : "#3a2e22", boxShadow: requireCoin ? "0 0 8px rgba(126,184,201,0.6)" : "none" }}
                    animate={{ x: requireCoin ? 18 : 2 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }} />
                </div>
              </div>
              <div>
                <p className="font-semibold text-sm" style={{ color: requireCoin ? "#7eb8c9" : "#5a4a38" }}>
                  Require Coin for Size Measurement
                </p>
                <p className="text-xs mt-0.5 text-dust">Place ₹1 coin in frame — REQUIRED for size variants (20gm vs 50gm)</p>
              </div>
            </label>

            {/* Step indicator */}
            <AnimatePresence>
              {isCylindrical && (status === "partial" || status === "capturing") && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
                  className="flex items-center justify-center gap-3">
                  {[1, 2, 3].map(step => (
                    <div key={step} className="flex items-center gap-3">
                      <motion.div className="flex items-center justify-center h-9 w-9 rounded-full text-sm font-black transition-all"
                        style={{
                          background: captureStep > step ? "linear-gradient(135deg, #3d6030, #8fbc8f)" : captureStep === step ? "linear-gradient(135deg, #6b4010, #c28c3c)" : "rgba(255,255,255,0.03)",
                          border: `1px solid ${captureStep > step ? "rgba(143,188,143,0.4)" : captureStep === step ? "rgba(194,140,60,0.5)" : "rgba(194,140,60,0.08)"}`,
                          color: captureStep >= step ? "#f0e6d0" : "#3a2e22",
                          boxShadow: captureStep === step ? "0 0 20px rgba(194,140,60,0.3)" : "none",
                        }}
                        animate={captureStep === step ? { scale: [1, 1.08, 1] } : {}}
                        transition={{ duration: 1.5, repeat: Infinity }}>
                        {captureStep > step ? "✓" : step}
                      </motion.div>
                      {step < 3 && <div className="w-8 h-px" style={{ background: captureStep > step ? "rgba(143,188,143,0.4)" : "rgba(194,140,60,0.1)" }} />}
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit button */}
            <motion.button type="submit"
              disabled={status === "capturing" || !formData.name}
              whileHover={status !== "capturing" && formData.name ? { scale: 1.02, translateY: -2 } : {}}
              whileTap={status !== "capturing" ? { scale: 0.98 } : {}}
              className="relative w-full flex items-center justify-center gap-2.5 rounded-xl py-4 font-black overflow-hidden disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: status === "success"
                  ? "linear-gradient(135deg, #2a5020, #8fbc8f)"
                  : "linear-gradient(135deg, #4a2808, #8a6018, #c28c3c, #8a6018, #4a2808)",
                color: "#f5e6c0",
                border: `1px solid ${status === "success" ? "rgba(143,188,143,0.3)" : "rgba(194,140,60,0.25)"}`,
                boxShadow: status === "success"
                  ? "0 0 30px rgba(143,188,143,0.2)"
                  : "0 0 40px rgba(194,140,60,0.2), 0 8px 25px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,220,150,0.1)",
                animation: status !== "capturing" && status !== "success" ? "gold-flow 4s linear infinite" : "none",
              }}>
              <div className="absolute inset-0 shimmer-btn pointer-events-none" />
              {status === "capturing" ? (
                <><Loader2 className="h-5 w-5 animate-spin relative z-10" /><span className="relative z-10">Processing...</span></>
              ) : status === "success" ? (
                <><CheckCircle2 className="h-5 w-5 relative z-10" /><span className="relative z-10">Registered!</span></>
              ) : (
                <><Camera className="h-5 w-5 relative z-10" /><span className="relative z-10">{isCylindrical ? `Capture Angle ${captureStep} / 3` : "Capture & Register"}</span></>
              )}
            </motion.button>

            {status === "partial" && (
              <button type="button" onClick={handleReset}
                className="w-full text-center text-xs transition-colors text-dust hover:text-ember">
                Cancel Registration
              </button>
            )}

            {/* Status message */}
            <AnimatePresence>
              {message && (
                <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="p-4 rounded-xl text-sm"
                  style={{
                    background: status === "error" ? "rgba(200,112,96,0.08)" : status === "success" ? "rgba(143,188,143,0.08)" : "rgba(194,140,60,0.08)",
                    border: `1px solid ${status === "error" ? "rgba(200,112,96,0.2)" : status === "success" ? "rgba(143,188,143,0.2)" : "rgba(194,140,60,0.2)"}`,
                    color: status === "error" ? "#c87060" : status === "success" ? "#8fbc8f" : "#c28c3c",
                  }}>
                  {message}
                </motion.div>
              )}
            </AnimatePresence>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
 