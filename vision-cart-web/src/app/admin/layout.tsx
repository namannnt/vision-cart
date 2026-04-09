"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Camera, LayoutDashboard, PackageSearch, LogOut, TrendingUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";

const WormholeCanvas = dynamic(() => import("@/components/WormholeCanvas"), { ssr: false });

const navLinks = [
  { name: "Dashboard",     href: "/admin",              icon: LayoutDashboard, color: "#c28c3c", glow: "rgba(194,140,60,0.3)"  },
  { name: "Inventory",     href: "/admin/inventory",    icon: PackageSearch,   color: "#7eb8c9", glow: "rgba(126,184,201,0.25)" },
  { name: "Sales History", href: "/admin/sales",        icon: TrendingUp,      color: "#8fbc8f", glow: "rgba(143,188,143,0.25)" },
  { name: "Add Product",   href: "/admin/registration", icon: Camera,          color: "#b8a090", glow: "rgba(184,160,144,0.25)" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "#030201" }}>
      <WormholeCanvas />

      {/* Vignette */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 1,
        background: "radial-gradient(ellipse 80% 80% at 50% 50%, transparent 20%, rgba(2,1,0,0.5) 100%)" }} />

      {/* ── Sidebar ── */}
      <aside className="w-64 flex-col hidden md:flex flex-shrink-0 relative"
        style={{ zIndex: 20 }}>

        {/* Sidebar glass panel */}
        <div className="absolute inset-0"
          style={{
            background: "linear-gradient(180deg, rgba(16,10,4,0.96) 0%, rgba(8,5,2,0.98) 100%)",
            borderRight: "1px solid rgba(194,140,60,0.08)",
            boxShadow: "6px 0 50px rgba(0,0,0,0.9), inset -1px 0 0 rgba(194,140,60,0.04)",
            backdropFilter: "blur(20px)",
          }} />

        {/* Animated top horizon */}
        <motion.div className="absolute top-0 inset-x-0 h-px"
          style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.6), rgba(255,248,230,0.8), rgba(194,140,60,0.6), transparent)" }}
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 4, repeat: Infinity }} />

        {/* Wormhole ambient glow at bottom */}
        <div className="absolute bottom-0 inset-x-0 h-48 pointer-events-none"
          style={{ background: "radial-gradient(ellipse 100% 80% at 50% 100%, rgba(194,140,60,0.05) 0%, transparent 70%)" }} />

        {/* Scan line */}
        <motion.div className="absolute inset-x-0 h-px pointer-events-none"
          style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.15), transparent)" }}
          animate={{ top: ["0%", "100%"] }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }} />

        <div className="relative flex flex-col h-full">
          {/* Logo */}
          <div className="flex h-16 items-center px-5 flex-shrink-0"
            style={{ borderBottom: "1px solid rgba(194,140,60,0.06)" }}>
            <Link href="/admin" className="flex items-center gap-3 group">
              <motion.div className="relative flex h-9 w-7 items-center justify-center rounded-md flex-shrink-0 overflow-hidden"
                style={{ background: "linear-gradient(180deg, #2a1504 0%, #6b3a10 40%, #c28c3c 70%, #8b5e1a 100%)" }}
                animate={{ boxShadow: ["0 0 15px rgba(194,140,60,0.4)", "0 0 35px rgba(194,140,60,0.7)", "0 0 15px rgba(194,140,60,0.4)"] }}
                transition={{ duration: 3, repeat: Infinity }}>
                {[0, 1, 2, 3].map(i => (
                  <div key={i} className="absolute inset-x-1 h-px"
                    style={{ top: `${18 + i * 18}%`, background: `rgba(255,220,150,${0.12 + i * 0.06})` }} />
                ))}
              </motion.div>
              <div>
                <span className="font-black text-sm tracking-tight text-gold">VisionCart</span>
                <p className="font-medium tracking-[0.25em] uppercase text-dust" style={{ fontSize: "8px" }}>Admin Panel</p>
              </div>
            </Link>
          </div>

          {/* Status */}
          <div className="mx-4 mt-4 px-3 py-2.5 rounded-xl flex items-center gap-2.5"
            style={{ background: "rgba(143,188,143,0.04)", border: "1px solid rgba(143,188,143,0.1)" }}>
            <div className="relative flex h-2 w-2 flex-shrink-0">
              <motion.span className="absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ background: "#8fbc8f" }}
                animate={{ scale: [1, 2, 1], opacity: [0.75, 0, 0.75] }}
                transition={{ duration: 2, repeat: Infinity }} />
              <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: "#8fbc8f" }} />
            </div>
            <span className="text-xs font-medium" style={{ color: "#8fbc8f" }}>System Ready</span>
            <div className="ml-auto flex items-end gap-0.5">
              {[3, 5, 4, 6, 3].map((h, i) => (
                <motion.div key={i} className="w-1 rounded-full"
                  style={{ background: `rgba(143,188,143,${0.3 + i * 0.1})` }}
                  animate={{ height: [`${h}px`, `${h + 4}px`, `${h}px`] }}
                  transition={{ duration: 0.8, delay: i * 0.1, repeat: Infinity }} />
              ))}
            </div>
          </div>

          {/* Nav */}
          <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
            <p className="px-3 mb-4 text-xs font-bold tracking-[0.25em] uppercase" style={{ color: "#2a1e14" }}>Navigation</p>
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <div key={link.name} className="relative">
                  <AnimatePresence>
                    {isActive && (
                      <motion.div layoutId="activeNav" className="absolute inset-0 rounded-xl"
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        style={{
                          background: `linear-gradient(135deg, ${link.color}14, ${link.color}06)`,
                          border: `1px solid ${link.color}22`,
                        }}
                        transition={{ type: "spring", stiffness: 400, damping: 35 }}>
                        {/* Active glow */}
                        <motion.div className="absolute inset-0 rounded-xl"
                          style={{ background: `radial-gradient(ellipse at left, ${link.glow} 0%, transparent 70%)` }}
                          animate={{ opacity: [0.4, 0.8, 0.4] }}
                          transition={{ duration: 2, repeat: Infinity }} />
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <Link href={link.href}
                    className="relative z-10 flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-200"
                    style={{ color: isActive ? "#e8dcc8" : "#3a2e22" }}
                    onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = "#7a6050"; }}
                    onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = "#3a2e22"; }}>
                    <motion.div className="p-1.5 rounded-lg flex-shrink-0"
                      style={isActive ? {
                        background: `${link.color}15`,
                        border: `1px solid ${link.color}25`,
                        boxShadow: `0 0 20px ${link.glow}`,
                      } : { border: "1px solid transparent" }}
                      animate={isActive ? { boxShadow: [`0 0 10px ${link.glow}`, `0 0 25px ${link.glow}`, `0 0 10px ${link.glow}`] } : {}}
                      transition={{ duration: 2, repeat: Infinity }}>
                      <Icon className="h-4 w-4" style={{ color: isActive ? link.color : "#3a2e22" }} />
                    </motion.div>
                    <span className="flex-1">{link.name}</span>
                    {isActive && (
                      <motion.div className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                        style={{ background: link.color }}
                        animate={{ boxShadow: [`0 0 4px ${link.color}`, `0 0 12px ${link.color}`, `0 0 4px ${link.color}`], scale: [1, 1.3, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }} />
                    )}
                  </Link>
                </div>
              );
            })}
          </nav>

          {/* Sign out */}
          <div className="p-3 flex-shrink-0" style={{ borderTop: "1px solid rgba(194,140,60,0.05)" }}>
            <Link href="/login"
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 group"
              style={{ color: "#3a2e22", border: "1px solid transparent" }}
              onMouseEnter={e => {
                const el = e.currentTarget as HTMLElement;
                el.style.background = "rgba(200,112,96,0.06)";
                el.style.borderColor = "rgba(200,112,96,0.2)";
                el.style.color = "#c87060";
              }}
              onMouseLeave={e => {
                const el = e.currentTarget as HTMLElement;
                el.style.background = "transparent";
                el.style.borderColor = "transparent";
                el.style.color = "#3a2e22";
              }}>
              <div className="p-1.5 rounded-lg" style={{ border: "1px solid transparent" }}>
                <LogOut className="h-4 w-4" />
              </div>
              <span>Sign Out</span>
            </Link>
          </div>

          {/* Bottom horizon */}
          <motion.div className="absolute bottom-0 inset-x-0 h-px"
            style={{ background: "linear-gradient(90deg, transparent, rgba(194,140,60,0.4), transparent)" }}
            animate={{ opacity: [0.3, 0.8, 0.3] }}
            transition={{ duration: 4, repeat: Infinity, delay: 2 }} />
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 overflow-y-auto relative" style={{ zIndex: 10 }}>
        <div className="relative mx-auto max-w-6xl p-8">
          <AnimatePresence mode="wait">
            <motion.div key={pathname}
              initial={{ opacity: 0, y: 20, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -10, filter: "blur(4px)" }}
              transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}>
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
