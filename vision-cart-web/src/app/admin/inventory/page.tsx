"use client";

import { useEffect, useState } from "react";
import { PackageOpen, TrendingUp, AlertCircle, Edit, Trash2, X, Check, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

type Product = { id: number; product_id: string; price: number; stock: number; created_at: string; };

export default function InventoryPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ price: 0, stock: 0 });
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => { fetchProducts(); }, []);

  const fetchProducts = () => {
    setLoading(true);
    fetch("/api/products").then(r => r.json()).then(d => { setProducts(d); setLoading(false); });
  };

  const startEdit = (p: Product) => { setEditingId(p.id); setEditForm({ price: p.price, stock: p.stock }); };
  const cancelEdit = () => setEditingId(null);

  const saveEdit = async (id: number) => {
    if (editForm.price < 0 || editForm.stock < 0) { alert("Values cannot be negative."); return; }
    setActionLoading(id);
    try {
      const res = await fetch(`/api/products/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(editForm) });
      if (res.ok) { setEditingId(null); fetchProducts(); } else alert("Failed to update.");
    } finally { setActionLoading(null); }
  };

  const deleteProduct = async (id: number) => {
    setConfirmDeleteId(null); setActionLoading(id);
    try {
      const res = await fetch(`/api/products/${id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok && data.success) fetchProducts(); else alert(data.error || "Failed to delete.");
    } finally { setActionLoading(null); }
  };

  const filtered = products.filter(p => p.product_id.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="h-px w-8" style={{ background: "linear-gradient(90deg, rgba(126,184,201,0.8), transparent)" }} />
            <span className="text-xs font-semibold tracking-widest uppercase" style={{ color: "#7eb8c9" }}>Inventory</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight text-interstellar">Products</h1>
          <p className="mt-1 text-sm text-dust">All registered products and stock levels.</p>
        </div>
        <motion.a href="/admin/registration" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
          className="relative rounded-xl px-5 py-2.5 font-bold overflow-hidden"
          style={{ background: "linear-gradient(135deg, #6b4010, #c28c3c)", color: "#f0e6d0", boxShadow: "0 0 20px rgba(194,140,60,0.25)" }}>
          + Register Product
        </motion.a>
      </div>

      {/* Search */}
      <input type="text" placeholder="Search products..." value={search} onChange={e => setSearch(e.target.value)}
        className="w-full rounded-xl px-4 py-3 placeholder:text-stone-700 focus:outline-none transition-all"
        style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(194,140,60,0.12)", color: "#e8dcc8" }}
        onFocus={e => (e.target.style.borderColor = "rgba(194,140,60,0.4)")}
        onBlur={e => (e.target.style.borderColor = "rgba(194,140,60,0.12)")} />

      {/* Table */}
      <div className="overflow-hidden rounded-2xl tars-panel">
        <div className="h-px w-full" style={{ background: "linear-gradient(90deg, transparent, rgba(126,184,201,0.5), rgba(194,140,60,0.4), transparent)" }} />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead style={{ background: "rgba(194,140,60,0.04)", borderBottom: "1px solid rgba(194,140,60,0.08)" }}>
              <tr>
                {["Product ID", "Status", "Price (₹)", "Stock", "Actions"].map((h, i) => (
                  <th key={h} className={`px-6 py-4 text-xs font-bold tracking-widest uppercase ${i === 4 ? "text-right" : ""}`}
                    style={{ color: "#5a4a38" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center">
                  <div className="flex justify-center items-center space-x-2">
                    {["#c28c3c", "#7eb8c9", "#8fbc8f"].map((c, i) => (
                      <div key={i} className="h-2.5 w-2.5 rounded-full animate-bounce" style={{ background: c, animationDelay: `${i * 0.1}s` }} />
                    ))}
                  </div>
                </td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-dust">
                  <PackageOpen className="mx-auto h-10 w-10 opacity-20 mb-3" />
                  <p>{search ? "No matching products." : "No products registered."}</p>
                </td></tr>
              ) : (
                filtered.map((product, i) => (
                  <motion.tr key={product.id}
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
                    style={{ borderBottom: "1px solid rgba(194,140,60,0.05)" }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "rgba(194,140,60,0.03)"}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
                    <td className="px-6 py-4 font-bold" style={{ color: "#e8dcc8" }}>{product.product_id}</td>
                    <td className="px-6 py-4">
                      {product.stock > 3 ? (
                        <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold"
                          style={{ background: "rgba(143,188,143,0.08)", border: "1px solid rgba(143,188,143,0.2)", color: "#8fbc8f" }}>
                          <TrendingUp className="h-3 w-3" /> In Stock
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold"
                          style={{ background: "rgba(200,112,96,0.08)", border: "1px solid rgba(200,112,96,0.2)", color: "#c87060" }}>
                          <AlertCircle className="h-3 w-3" /> Low Stock
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingId === product.id ? (
                        <input type="number" value={editForm.price} min="0"
                          onChange={e => setEditForm(p => ({ ...p, price: parseFloat(e.target.value) || 0 }))}
                          className="w-24 rounded-lg px-2 py-1 focus:outline-none"
                          style={{ background: "rgba(194,140,60,0.08)", border: "1px solid rgba(194,140,60,0.3)", color: "#e8dcc8" }} />
                      ) : (
                        <span className="font-semibold text-dust">₹{product.price.toFixed(2)}</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingId === product.id ? (
                        <input type="number" value={editForm.stock} min="0"
                          onChange={e => setEditForm(p => ({ ...p, stock: parseInt(e.target.value) || 0 }))}
                          className="w-20 rounded-lg px-2 py-1 focus:outline-none"
                          style={{ background: "rgba(194,140,60,0.08)", border: "1px solid rgba(194,140,60,0.3)", color: "#e8dcc8" }} />
                      ) : (
                        <span className="font-mono font-bold px-2.5 py-1 rounded-lg text-sm"
                          style={{
                            background: product.stock <= 3 ? "rgba(200,112,96,0.08)" : "rgba(255,255,255,0.03)",
                            border: `1px solid ${product.stock <= 3 ? "rgba(200,112,96,0.2)" : "rgba(194,140,60,0.08)"}`,
                            color: product.stock <= 3 ? "#c87060" : "#a89070",
                          }}>
                          {product.stock}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {actionLoading === product.id ? (
                          <Loader2 className="h-5 w-5 animate-spin text-dust" />
                        ) : editingId === product.id ? (
                          <>
                            <button onClick={() => saveEdit(product.id)} className="p-2 rounded-lg transition-colors"
                              style={{ background: "rgba(143,188,143,0.08)", border: "1px solid rgba(143,188,143,0.2)", color: "#8fbc8f" }}>
                              <Check className="h-4 w-4" />
                            </button>
                            <button onClick={cancelEdit} className="p-2 rounded-lg transition-colors"
                              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", color: "#5a4a38" }}>
                              <X className="h-4 w-4" />
                            </button>
                          </>
                        ) : (
                          <>
                            <button onClick={() => startEdit(product)} className="p-2 rounded-lg transition-all"
                              style={{ color: "#5a4a38", border: "1px solid transparent" }}
                              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(194,140,60,0.08)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(194,140,60,0.2)"; (e.currentTarget as HTMLElement).style.color = "#c28c3c"; }}
                              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.borderColor = "transparent"; (e.currentTarget as HTMLElement).style.color = "#5a4a38"; }}>
                              <Edit className="h-4 w-4" />
                            </button>
                            {confirmDeleteId === product.id ? (
                              <>
                                <button onClick={() => deleteProduct(product.id)}
                                  className="px-3 py-1 text-xs font-bold rounded-lg"
                                  style={{ background: "rgba(200,112,96,0.7)", color: "#f0e6d0" }}>
                                  Confirm?
                                </button>
                                <button onClick={() => setConfirmDeleteId(null)} className="p-2 rounded-lg"
                                  style={{ color: "#5a4a38" }}>
                                  <X className="h-4 w-4" />
                                </button>
                              </>
                            ) : (
                              <button onClick={() => setConfirmDeleteId(product.id)} className="p-2 rounded-lg transition-all"
                                style={{ color: "#5a4a38", border: "1px solid transparent" }}
                                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(200,112,96,0.08)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(200,112,96,0.2)"; (e.currentTarget as HTMLElement).style.color = "#c87060"; }}
                                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.borderColor = "transparent"; (e.currentTarget as HTMLElement).style.color = "#5a4a38"; }}>
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    </td>
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
