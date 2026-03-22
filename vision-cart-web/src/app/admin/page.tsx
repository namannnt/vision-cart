"use client";

import { useEffect, useState, useRef } from "react";
import { DollarSign, Package, TrendingUp, AlertTriangle, Activity } from "lucide-react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import Link from "next/link";

type Product = {
  id: number;
  product_id: string;
  price: number;
  stock: number;
};

function StatCard({ stat, index }: { stat: { title: string; value: string; icon: React.ElementType; glowColor: string; accentColor: string; gradient: string; }; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 200, damping: 30 });
  const springY = useSpring(mouseY, { stiffness: 200, damping: 30 });
  const rotateX = useTransform(springY, [-80, 80], [8, -8]);
  const rotateY = useTransform(springX, [-80, 80], [-8, 8]);

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 40, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d", perspective: 800 }}
      onMouseMove={(e) => {
        const rect = cardRef.current?.getBoundingClientRect();
        if (!rect) return;
        mouseX.set(e.clientX - rect.left - rect.width / 2);
        mouseY.set(e.clientY - rect.top - rect.height / 2);
      }}
      onMouseLeave={() => { mouseX.set(0); mouseY.set(0); }}
      className="relative cursor-default group"
    >
      <div className="absolute inset-0 rounded-2xl translate-x-2 translate-y-2 opacity-30"
        style={{ background: stat.glowColor, filter: "blur(2px)" }} />
      <div className="absolute inset-0 rounded-2xl translate-x-1 translate-y-1 opacity-20"
        style={{ background: stat.glowColor }} />
      <div
        className="relative rounded-2xl overflow-hidden p-6 transition-all duration-300"
        style={{
          background: "linear-gradient(145deg, rgba(12,15,35,0.98), rgba(8,10,25,0.99))",
          border: `1px solid ${stat.glowColor}30`,
          boxShadow: `0 0 0 1px ${stat.glowColor}10 inset, 0 4px 24px rgba(0,0,0,0.8), 0 0 60px ${stat.glowColor}0a`,
        }}
      >
        <div className="absolute top-0 inset-x-0 h-px opacity-60"
          style={{ background: `linear-gradient(90deg, transparent, ${stat.glowColor}, transparent)` }} />
        <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full opacity-10 group-hover:opacity-20 transition-opacity duration-500"
          style={{ background: `radial-gradient(circle, ${stat.glowColor}, transparent 70%)`, filter: "blur(20px)" }} />
        <div className="relative mb-4 inline-flex">
          <div className="p-3 rounded-xl"
            style={{
              background: `linear-gradient(135deg, ${stat.glowColor}25, ${stat.glowColor}10)`,
              border: `1px solid ${stat.glowColor}30`,
              boxShadow: `0 0 20px ${stat.glowColor}20`,
            }}>
            <stat.icon className="h-6 w-6" style={{ color: stat.accentColor }} />
          </div>
        </div>
        <p className="text-3xl font-black tracking-tight mb-1"
          style={{
            background: `linear-gradient(135deg, #fff 0%, ${stat.accentColor} 100%)`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}>
          {stat.value}
        </p>
        <h3 className="text-slate-500 text-sm font-medium">{stat.title}</h3>
        <div className="absolute bottom-0 inset-x-0 h-px opacity-30"
          style={{ background: `linear-gradient(90deg, transparent, ${stat.glowColor}, transparent)` }} />
      </div>
    </motion.div>
  );
}

export default function AdminDashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = () => {
    fetch("/api/products")
      .then((res) => res.json())
      .then((data) => { setProducts(data); setLoading(false); });
  };

  useEffect(() => {
    fetchProducts();
    const interval = setInterval(fetchProducts, 10000);
    return () => clearInterval(interval);
  }, []);

  const totalStock = products.reduce((acc, curr) => acc + curr.stock, 0);
  const lowStockItems = products.filter(p => p.stock <= 3);
  const totalValue = products.reduce((acc, curr) => acc + (curr.price * curr.stock), 0);

  const stats = [
    { title: "Registered Products", value: products.length.toString(), icon: Package, glowColor: "#3b82f6", accentColor: "#60a5fa", gradient: "from-blue-500" },
    { title: "Total Stock Units", value: totalStock.toString(), icon: Activity, glowColor: "#8b5cf6", accentColor: "#a78bfa", gradient: "from-purple-500" },
    { title: "Inventory Value", value: `₹${totalValue.toLocaleString()}`, icon: DollarSign, glowColor: "#10b981", accentColor: "#34d399", gradient: "from-emerald-500" },
    { title: "Low Stock Alerts", value: lowStockItems.length.toString(), icon: AlertTriangle, glowColor: "#f59e0b", accentColor: "#fbbf24", gradient: "from-amber-500" },
  ];

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="h-px flex-1" style={{ background: "linear-gradient(90deg, rgba(99,102,241,0.5), transparent)" }} />
          <span className="text-xs text-indigo-400 font-semibold tracking-widest uppercase">Admin Console</span>
        </div>
        <h1 className="text-4xl font-black tracking-tight"
          style={{
            background: "linear-gradient(135deg, #fff 0%, #a5b4fc 50%, #67e8f9 100%)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text"
          }}>
          Command Center
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Monitor your store&apos;s performance and inventory health.</p>
      </motion.div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-36 rounded-2xl animate-pulse" style={{ background: "rgba(255,255,255,0.03)" }} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, i) => <StatCard key={stat.title} stat={stat} index={i} />)}
        </div>
      )}

      {!loading && lowStockItems.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="relative rounded-2xl overflow-hidden"
          style={{
            background: "linear-gradient(145deg, rgba(15,12,8,0.98), rgba(10,8,4,0.99))",
            border: "1px solid rgba(245,158,11,0.2)",
            boxShadow: "0 0 60px rgba(245,158,11,0.05), 0 24px 48px rgba(0,0,0,0.6)"
          }}
        >
          <div className="absolute top-0 inset-x-0 h-px"
            style={{ background: "linear-gradient(90deg, transparent, rgba(245,158,11,0.6), transparent)" }} />
          <div className="px-6 py-4 border-b border-amber-500/15 flex items-center gap-3"
            style={{ background: "rgba(245,158,11,0.05)" }}>
            <div className="p-2 rounded-lg" style={{ background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)" }}>
              <AlertTriangle className="h-4 w-4 text-amber-400" />
            </div>
            <h2 className="font-bold text-amber-400 tracking-wide">Low Stock Alert</h2>
            <span className="ml-auto text-xs text-amber-600 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
              {lowStockItems.length} items
            </span>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {lowStockItems.map((item, i) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 + i * 0.05 }}
                  className="relative rounded-xl p-4 overflow-hidden"
                  style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(245,158,11,0.12)" }}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-slate-200">{item.product_id}</h3>
                      <p className="text-slate-500 text-sm mt-0.5">₹{item.price.toLocaleString()}</p>
                    </div>
                    <div className="text-center px-3 py-1.5 rounded-lg"
                      style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)" }}>
                      <p className="text-red-400 font-black text-lg leading-none">{item.stock}</p>
                      <p className="text-red-600 text-xs">left</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            <div className="mt-5 flex justify-end">
              <Link href="/admin/inventory"
                className="flex items-center gap-2 text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors group">
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
