"use client";

import { useEffect, useState } from "react";
import { PackageOpen, TrendingUp, AlertCircle, Edit, Trash2, X, Check, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
type Product = {
  id: number;
  product_id: string;
  price: number;
  stock: number;
  created_at: string;
};

export default function InventoryPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = () => {
    setLoading(true);
    fetch("/api/products")
      .then((res) => res.json())
      .then((data) => {
        setProducts(data);
        setLoading(false);
      });
  };

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ price: 0, stock: 0 });
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const startEdit = (product: Product) => {
    setEditingId(product.id);
    setEditForm({ price: product.price, stock: product.stock });
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEdit = async (id: number) => {
    setActionLoading(id);
    try {
      const res = await fetch(`/api/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editForm),
      });
      if (res.ok) {
        setEditingId(null);
        fetchProducts();
      } else {
        alert("Failed to update product");
      }
    } catch (e) {
      alert("Error updating product");
    } finally {
      setActionLoading(null);
    }
  };

  const deleteProduct = async (id: number) => {
    setConfirmDeleteId(null);
    setActionLoading(id);
    try {
      const res = await fetch(`/api/products/${id}`, {
        method: "DELETE",
      });
      const data = await res.json();
      if (res.ok && data.success) {
        fetchProducts();
      } else {
        alert(data.error || "Failed to delete product");
      }
    } catch (e) {
      alert("Network error – could not delete product");
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="h-px w-8" style={{ background: "linear-gradient(90deg, rgba(6,182,212,0.8), transparent)" }} />
            <span className="text-xs text-cyan-400 font-semibold tracking-widest uppercase">Stock Control</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight"
            style={{ background: "linear-gradient(135deg, #fff, #67e8f9)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
            Inventory Management
          </h1>
          <p className="text-slate-500 mt-1 text-sm">View and manage all registered products.</p>
        </div>
        <motion.a href="/admin/registration"
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="relative rounded-xl px-5 py-2.5 font-bold text-white overflow-hidden"
          style={{
            background: "linear-gradient(135deg, #4f46e5, #0891b2)",
            boxShadow: "0 0 20px rgba(99,102,241,0.3), 0 8px 20px rgba(0,0,0,0.4)"
          }}>
          + Add New Product
        </motion.a>
      </div>

      <div className="overflow-hidden rounded-2xl"
        style={{
          background: "linear-gradient(145deg, rgba(10,13,30,0.97), rgba(6,8,20,0.99))",
          border: "1px solid rgba(99,102,241,0.15)",
          boxShadow: "0 0 60px rgba(99,102,241,0.06)"
        }}>
        {/* Top glow */}
        <div className="h-px w-full" style={{ background: "linear-gradient(90deg, transparent, rgba(6,182,212,0.6), rgba(99,102,241,0.6), transparent)" }} />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead style={{ background: "rgba(99,102,241,0.05)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <tr>
                {["Product ID", "Status", "Price (₹)", "Stock", "Actions"].map((h, i) => (
                  <th key={h} className={`px-6 py-4 text-xs font-bold tracking-widest uppercase ${i === 4 ? "text-right" : ""}`}
                    style={{ color: "rgba(148,163,184,0.7)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/30">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <div className="flex justify-center items-center space-x-2">
                      <div className="h-3 w-3 rounded-full bg-indigo-500 animate-bounce" />
                      <div className="h-3 w-3 rounded-full bg-cyan-500 animate-bounce delay-75" />
                      <div className="h-3 w-3 rounded-full bg-purple-500 animate-bounce delay-150" />
                    </div>
                  </td>
                </tr>
              ) : products.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <PackageOpen className="mx-auto h-12 w-12 opacity-30 mb-3" />
                    <p>No products found in database.</p>
                  </td>
                </tr>
              ) : (
                products.map((product, i) => (
                  <motion.tr
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    key={product.id}
                    className="transition-colors"
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "rgba(99,102,241,0.04)"}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}
                  >
                    <td className="px-6 py-4 font-bold text-slate-200">{product.product_id}</td>
                    <td className="px-6 py-4">
                      {product.stock > 3 ? (
                        <span className="inline-flex items-center space-x-1 rounded-full px-2.5 py-1 text-xs font-semibold"
                          style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", color: "#34d399" }}>
                          <TrendingUp className="h-3 w-3" /><span>In Stock</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 rounded-full px-2.5 py-1 text-xs font-semibold"
                          style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)", color: "#f87171" }}>
                          <AlertCircle className="h-3 w-3" /><span>Low Stock</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingId === product.id ? (
                        <input
                          type="number"
                          value={editForm.price}
                          onChange={(e) => setEditForm(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
                          className="w-24 rounded-lg px-2 py-1 text-slate-100 focus:outline-none"
                          style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.4)" }}
                        />
                      ) : (
                        <span className="font-semibold text-slate-300">₹{product.price.toFixed(2)}</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingId === product.id ? (
                        <input
                          type="number"
                          value={editForm.stock}
                          onChange={(e) => setEditForm(prev => ({ ...prev, stock: parseInt(e.target.value) || 0 }))}
                          className="w-20 rounded-lg px-2 py-1 text-slate-100 focus:outline-none"
                          style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.4)" }}
                        />
                      ) : (
                        <span className={`font-mono font-bold px-2.5 py-1 rounded-lg text-sm ${product.stock <= 3 ? 'text-red-400' : 'text-slate-300'}`}
                          style={{ background: product.stock <= 3 ? "rgba(239,68,68,0.1)" : "rgba(255,255,255,0.04)", border: `1px solid ${product.stock <= 3 ? "rgba(239,68,68,0.25)" : "rgba(255,255,255,0.06)"}` }}>
                          {product.stock}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {actionLoading === product.id ? (
                          <Loader2 className="h-5 w-5 text-indigo-400 animate-spin" />
                        ) : editingId === product.id ? (
                          <>
                            <button onClick={() => saveEdit(product.id)} className="p-2 rounded-lg transition-colors"
                              style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", color: "#34d399" }}>
                              <Check className="h-4 w-4" />
                            </button>
                            <button onClick={cancelEdit} className="p-2 rounded-lg transition-colors"
                              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", color: "#94a3b8" }}>
                              <X className="h-4 w-4" />
                            </button>
                          </>
                        ) : (
                          <>
                            <button onClick={() => startEdit(product)} className="p-2 rounded-lg transition-all text-slate-500 hover:text-blue-400"
                              style={{ border: "1px solid transparent" }}
                              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(99,102,241,0.1)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(99,102,241,0.25)"; }}
                              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.borderColor = "transparent"; }}>
                              <Edit className="h-4 w-4" />
                            </button>
                            {confirmDeleteId === product.id ? (
                              <>
                                <button onClick={() => deleteProduct(product.id)}
                                  className="px-3 py-1 text-xs font-bold text-white rounded-lg transition-colors"
                                  style={{ background: "rgba(239,68,68,0.8)", border: "1px solid rgba(239,68,68,0.5)" }}>
                                  Confirm?
                                </button>
                                <button onClick={() => setConfirmDeleteId(null)} className="p-2 text-slate-400 hover:bg-slate-700 rounded-lg transition-colors">
                                  <X className="h-4 w-4" />
                                </button>
                              </>
                            ) : (
                              <button onClick={() => setConfirmDeleteId(product.id)} className="p-2 rounded-lg transition-all text-slate-500 hover:text-red-400"
                                style={{ border: "1px solid transparent" }}
                                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.1)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(239,68,68,0.25)"; }}
                                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.borderColor = "transparent"; }}>
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
