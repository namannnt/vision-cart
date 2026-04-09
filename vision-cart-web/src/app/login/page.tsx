"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from "framer-motion";
import { ShieldCheck, ShoppingCart, Eye, EyeOff } from "lucide-react";
import dynamic from "next/dynamic";

const WormholeCanvas = dynamic(() => import("@/components/WormholeCanvas"), { ssr: false });

const CREDENTIALS = { admin: "admin123", staff: "staff123" };

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"admin" | "staff" | null>(null);
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const mx = useMotionValue(0); const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 50, damping: 15 });
  const sy = useSpring(my, { stiffness: 50, damping: 15 });
  const rx = useTransform(sy, [-300, 300], [12, -12]);
  const ry = useTransform(sx, [-300, 300], [-12, 12]);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!role) return;
    if (password !== CREDENTIALS[role]) {
      setError("Incorrect access code.");
      return;
    }
    setLoading(true);
    setError("");
    await new Promise(r => setTimeout(r, 800));
    router.push(role === "admin" ? "/admin" : "/billing");
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center p-4 overflow-hidden"
      style={{ background: "#030201" }}>

      {/* ── Full canvas wormhole ── */}
      <WormholeCanvas />

      {/* ── Vignette overlay ── */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 1,
        background: "radial-gradient(ellipse 70% 70% at 50% 50%, transparent 30%, rgba(2,1,0,0.6) 100%)" }} />

      {/* ── Floating data particles ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 1 }}>
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div key={i}
            className="absolute text-xs font-mono"
            style={{
              left: `${5 + (i * 4.7) % 90}%`,
              color: `rgba(194,140,60,${0.08 + (i % 5) * 0.04})`,
              fontSize: "10px",
            }}
            initial={{ y: "110vh", opacity: 0 }}
            animate={{ y: "-10vh", opacity: [0, 0.6, 0.6, 0] }}
            transition={{
              duration: 8 + (i % 5) * 3,
              delay: i * 0.8,
              repeat: Infinity,
              ease: "linear",
            }}>
            {["01001", "10110", "SCAN", "₹₹₹", "ITEM", "0xFF", "CART", "AI"][i % 8]}
          </motion.div>
        ))}
      </div>

      {/* ── Main card ── */}
      <motion.div ref={cardRef}
        onMouseMove={e => {
          const r = cardRef.current?.getBoundingClientRect();
          if (!r) return;
          mx.set(e.clientX - r.left - r.width / 2);
          my.set(e.clientY - r.top - r.height / 2);
        }}
        onMouseLeave={() => { mx.set(0); my.set(0); }}
        style={{ rotateX: rx, rotateY: ry, transformStyle: "preserve-3d", perspective: 1400, zIndex: 10 }}
        initial={{ opacity: 0, y: 100, scale: 0.8 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 1.4, ease: [0.23, 1, 0.32, 1] }}
        className="relative w-full max-w-[440px]">

        {/* Outer pulsing halo */}
        <motion.div className="absolute -inset-8 rounded-full pointer-events-none"
          style={{ background: "radial-gradient(ellipse, rgba(194,140,60,0.08) 0%, transparent 70%)", filter: "blur(30px)" }}
          animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }} />

        {/* Rotating border gradient */}
        <motion.div className="absolute -inset-[1px] rounded-2xl pointer-events-none overflow-hidden"
          style={{ zIndex: -1 }}>
          <motion.div className="absolute inset-0"
            style={{
              background: "conic-gradient(from 0deg, rgba(194,140,60,0.8), rgba(255,220,140,0.4), rgba(194,140,60,0.1), rgba(255,248,230,0.6), rgba(194,140,60,0.8))",
              borderRadius: "1rem",
            }}
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 6, repeat: Infinity, ease: "linear" }} />
        </motion.div>

        {/* Card */}
        <div className="relative rounded-2xl overflow-hidden"
          style={{
            background: "linear-gradient(160deg, rgba(22,15,6,0.97) 0%, rgba(14,9,3,0.98) 50%, rgba(8,5,2,0.99) 100%)",
            border: "1px solid rgba(194,140,60,0.08)",
            boxShadow: "0 60px 140px rgba(0,0,0,0.98), 0 0 120px rgba(194,140,60,0.05), inset 0 1px 0 rgba(255,220,150,0.04)",
            transform: "translateZ(40px)",
          }}>

          {/* Animated top horizon */}
          <motion.div className="h-px w-full"
            style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.3), rgba(255,248,230,0.8), rgba(194,140,60,0.3), transparent)" }}
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 3, repeat: Infinity }} />

          {/* Inner shimmer sweep */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
            <motion.div className="absolute inset-y-0 w-2/3"
              style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.025), rgba(255,220,140,0.04), transparent)" }}
              animate={{ x: ["-100%", "200%"] }}
              transition={{ duration: 5, repeat: Infinity, ease: "linear", repeatDelay: 5 }} />
          </div>

          {/* Scan line */}
          <motion.div className="absolute inset-x-0 h-px pointer-events-none"
            style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.2), transparent)" }}
            animate={{ top: ["0%", "100%"] }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }} />

          <div className="p-8 pt-7">

            {/* ── Logo ── */}
            <motion.div className="mb-8 flex flex-col items-center"
              initial={{ scale: 0, opacity: 0, rotate: -180 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              transition={{ delay: 0.5, duration: 1.2, ease: [0.23, 1, 0.32, 1] }}>

              <div className="relative mb-5 flex h-36 w-36 items-center justify-center">
                {/* Outer rings */}
                {[0, 1, 2, 3].map(i => (
                  <motion.div key={i}
                    className="absolute rounded-full"
                    style={{
                      inset: `${i * 10}px`,
                      border: `1px solid rgba(194,140,60,${0.25 - i * 0.05})`,
                    }}
                    animate={{ rotate: i % 2 === 0 ? [0, 360] : [0, -360] }}
                    transition={{ duration: 10 + i * 5, repeat: Infinity, ease: "linear" }} />
                ))}

                {/* Conic glow ring */}
                <motion.div className="absolute inset-4 rounded-full"
                  style={{ background: "conic-gradient(from 0deg, transparent 0%, rgba(194,140,60,0.15) 25%, transparent 50%, rgba(255,220,140,0.1) 75%, transparent 100%)" }}
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 6, repeat: Infinity, ease: "linear" }} />

                {/* Core */}
                <motion.div className="relative z-10 flex h-18 w-18 items-center justify-center rounded-2xl"
                  style={{
                    width: "72px", height: "72px",
                    background: "linear-gradient(135deg, #2a1504 0%, #6b3a10 30%, #c28c3c 60%, #8b5e1a 85%, #2a1504 100%)",
                    boxShadow: "0 0 0 1px rgba(255,220,150,0.1) inset",
                  }}
                  animate={{
                    boxShadow: [
                      "0 0 30px rgba(194,140,60,0.4), 0 0 60px rgba(194,140,60,0.15)",
                      "0 0 60px rgba(194,140,60,0.7), 0 0 120px rgba(194,140,60,0.3)",
                      "0 0 30px rgba(194,140,60,0.4), 0 0 60px rgba(194,140,60,0.15)",
                    ]
                  }}
                  transition={{ duration: 2.5, repeat: Infinity }}>
                  <ShoppingCart className="h-9 w-9" style={{ color: "#f5e6c0" }} />
                </motion.div>

                {/* Orbiting particles */}
                {[
                  { r: 0, speed: 4, size: 3, color: "#f5e6c0", glow: "rgba(255,248,230,1)" },
                  { r: 180, speed: 7, size: 2, color: "#c28c3c", glow: "rgba(194,140,60,0.9)" },
                  { r: 90, speed: 5.5, size: 1.5, color: "#7eb8c9", glow: "rgba(126,184,201,0.8)" },
                ].map((p, i) => (
                  <motion.div key={i} className="absolute inset-0"
                    animate={{ rotate: [p.r, p.r + 360] }}
                    transition={{ duration: p.speed, repeat: Infinity, ease: "linear" }}>
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 rounded-full"
                      style={{
                        width: `${p.size * 2}px`, height: `${p.size * 2}px`,
                        background: p.color,
                        boxShadow: `0 0 ${p.size * 4}px ${p.glow}, 0 0 ${p.size * 8}px ${p.glow.replace("1)", "0.4)")}`,
                      }} />
                  </motion.div>
                ))}
              </div>

              <motion.h1 className="text-5xl font-black tracking-tighter mb-1 text-gold"
                animate={{ opacity: [0.8, 1, 0.8] }}
                transition={{ duration: 4, repeat: Infinity }}>
                VisionCart
              </motion.h1>
              <div className="flex items-center gap-3 mt-1">
                <motion.div className="h-px w-12"
                  style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.5))" }}
                  animate={{ scaleX: [0.5, 1, 0.5] }} transition={{ duration: 3, repeat: Infinity }} />
                <p className="text-xs tracking-[0.35em] uppercase font-medium text-dust">Smart Billing</p>
                <motion.div className="h-px w-12"
                  style={{ background: "linear-gradient(90deg, rgba(194,140,60,0.5), transparent)" }}
                  animate={{ scaleX: [0.5, 1, 0.5] }} transition={{ duration: 3, repeat: Infinity }} />
              </div>
            </motion.div>

            {/* ── Form ── */}
            <form onSubmit={handleLogin} className="space-y-4">

              {/* Role buttons */}
              <div className="grid grid-cols-2 gap-3">
                {([
                  { key: "admin" as const, Icon: ShieldCheck, label: "Admin", desc: "Full access", color: "#c28c3c", glow: "rgba(194,140,60,0.25)" },
                  { key: "staff" as const, Icon: ShoppingCart, label: "Staff", desc: "Billing only", color: "#7eb8c9", glow: "rgba(126,184,201,0.2)" },
                ] as const).map(({ key, Icon, label, desc, color, glow }) => {
                  const active = role === key;
                  return (
                    <motion.button key={key} type="button"
                      whileHover={{ scale: 1.05, translateY: -4 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setRole(key)}
                      className="relative flex flex-col items-center rounded-xl p-5 overflow-hidden transition-all duration-300"
                      style={{
                        background: active ? `${color}12` : "rgba(255,255,255,0.015)",
                        border: `1px solid ${active ? `${color}40` : "rgba(194,140,60,0.06)"}`,
                      }}>
                      {active && (
                        <>
                          <motion.div className="absolute inset-0 rounded-xl pointer-events-none"
                            style={{ background: `radial-gradient(ellipse at center, ${glow} 0%, transparent 70%)` }}
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }} />
                          <motion.div className="absolute top-0 inset-x-0 h-px"
                            style={{ background: `linear-gradient(90deg, transparent, ${color}80, transparent)` }}
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 1.5, repeat: Infinity }} />
                        </>
                      )}
                      <motion.div className="relative z-10 mb-2 p-2.5 rounded-xl"
                        style={{
                          background: active ? `${color}15` : "rgba(255,255,255,0.03)",
                          border: `1px solid ${active ? `${color}30` : "rgba(255,255,255,0.04)"}`,
                          boxShadow: active ? `0 0 20px ${glow}` : "none",
                        }}
                        animate={active ? { boxShadow: [`0 0 10px ${glow}`, `0 0 25px ${glow}`, `0 0 10px ${glow}`] } : {}}
                        transition={{ duration: 2, repeat: Infinity }}>
                        <Icon className="h-6 w-6" style={{ color: active ? color : "#3a2e22" }} />
                      </motion.div>
                      <span className="relative z-10 font-bold text-sm" style={{ color: active ? "#f0e6d0" : "#3a2e22" }}>{label}</span>
                      <span className="relative z-10 text-xs mt-0.5" style={{ color: active ? "#8a7060" : "#1e1810" }}>{desc}</span>
                    </motion.button>
                  );
                })}
              </div>

              {/* Password */}
              <div className="relative">
                <input type={showPw ? "text" : "password"} placeholder="Access Code"
                  value={password}
                  onChange={e => { setPassword(e.target.value); setError(""); }}
                  className="w-full rounded-xl px-4 py-3.5 pr-12 text-sm placeholder:text-stone-800 focus:outline-none transition-all duration-300"
                  style={{
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid rgba(194,140,60,0.1)",
                    color: "#e8dcc8",
                    boxShadow: "inset 0 2px 8px rgba(0,0,0,0.5)",
                  }}
                  onFocus={e => {
                    e.target.style.borderColor = "rgba(194,140,60,0.5)";
                    e.target.style.boxShadow = "inset 0 2px 8px rgba(0,0,0,0.5), 0 0 30px rgba(194,140,60,0.1)";
                  }}
                  onBlur={e => {
                    e.target.style.borderColor = "rgba(194,140,60,0.1)";
                    e.target.style.boxShadow = "inset 0 2px 8px rgba(0,0,0,0.5)";
                  }}
                  required />
                <button type="button" onClick={() => setShowPw(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-dust hover:text-star transition-colors">
                  {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
                <AnimatePresence>
                  {error && (
                    <motion.p initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                      className="mt-2 text-xs text-center" style={{ color: "#c87060" }}>
                      {error}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/* Submit */}
              <motion.button type="submit" disabled={!role || loading}
                whileHover={role && !loading ? { scale: 1.02, translateY: -2 } : {}}
                whileTap={role && !loading ? { scale: 0.98 } : {}}
                className="relative w-full flex items-center justify-center gap-2 rounded-xl py-4 font-black overflow-hidden disabled:opacity-30 disabled:cursor-not-allowed"
                style={{
                  background: "linear-gradient(135deg, #3a1e06, #7a5010, #c28c3c, #7a5010, #3a1e06)",
                  color: "#f5e6c0",
                  border: "1px solid rgba(194,140,60,0.25)",
                  boxShadow: role ? "0 0 50px rgba(194,140,60,0.25), 0 12px 35px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,220,150,0.12)" : "none",
                  animation: role && !loading ? "gold-flow 3s linear infinite" : "none",
                }}>
                <div className="absolute inset-0 shimmer-btn pointer-events-none" />
                <AnimatePresence mode="wait">
                  {loading ? (
                    <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="flex items-center gap-2 relative z-10">
                      {[0, 1, 2].map(i => (
                        <motion.div key={i} className="w-2 h-2 rounded-full"
                          style={{ background: "#f5e6c0" }}
                          animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                          transition={{ duration: 0.8, delay: i * 0.15, repeat: Infinity }} />
                      ))}
                    </motion.div>
                  ) : (
                    <motion.span key="text" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="relative z-10 tracking-widest uppercase text-sm font-black">
                      Login
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            </form>
          </div>

          {/* Bottom horizon */}
          <motion.div className="h-px w-full"
            style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.3), rgba(255,248,230,0.8), rgba(194,140,60,0.3), transparent)" }}
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 3, repeat: Infinity, delay: 1.5 }} />
        </div>
      </motion.div>
    </div>
  );
}
