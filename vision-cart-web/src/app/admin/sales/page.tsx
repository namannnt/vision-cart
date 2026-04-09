"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, ShoppingBag, DollarSign, RefreshCcw } from "lucide-react";

type Sale = { id: number; product_id: string; quantity: number; price_per_unit: number; total_amount: number; sold_at: string; };

export default function SalesPage() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSales = () => {
    setLoading(true);
    fetch("/api/sales").then(r => r.json()).then(d => { setSales(d); setLoading(false); });
  };

  useEffect(() => { fetchSales(); }, []);

  const totalRevenue = sales.reduce((a, s) => a + s.total_amount, 0);
  const totalUnits = sales.reduce((a, s) => a + s.quantity, 0);

  const productMap: Record<string, { units: number; revenue: number }> = {};
  for (const s of sales) {
    if (!productMap[s.product_id]) productMap[s.product_id] = { units: 0, revenue: 0 };
    productMap[s.product_id].units += s.quantity;
    productMap[s.product_id].revenue += s.total_amount;
  }
  const topProducts = Object.entries(productMap).sort((a, b) => b[1].revenue - a[1].revenue).slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="h-px w-8" style={{ background: "linear-gradient(90deg, rgba(143,188,143,0.8), transparent)" }} />
            <span className="text-xs font-semibold tracking-widest uppercase" style={{ color: "#8fbc8f" }}>Analytics</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight text-interstellar">Sales History</h1>
          <p className="mt-1 text-sm text-dust">All completed transactions.</p>
        </div>
        <button onClick={fetchSales}
          className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all text-dust"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(194,140,60,0.12)" }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.3)"; (e.currentTarget as HTMLElement).style.color = "#c28c3c"; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.12)"; (e.currentTarget as HTMLElement).style.color = "#a89070"; }}>
          <RefreshCcw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: "Total Revenue", value: `₹${totalRevenue.toFixed(2)}`, icon: DollarSign, color: "#c28c3c" },
          { label: "Units Sold", value: totalUnits.toString(), icon: ShoppingBag, color: "#7eb8c9" },
          { label: "Transactions", value: sales.length.toString(), icon: TrendingUp, color: "#8fbc8f" },
        ].map((card, i) => (
          <motion.div key={card.label}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
            className="rounded-2xl p-5 tars-panel overflow-hidden relative gravity-shimmer">
            <div className="absolute top-0 inset-x-0 h-px"
              style={{ background: `linear-gradient(90deg, transparent, ${card.color}50, transparent)` }} />
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-xl"
                style={{ background: `${card.color}10`, border: `1px solid ${card.color}20` }}>
                <card.icon className="h-5 w-5" style={{ color: card.color }} />
              </div>
              <span className="text-sm text-dust">{card.label}</span>
            </div>
            <p className="text-2xl font-black" style={{ color: "#e8dcc8" }}>{card.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Top products */}
      {topProducts.length > 0 && (
        <div className="rounded-2xl overflow-hidden tars-panel">
          <div className="px-6 py-4" style={{ borderBottom: "1px solid rgba(194,140,60,0.08)" }}>
            <h2 className="font-bold" style={{ color: "#c28c3c" }}>Top Performing Products</h2>
          </div>
          <div className="p-4 space-y-2">
            {topProducts.map(([pid, data], i) => (
              <div key={pid} className="flex items-center justify-between rounded-xl px-4 py-3 transition-all"
                style={{ background: "rgba(255,255,255,0.01)", border: "1px solid rgba(194,140,60,0.06)" }}
                onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.15)"}
                onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.06)"}>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm w-5" style={{ color: "#3a2e22" }}>#{i + 1}</span>
                  <span className="font-semibold" style={{ color: "#e8dcc8" }}>{pid}</span>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <span className="text-dust">{data.units} units</span>
                  <span className="font-bold" style={{ color: "#c28c3c" }}>₹{data.revenue.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transactions */}
      <div className="overflow-hidden rounded-2xl tars-panel">
        <div className="h-px w-full" style={{ background: "linear-gradient(90deg, transparent, rgba(143,188,143,0.5), rgba(194,140,60,0.4), transparent)" }} />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead style={{ background: "rgba(194,140,60,0.03)", borderBottom: "1px solid rgba(194,140,60,0.08)" }}>
              <tr>
                {["#", "Product", "Qty", "Unit Price", "Total", "Time"].map(h => (
                  <th key={h} className="px-6 py-4 text-xs font-bold tracking-widest uppercase" style={{ color: "#5a4a38" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-dust">Loading...</td></tr>
              ) : sales.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-dust">No transactions recorded yet.</td></tr>
              ) : (
                sales.map((sale, i) => (
                  <motion.tr key={sale.id}
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.02 }}
                    style={{ borderBottom: "1px solid rgba(194,140,60,0.04)" }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "rgba(194,140,60,0.03)"}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
                    <td className="px-6 py-3 font-mono text-xs" style={{ color: "#3a2e22" }}>{sale.id}</td>
                    <td className="px-6 py-3 font-semibold" style={{ color: "#e8dcc8" }}>{sale.product_id}</td>
                    <td className="px-6 py-3 text-dust">{sale.quantity}</td>
                    <td className="px-6 py-3 text-dust">₹{sale.price_per_unit.toFixed(2)}</td>
                    <td className="px-6 py-3 font-bold" style={{ color: "#c28c3c" }}>₹{sale.total_amount.toFixed(2)}</td>
                    <td className="px-6 py-3 font-mono text-xs text-dust">{new Date(sale.sold_at).toLocaleString()}</td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
