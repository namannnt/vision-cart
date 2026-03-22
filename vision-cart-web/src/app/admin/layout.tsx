"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Camera, LayoutDashboard, PackageSearch, LogOut, Cpu } from "lucide-react";
import { motion } from "framer-motion";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const navLinks = [
    { name: "Dashboard", href: "/admin", icon: LayoutDashboard, color: "#6366f1" },
    { name: "Inventory", href: "/admin/inventory", icon: PackageSearch, color: "#06b6d4" },
    { name: "Registration", href: "/admin/registration", icon: Camera, color: "#8b5cf6" },
  ];

  return (
    <div className="flex h-screen overflow-hidden">
      {/* 3D Sidebar */}
      <aside
        className="w-64 flex-col hidden md:flex z-20 relative"
        style={{
          background: "linear-gradient(180deg, rgba(8,10,25,0.98) 0%, rgba(5,8,18,0.99) 100%)",
          borderRight: "1px solid rgba(255,255,255,0.05)",
          boxShadow: "4px 0 24px rgba(0,0,0,0.5), inset -1px 0 0 rgba(255,255,255,0.03)",
        }}
      >
        {/* Top glowing line */}
        <div className="absolute top-0 inset-x-0 h-px"
          style={{ background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.6), rgba(6,182,212,0.4), transparent)" }} />

        {/* Logo */}
        <div className="flex h-16 items-center px-6"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
          <Link href="/admin" className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg flex-shrink-0"
              style={{
                background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                boxShadow: "0 0 20px rgba(99,102,241,0.4), inset 0 1px 0 rgba(255,255,255,0.15)",
              }}>
              <Cpu className="h-4 w-4 text-white" />
            </div>
            <div>
              <span className="font-black text-sm tracking-tight"
                style={{
                  background: "linear-gradient(135deg, #fff, #a5b4fc)",
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text"
                }}>
                VisionCart
              </span>
              <p className="text-xs text-slate-600 font-medium tracking-widest uppercase" style={{ fontSize: "9px" }}>Admin Portal</p>
            </div>
          </Link>
        </div>

        {/* Status indicator */}
        <div className="mx-4 mt-4 px-3 py-2 rounded-lg flex items-center gap-2"
          style={{ background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.12)" }}>
          <span className="relative flex h-2 w-2 flex-shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-xs text-emerald-500 font-medium">Systems Online</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1.5 px-3 py-6">
          <p className="px-3 mb-3 text-xs font-semibold text-slate-600 tracking-widest uppercase">Navigation</p>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <div key={link.name} className="relative">
                {isActive && (
                  <motion.div
                    layoutId="sidebarActive"
                    className="absolute inset-0 rounded-xl"
                    style={{
                      background: `linear-gradient(135deg, ${link.color}18, ${link.color}08)`,
                      border: `1px solid ${link.color}30`,
                      boxShadow: `0 0 20px ${link.color}15, inset 0 1px 0 ${link.color}15`,
                    }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <Link
                  href={link.href}
                  className={`relative z-10 flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all group ${
                    isActive ? "text-slate-100" : "text-slate-500 hover:text-slate-200"
                  }`}
                >
                  <div className={`p-1.5 rounded-lg flex-shrink-0 transition-all ${isActive ? "" : "group-hover:scale-110"}`}
                    style={isActive ? {
                      background: `${link.color}20`,
                      boxShadow: `0 0 12px ${link.color}30`,
                    } : {}}>
                    <Icon className="h-4 w-4" style={isActive ? { color: link.color } : {}} />
                  </div>
                  <span>{link.name}</span>
                  {isActive && (
                    <div className="ml-auto h-1.5 w-1.5 rounded-full flex-shrink-0"
                      style={{ background: link.color, boxShadow: `0 0 6px ${link.color}` }} />
                  )}
                </Link>
              </div>
            );
          })}
        </nav>

        {/* Sign out */}
        <div className="p-3" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
          <Link
            href="/login"
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 hover:text-red-400 transition-all group"
            style={{ border: "1px solid transparent" }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.06)";
              (e.currentTarget as HTMLElement).style.borderColor = "rgba(239,68,68,0.15)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = "transparent";
              (e.currentTarget as HTMLElement).style.borderColor = "transparent";
            }}
          >
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl p-8">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
