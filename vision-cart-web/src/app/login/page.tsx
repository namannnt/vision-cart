"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { LogIn, ShieldCheck, ShoppingCart, Zap } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"admin" | "staff" | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 100, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 100, damping: 20 });
  const rotateX = useTransform(springY, [-200, 200], [10, -10]);
  const rotateY = useTransform(springX, [-200, 200], [-10, 10]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = cardRef.current?.getBoundingClientRect();
    if (!rect) return;
    mouseX.set(e.clientX - rect.left - rect.width / 2);
    mouseY.set(e.clientY - rect.top - rect.height / 2);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (role === "admin") router.push("/admin");
    if (role === "staff") router.push("/billing");
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 overflow-hidden">

      {/* Floating background orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ y: [0, -30, 0], rotate: [0, 10, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, #6366f1, transparent 70%)", filter: "blur(40px)" }}
        />
        <motion.div
          animate={{ y: [0, 20, 0], rotate: [0, -8, 0] }}
          transition={{ duration: 10, delay: 2, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full opacity-8"
          style={{ background: "radial-gradient(circle, #06b6d4, transparent 70%)", filter: "blur(60px)" }}
        />
      </div>

      {/* 3D Tilt Card */}
      <motion.div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ rotateX, rotateY, transformStyle: "preserve-3d", perspective: 1000 }}
        initial={{ opacity: 0, y: 60, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
        className="relative w-full max-w-md"
      >
        {/* Holographic border glow */}
        <div className="absolute -inset-px rounded-2xl opacity-70"
          style={{
            background: "linear-gradient(135deg, rgba(99,102,241,0.5), rgba(6,182,212,0.3), rgba(139,92,246,0.5), rgba(59,130,246,0.3))",
            filter: "blur(1px)",
            borderRadius: "1rem",
          }}
        />

        {/* Card body */}
        <div
          className="relative rounded-2xl overflow-hidden"
          style={{
            background: "linear-gradient(145deg, rgba(15,18,40,0.97), rgba(8,10,28,0.99))",
            backdropFilter: "blur(40px)",
            border: "1px solid rgba(255,255,255,0.06)",
            boxShadow: "0 32px 80px -20px rgba(0,0,0,0.9), 0 0 120px -40px rgba(99,102,241,0.3)",
            transform: "translateZ(20px)",
          }}
        >
          {/* Top scan line */}
          <div className="absolute top-0 inset-x-0 h-px"
            style={{ background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.8), rgba(6,182,212,0.8), transparent)" }} />

          {/* Shimmer overlay */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
            <motion.div
              animate={{ x: ["-100%", "200%"] }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear", repeatDelay: 2 }}
              className="absolute inset-y-0 w-1/3"
              style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent)" }}
            />
          </div>

          <div className="p-8">
            {/* Logo section */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.3, duration: 0.7, ease: [0.23, 1, 0.32, 1] }}
              className="mb-8 flex flex-col items-center text-center"
            >
              {/* Orbiting logo */}
              <div className="relative mb-5 flex h-24 w-24 items-center justify-center">
                {/* Outer ring */}
                <div className="absolute inset-0 rounded-full border border-indigo-500/30 animate-spin" style={{ animationDuration: "10s" }} />
                <div className="absolute inset-2 rounded-full border border-cyan-500/20 animate-spin" style={{ animationDuration: "7s", animationDirection: "reverse" }} />

                {/* Center icon */}
                <div className="relative z-10 flex h-16 w-16 items-center justify-center rounded-2xl"
                  style={{
                    background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                    boxShadow: "0 0 30px rgba(99,102,241,0.5), 0 0 60px rgba(99,102,241,0.2), inset 0 1px 0 rgba(255,255,255,0.15)",
                  }}>
                  <ShoppingCart className="h-8 w-8 text-white drop-shadow-md" />
                </div>

                {/* Orbiting dot */}
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0"
                >
                  <div className="absolute top-1 left-1/2 -translate-x-1/2 h-2 w-2 rounded-full bg-cyan-400"
                    style={{ boxShadow: "0 0 8px rgba(6,182,212,0.8)" }} />
                </motion.div>
              </div>

              <h1
                className="text-4xl font-black tracking-tighter mb-1"
                style={{
                  background: "linear-gradient(135deg, #fff 0%, #a5b4fc 40%, #67e8f9 80%, #fff 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                VisionCart
              </h1>

              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Zap className="h-3 w-3 text-indigo-400" />
                <span className="tracking-widest uppercase text-xs font-medium text-slate-400">
                  AI-Powered Smart Billing
                </span>
                <Zap className="h-3 w-3 text-cyan-400" />
              </div>
            </motion.div>

            {/* Role selection */}
            <form onSubmit={handleLogin} className="space-y-5">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { key: "admin" as const, Icon: ShieldCheck, label: "Admin", desc: "Full access", color: "purple", gradient: "from-purple-500/20 to-indigo-500/10", border: "border-purple-500/60", glow: "rgba(139,92,246,0.3)" },
                  { key: "staff" as const, Icon: ShoppingCart, label: "Staff", desc: "Billing only", color: "cyan", gradient: "from-cyan-500/20 to-blue-500/10", border: "border-cyan-500/60", glow: "rgba(6,182,212,0.3)" },
                ].map(({ key, Icon, label, desc, gradient, border, glow }) => (
                  <motion.button
                    key={key}
                    type="button"
                    whileHover={{ scale: 1.03, translateY: -2 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => setRole(key)}
                    className={`relative flex flex-col items-center rounded-xl border p-5 transition-all overflow-hidden ${
                      role === key
                        ? `bg-gradient-to-br ${gradient} ${border}`
                        : "border-slate-800/60 bg-slate-900/40 hover:border-slate-700"
                    }`}
                    style={role === key ? { boxShadow: `0 0 30px ${glow}, inset 0 1px 0 rgba(255,255,255,0.07)` } : {}}
                  >
                    {role === key && (
                      <div className="absolute inset-0 opacity-30"
                        style={{ background: `radial-gradient(circle at center, ${glow}, transparent 70%)` }} />
                    )}
                    <Icon className={`mb-2 h-7 w-7 relative z-10 ${role === key ? (key === "admin" ? "text-purple-300" : "text-cyan-300") : "text-slate-500"}`} />
                    <span className={`font-bold text-sm relative z-10 ${role === key ? "text-white" : "text-slate-400"}`}>{label}</span>
                    <span className={`text-xs mt-0.5 relative z-10 ${role === key ? "text-slate-300" : "text-slate-600"}`}>{desc}</span>
                  </motion.button>
                ))}
              </div>

              <div>
                <input
                  type="password"
                  placeholder="Enter Access Code..."
                  className="w-full rounded-xl px-4 py-3.5 text-slate-100 placeholder:text-slate-600 focus:outline-none transition-all"
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    boxShadow: "inset 0 2px 4px rgba(0,0,0,0.3)",
                  }}
                  onFocus={(e) => {
                    e.target.style.border = "1px solid rgba(99,102,241,0.6)";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0,0,0,0.3), 0 0 20px rgba(99,102,241,0.15)";
                  }}
                  onBlur={(e) => {
                    e.target.style.border = "1px solid rgba(255,255,255,0.08)";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0,0,0,0.3)";
                  }}
                  required
                />
              </div>

              <motion.button
                type="submit"
                disabled={!role}
                whileHover={role ? { scale: 1.02 } : {}}
                whileTap={role ? { scale: 0.98 } : {}}
                className="relative w-full flex items-center justify-center gap-2 rounded-xl py-3.5 font-bold text-white overflow-hidden disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  background: role ? "linear-gradient(135deg, #4f46e5, #7c3aed, #0891b2)" : "#1e1e2e",
                  boxShadow: role ? "0 0 30px rgba(99,102,241,0.4), 0 8px 20px rgba(0,0,0,0.5)" : "none",
                }}
              >
                {role && (
                  <motion.div
                    animate={{ x: ["-100%", "200%"] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear", repeatDelay: 1 }}
                    className="absolute inset-y-0 w-1/3"
                    style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent)" }}
                  />
                )}
                <span className="relative z-10">Access Portal</span>
                <LogIn className="h-4 w-4 relative z-10" />
              </motion.button>
            </form>
          </div>

          {/* Bottom glow */}
          <div className="h-px w-full"
            style={{ background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.4), rgba(6,182,212,0.4), transparent)" }} />
        </div>
      </motion.div>
    </div>
  );
}
