"use client";

import { useEffect, useState, useRef } from "react";
import { DollarSign, Package, TrendingUp, AlertTriangle, Activity } from "lucide-react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import Link from "next/link";

type Product = { id: number; product_id: string; price: number; stock: number; };

function StatCard({ stat, index }: {
  stat: { title: string; value: string; icon: React.ElementType; color: string; glow: string };
  index: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const mx = useMotionValue(0); const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 120, damping: 22 });
  const sy = useSpring(my, { stiffness: 120, damping: 22 });
  const rx = useTransform(sy, [-50, 50], [5, -5]);
  const ry = useTransform(sx, [-50, 50], [-5, 5]);

  return (
    <motion.div ref={ref}
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
      style={{ rotateX: rx, rotateY: ry, transformStyle: "preserve-3d", perspective: 600 }}
      onMouseMove={e => {
        const r = ref.current?.getBoundingClientRect();
        if (!r) return;
        mx.set(e.clientX - r.left - r.width / 2);
        my.set(e.clientY - r.top - r.height / 2);
      }}
      onMouseLeave={() => { mx.set(0); my.set(0); }}
      className="stat-card p-6 relative overflow-hidden cursor-default group">

      {/* Top accent line */}
      <div className="absolute top-0 inset-x-0 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${stat.color}50, ${stat.color}80, ${stat.color}50, transparent)` }} />

      {/* Corner wormhole glow */}
      <motion.div className="absolute -top-10 -right-10 w-40 h-40 rounded-full pointer-events-none"
        style={{ background: `radial-gradient(circle, ${stat.glow} 0%, transparent 70%)`, filter: "blur(25px)" }}
        animate={{ opacity: [0.3, 0.7, 0.3], scale: [1, 1.1, 1] }}
        transition={{ duration: 4 + index, repeat: Infinity, ease: "easeInOut" }} />

      {/* Scan line */}
      <motion.div className="absolute inset-x-0 h-px pointer-events-none"
        style={{ background: `linear-gradient(90deg, transparent, ${stat.color}30, transparent)` }}
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 6 + index, repeat: Infinity, ease: "linear" }} />

      {/* Icon */}
      <div className="relative mb-5 inline-flex">
        <div className="p-3 rounded-xl"
          style={{
            background: `${stat.color}10`,
            border: `1px solid ${stat.color}20`,
            boxShadow: `0 0 25px ${stat.glow}`,
          }}>
          <stat.icon className="h-5 w-5" style={{ color: stat.color }} />
        </div>
      </div>

      {/* Value */}
      <p className="text-3xl font-black tracking-tight mb-1"
        style={{ color: "#e8dcc8", textShadow: `0 0 40px ${stat.glow}` }}>
        {stat.value}
      </p>
      <p className="text-sm font-medium text-dust">{stat.title}</p>

      {/* Bottom accent */}
      <div className="absolute bottom-0 inset-x-0 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${stat.color}20, transparent)` }} />
    </motion.div>
  );
}

export default function AdminDashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = () => {
    fetch("/api/products").then(r => r.json()).then(d => { setProducts(d); setLoading(false); });
  };

  useEffect(() => {
    fetchProducts();
    const t = setInterval(fetchProducts, 10000);
    return () => clearInterval(t);
  }, []);

  const totalStock = products.reduce((a, c) => a + c.stock, 0);
  const lowStock = products.filter(p => p.stock <= 3);
  const totalValue = products.reduce((a, c) => a + c.price * c.stock, 0);

  const stats = [
    { title: "Registered Products", value: products.length.toString(),       icon: Package,       color: "#c28c3c", glow: "rgba(194,140,60,0.25)"  },
    { title: "Total Stock Units",    value: totalStock.toString(),            icon: Activity,      color: "#7eb8c9", glow: "rgba(126,184,201,0.2)"  },
    { title: "Inventory Value",      value: `₹${totalValue.toLocaleString()}`, icon: DollarSign,  color: "#8fbc8f", glow: "rgba(143,188,143,0.2)"  },
    { title: "Low Stock Alerts",     value: lowStock.length.toString(),       icon: AlertTriangle, color: "#c87060", glow: "rgba(200,112,96,0.2)"   },
  ];

  return (
    <div className="space-y-8">

      {/* ── Header ── */}
      <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.7 }}>
        <div className="flex items-center gap-4 mb-3">
          <div className="h-px flex-1" style={{ background: "linear-gradient(90deg, rgba(194,140,60,0.5), transparent)" }} />
          <span className="text-xs font-bold tracking-[0.3em] uppercase text-dust">Admin</span>
          <div className="h-px w-8" style={{ background: "rgba(194,140,60,0.2)" }} />
        </div>
        <h1 className="text-5xl font-black tracking-tighter text-gold">Dashboard</h1>
        <p className="mt-2 text-sm text-dust">Your store overview at a glance.</p>
      </motion.div>

      {/* ── Stats ── */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-40 rounded-2xl animate-pulse"
              style={{ background: "rgba(194,140,60,0.03)", border: "1px solid rgba(194,140,60,0.06)" }} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {stats.map((s, i) => <StatCard key={s.title} stat={s} index={i} />)}
        </div>
      )}

      {/* ── Low stock warning ── */}
      {!loading && lowStock.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 25 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5, duration: 0.7 }}
          className="relative rounded-2xl overflow-hidden panel">

          {/* Top accent */}
          <div className="absolute top-0 inset-x-0 h-px"
            style={{ background: "linear-gradient(90deg, transparent, rgba(200,112,96,0.6), transparent)" }} />

          {/* Ambient glow */}
          <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-80 h-40 pointer-events-none"
            style={{ background: "radial-gradient(ellipse, rgba(200,112,96,0.06) 0%, transparent 70%)", filter: "blur(30px)" }} />

          <div className="px-6 py-4 flex items-center gap-3"
            style={{ borderBottom: "1px solid rgba(200,112,96,0.08)", background: "rgba(200,112,96,0.03)" }}>
            <motion.div className="p-2 rounded-xl"
              style={{ background: "rgba(200,112,96,0.1)", border: "1px solid rgba(200,112,96,0.2)" }}
              animate={{ boxShadow: ["0 0 10px rgba(200,112,96,0.2)", "0 0 25px rgba(200,112,96,0.4)", "0 0 10px rgba(200,112,96,0.2)"] }}
              transition={{ duration: 2, repeat: Infinity }}>
              <AlertTriangle className="h-4 w-4" style={{ color: "#c87060" }} />
            </motion.div>
            <h2 className="font-bold tracking-wide" style={{ color: "#c87060" }}>Low Stock Warning</h2>
            <span className="ml-auto text-xs px-2.5 py-1 rounded-full font-bold"
              style={{ background: "rgba(200,112,96,0.1)", border: "1px solid rgba(200,112,96,0.2)", color: "#c87060" }}>
              {lowStock.length} items
            </span>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {lowStock.map((item, i) => (
                <motion.div key={item.id}
                  initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 + i * 0.06 }}
                  className="rounded-xl p-4 relative overflow-hidden"
                  style={{ background: "rgba(255,255,255,0.01)", border: "1px solid rgba(200,112,96,0.1)" }}>
                  <div className="absolute top-0 inset-x-0 h-px"
                    style={{ background: "linear-gradient(90deg, transparent, rgba(200,112,96,0.3), transparent)" }} />
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold" style={{ color: "#e8dcc8" }}>{item.product_id}</h3>
                      <p className="text-sm mt-0.5 text-dust">₹{item.price.toLocaleString()}</p>
                    </div>
                    <div className="text-center px-3 py-2 rounded-xl"
                      style={{ background: "rgba(200,112,96,0.08)", border: "1px solid rgba(200,112,96,0.2)" }}>
                      <p className="font-black text-xl leading-none" style={{ color: "#c87060" }}>{item.stock}</p>
                      <p className="text-xs mt-0.5" style={{ color: "#7a4030" }}>left</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            <div className="mt-5 flex justify-end">
              <Link href="/admin/inventory"
                className="flex items-center gap-2 text-sm font-bold transition-all group"
                style={{ color: "#c28c3c" }}
                onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = "#e8a84c"}
                onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = "#c28c3c"}>
                <span>Manage Inventory</span>
                <TrendingUp className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
