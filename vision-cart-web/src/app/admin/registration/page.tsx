"use client";

import { useState, useEffect } from "react";
import { Camera, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export default function RegistrationPage() {
  const [formData, setFormData] = useState({ name: "", price: "", stock: "" });
  const [isCylindrical, setIsCylindrical] = useState(false);
  const [status, setStatus] = useState<"idle" | "capturing" | "success" | "error" | "partial">("idle");
  const [message, setMessage] = useState("");
  const [captureStep, setCaptureStep] = useState(1);
  const [streamKey, setStreamKey] = useState(Date.now());

  // Auto-refresh stream every 30s to prevent stale black feed
  useEffect(() => {
    const t = setInterval(() => setStreamKey(Date.now()), 30000);
    return () => clearInterval(t);
  }, []);

  const handleReset = () => {
    setStatus("idle");
    setMessage("");
    setCaptureStep(1);
    setFormData({ name: "", price: "", stock: "" });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.price || !formData.stock) return;

    setStatus("capturing");
    setMessage(isCylindrical 
      ? `Capturing side ${captureStep} of 3...`
      : "Capturing reference image from camera and processing AI embeddings...");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: formData.name,
          price: parseFloat(formData.price),
          stock: parseInt(formData.stock),
          is_cylindrical: isCylindrical,
          capture_step: captureStep
        }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.status === "partial") {
          setStatus("partial");
          setMessage(data.message);
          setCaptureStep(captureStep + 1);
        } else if (data.status === "success") {
          setStatus("success");
          setMessage(`Successfully registered: ${formData.name}`);
          setFormData({ name: "", price: "", stock: "" });
          setIsCylindrical(false);
          setCaptureStep(1);
          setTimeout(() => {
            setStatus("idle");
            setMessage("");
          }, 5000);
        } else {
          setStatus("error");
          setMessage(data.error || "Failed to register product.");
        }
      } else {
        setStatus("error");
        setMessage(data.error || "Server error.");
      }
    } catch (err) {
      setStatus("error");
      setMessage("Could not connect to the Python ML server. Is it running?");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Register New Product</h1>
        <p className="text-slate-400 mt-1">Place the item clearly under the camera and fill in its details.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Camera Preview */}
        <div className="glass-card overflow-hidden flex flex-col ring-1 ring-white/10 hover:ring-blue-500/30 transition-all duration-700 shadow-[0_0_40px_-15px_rgba(59,130,246,0.2)] hover:shadow-[0_0_60px_-15px_rgba(59,130,246,0.4)] group">
          <div className="bg-slate-900/60 px-4 py-3 border-b border-slate-800 flex justify-between items-center">
            <span className="font-semibold text-slate-200">Live Camera Feed</span>
            <div className="flex items-center gap-3">
              <button onClick={() => setStreamKey(Date.now())} className="text-slate-500 hover:text-slate-300 transition-colors" title="Refresh feed">
                <RefreshCw className="h-4 w-4" />
              </button>
              <div className="flex items-center space-x-2 text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full border border-emerald-500/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>LIVE</span>
              </div>
            </div>
          </div>
          <div className="relative aspect-video bg-black flex-1 min-h-[300px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              key={streamKey}
              src={`http://127.0.0.1:8000/video_feed?t=${streamKey}`}
              alt="Live Camera Feed"
              className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-[1.02]"
              onError={(e) => {
                setTimeout(() => setStreamKey(Date.now()), 3000);
              }}
            />
            {status === "capturing" && (
              <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-8 text-center">
                <div className="flex flex-col items-center">
                  <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
                  <p className="text-xl font-medium text-white shadow-sm drop-shadow-md">
                    {isCylindrical ? "Analyzing multiple sides..." : "Analyzing product shape..."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Registration Form */}
        <div className="glass-card p-6">
          <form onSubmit={handleRegister} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Product Name (ID)</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Lay's Classic"
                className="w-full rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
                disabled={status === "capturing"}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Price (₹)</label>
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  placeholder="0.00"
                  className="w-full rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3 text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                  disabled={status === "capturing"}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Initial Stock</label>
                <input
                  type="number"
                  min="1"
                  value={formData.stock}
                  onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                  placeholder="10"
                  className="w-full rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3 text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                  disabled={status === "capturing"}
                />
              </div>
            </div>

            <div className="pt-2">
              <label className="flex items-center space-x-3 cursor-pointer p-3 rounded-xl border border-slate-700 bg-slate-800/30 hover:bg-slate-800/50 transition-colors">
                <input
                  type="checkbox"
                  checked={isCylindrical}
                  onChange={(e) => {
                    setIsCylindrical(e.target.checked);
                    setCaptureStep(1);
                  }}
                  disabled={status === "capturing"}
                  className="h-5 w-5 rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-0 disabled:opacity-50"
                />
                <div className="flex flex-col">
                  <p className="font-medium text-slate-200">Multi-Angle Capture (3 Photos)</p>
                  <p className="text-sm text-slate-400 mt-1">
                    Enable for cylindrical or complex products. Captures 3 photos from different angles for better recognition accuracy.
                  </p>
                </div>
              </label>
            </div>

            <div className="pt-2">
              <motion.button
                whileHover={{ scale: 1.02, boxShadow: "0px 0px 20px rgba(59, 130, 246, 0.4)" }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={status === "capturing" || !formData.name}
                className={`flex w-full items-center justify-center space-x-2 rounded-xl px-4 py-3 font-semibold text-white shadow-lg transition-all outline-none border-none 
                  ${status === "success" ? "bg-emerald-600 shadow-emerald-500/25 cursor-default" : 
                    "bg-gradient-to-r from-blue-600 to-purple-600 shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed"}`}
              >
                {status === "capturing" ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Processing AI Embeddings...</span>
                  </>
                ) : status === "success" ? (
                  <>
                    <CheckCircle2 className="h-5 w-5" />
                    <span>Registration Complete!</span>
                  </>
                ) : (
                  <>
                    <Camera className="h-5 w-5" />
                    <span>{isCylindrical ? `Capture Photo ${captureStep} of 3` : "Capture & Register Product"}</span>
                  </>
                )}
              </motion.button>
            </div>

            {isCylindrical && (status === "partial" || status === "capturing") && (
              <div className="flex items-center justify-center space-x-2 mt-2">
                {[1, 2, 3].map((step) => (
                  <div key={step} className={`flex items-center justify-center h-8 w-8 rounded-full text-sm font-bold border-2 transition-all
                    ${captureStep > step ? "bg-emerald-500 border-emerald-500 text-white" :
                      captureStep === step ? "bg-blue-500 border-blue-500 text-white animate-pulse" :
                      "bg-slate-800 border-slate-600 text-slate-400"}`}>
                    {captureStep > step ? "✓" : step}
                  </div>
                ))}
                <span className="text-sm text-slate-400 ml-2">Photo {Math.min(captureStep, 3)} of 3</span>
              </div>
            )}

            {status === "partial" && (
              <button
                type="button"
                onClick={handleReset}
                className="mt-3 w-full text-center text-xs font-semibold text-slate-500 hover:text-red-400 transition-colors"
              >
                Cancel Registration
              </button>
            )}

            {/* Status Messages */}
            {message && (
              <div className={`mt-4 p-4 rounded-xl border text-sm ${
                status === "error" ? "bg-red-500/10 border-red-500/20 text-red-400" :
                status === "success" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" :
                "bg-blue-500/10 border-blue-500/20 text-blue-400"
              }`}>
                {message}
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
