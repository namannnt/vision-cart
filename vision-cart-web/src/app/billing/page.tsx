"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, ShoppingCart, Trash2, CheckCircle2, AlertCircle, RefreshCcw, LogOut, PackageOpen } from "lucide-react";
import Link from 'next/link';

type CartItem = {
  name: string;
  price: number;
  confidence: number;
  timestamp: string;
};

type CartState = {
  items: CartItem[];
  total: number;
  status: string;
};

export default function BillingPage() {
  const [cartState, setCartState] = useState<CartState>({ items: [], total: 0, status: "" });
  const [isConnected, setIsConnected] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let destroyed = false;

    const connectWs = () => {
      if (destroyed) return;

      const ws = new WebSocket("ws://127.0.0.1:8000/ws/cart");
      wsRef.current = ws;

      ws.onopen = () => {
        if (!destroyed) setIsConnected(true);
      };

      ws.onclose = () => {
        if (destroyed) return;
        setIsConnected(false);
        // Reconnect after 1.5s
        reconnectTimer.current = setTimeout(connectWs, 1500);
      };

      ws.onerror = () => {
        ws.close();
      };

      ws.onmessage = (event) => {
        if (destroyed) return;
        try {
          const data = JSON.parse(event.data);
          // Spread to always create new object reference → forces React re-render
          setCartState({ items: data.items ?? [], total: data.total ?? 0, status: data.status ?? "" });

          if (data.status === "Checkout Complete!") {
            setShowReceipt(true);
            setTimeout(() => setShowReceipt(false), 5000);
          }

          if (data.stock_updated) {
            fetch("/api/products", { cache: "no-store" });
          }
        } catch {
          // ignore malformed messages
        }
      };
    };

    connectWs();

    return () => {
      destroyed = true;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  const sendAction = (action: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action }));
    }
  };

  return (
    <div className="flex h-screen w-full flex-col lg:flex-row overflow-hidden p-4 gap-4 cyber-grid"
      style={{ background: "linear-gradient(135deg, #020408 0%, #050810 50%, #020510 100%)" }}>
      {/* Left Panel: Camera Feed */}
      <div className="flex-1 flex flex-col gap-4">
        <div className="flex items-center justify-between px-6 py-4 rounded-2xl"
          style={{
            background: "linear-gradient(135deg, rgba(10,13,30,0.95), rgba(6,8,20,0.98))",
            border: "1px solid rgba(99,102,241,0.2)",
            boxShadow: "0 0 30px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.04)"
          }}>
          <div className="flex items-center space-x-3">
            <div className={`relative h-3 w-3`}>
              {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />}
              <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]' : 'bg-red-500'}`} />
            </div>
            <h1 className="text-xl font-black tracking-tight text-neon-blue">
              VisionCart <span className="text-neon-purple">LIVE</span>
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-400 max-w-[300px] truncate px-3 py-1 rounded-lg"
              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
              {cartState.status || "Waiting for items..."}
            </span>
            <Link href="/login" className="flex items-center space-x-2 text-slate-400 hover:text-white transition-all px-3 py-1.5 rounded-xl"
              style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.15)" }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.12)"}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.06)"}>
              <LogOut className="h-4 w-4 text-red-400" />
              <span className="text-sm font-medium text-red-400">Exit</span>
            </Link>
          </div>
        </div>

        <div className="flex-1 overflow-hidden relative group rounded-2xl"
          style={{
            border: "1px solid rgba(99,102,241,0.2)",
            boxShadow: "0 0 60px rgba(99,102,241,0.08), 0 0 120px rgba(6,182,212,0.04)",
          }}>
          {/* Corner accents */}
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-blue-500/60 rounded-tl-2xl z-10 pointer-events-none" />
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-purple-500/60 rounded-tr-2xl z-10 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-500/60 rounded-bl-2xl z-10 pointer-events-none" />
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-blue-500/60 rounded-br-2xl z-10 pointer-events-none" />

          {/* Camera feed always visible */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="http://127.0.0.1:8000/video_feed"
            alt="Live Camera Feed"
            className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-[1.01] rounded-2xl"
            onError={(e) => {
              setTimeout(() => {
                (e.target as HTMLImageElement).src = `http://127.0.0.1:8000/video_feed?t=${Date.now()}`;
              }, 3000);
            }}
          />
          {!isConnected && (
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10 rounded-2xl pointer-events-none"
              style={{ background: "rgba(5,8,20,0.7)" }}>
              <RefreshCcw className="h-8 w-8 text-blue-500/80 mb-3 animate-spin" />
              <p className="text-slate-300 font-medium text-sm">Connecting to backend...</p>
            </div>
          )}

          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-6 pointer-events-none rounded-b-2xl">
            <div className="flex items-center space-x-2 w-fit px-3 py-1.5 rounded-full"
              style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)", backdropFilter: "blur(10px)" }}>
              <Camera className="h-4 w-4 text-blue-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-300">AI Camera Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel: Cart */}
      <div className="w-full lg:w-[400px] xl:w-[480px] flex flex-col gap-4">
        <div className="flex-1 flex flex-col overflow-hidden rounded-2xl"
          style={{
            background: "linear-gradient(145deg, rgba(10,13,30,0.97), rgba(6,8,20,0.99))",
            border: "1px solid rgba(99,102,241,0.2)",
            boxShadow: "0 0 60px rgba(99,102,241,0.08)"
          }}>
          {/* Top glow line */}
          <div className="h-px w-full" style={{ background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.8), rgba(6,182,212,0.6), transparent)" }} />

          <div className="flex items-center justify-between px-6 py-5 shrink-0"
            style={{ borderBottom: "1px solid rgba(255,255,255,0.05)", background: "rgba(99,102,241,0.04)" }}>
            <div className="flex items-center space-x-3">
              <div className="rounded-xl p-2" style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)", boxShadow: "0 0 15px rgba(99,102,241,0.2)" }}>
                <ShoppingCart className="h-6 w-6 text-indigo-400" />
              </div>
              <h2 className="text-xl font-black tracking-tight text-neon-blue">Current Bill</h2>
            </div>
            <span className="inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-bold"
              style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)", color: "#a5b4fc" }}>
              {cartState.items.length} items
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {cartState.items.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center space-y-4 text-slate-500">
                <div className="rounded-full p-6" style={{ background: "rgba(99,102,241,0.05)", border: "1px dashed rgba(99,102,241,0.2)" }}>
                  <PackageOpen className="h-12 w-12 opacity-40" />
                </div>
                <p className="font-semibold tracking-wide text-slate-400">Cart is empty</p>
                <p className="text-sm text-slate-600 text-center px-8">Place an item under the camera to automatically add it to the bill.</p>
              </div>
            ) : (
              <ul className="space-y-3 p-4">
                <AnimatePresence>
                  {cartState.items.map((item, index) => (
                    <motion.li
                      key={`${item.name}-${item.timestamp}-${index}`}
                      initial={{ opacity: 0, x: 30, scale: 0.95 }}
                      animate={{ opacity: 1, x: 0, scale: 1 }}
                      exit={{ opacity: 0, x: -30, scale: 0.95 }}
                      transition={{ type: "spring", stiffness: 300, damping: 25 }}
                      className="relative flex items-center justify-between rounded-xl p-4 overflow-hidden group/item"
                      style={{
                        background: "linear-gradient(135deg, rgba(15,18,45,0.9), rgba(10,12,30,0.95))",
                        border: "1px solid rgba(99,102,241,0.15)",
                        boxShadow: "0 4px 15px rgba(0,0,0,0.4)"
                      }}
                      onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(99,102,241,0.4)"}
                      onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = "rgba(99,102,241,0.15)"}
                    >
                      {/* Left accent bar */}
                      <div className="absolute left-0 top-0 bottom-0 w-0.5 rounded-l-xl" style={{ background: "linear-gradient(180deg, #6366f1, #06b6d4)" }} />
                      <div className="min-w-0 flex-1 pl-2">
                        <p className="font-bold text-slate-100 truncate">{item.name}</p>
                        <p className="text-xs text-slate-500 font-mono mt-0.5">
                          <span className="text-emerald-500">{Math.round(item.confidence * 100)}%</span> confidence • {item.timestamp}
                        </p>
                      </div>
                      <div className="text-right ml-4">
                        <p className="font-black text-lg text-neon-green">₹{item.price.toFixed(2)}</p>
                      </div>
                    </motion.li>
                  ))}
                </AnimatePresence>
              </ul>
            )}
          </div>

          {/* Cart Actions & Total */}
          <div className="p-6 shrink-0 relative overflow-hidden"
            style={{ borderTop: "1px solid rgba(255,255,255,0.05)", background: "rgba(5,8,20,0.8)" }}>
            <div className="absolute inset-0 pointer-events-none" style={{ background: "radial-gradient(ellipse at bottom, rgba(99,102,241,0.06), transparent 70%)" }} />

            <div className="mb-5 flex items-end justify-between relative z-10">
              <span className="text-slate-500 font-semibold uppercase tracking-widest text-xs">Total Amount</span>
              <span className="text-4xl font-black tracking-tighter text-neon-green">
                ₹{cartState.total.toFixed(2)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 relative z-10">
              <button
                onClick={() => sendAction('remove_last')}
                disabled={cartState.items.length === 0}
                className="flex items-center justify-center space-x-2 rounded-xl px-4 py-3 font-semibold text-slate-300 transition-all disabled:opacity-40 disabled:cursor-not-allowed group/btn"
                style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)" }}
                onMouseEnter={e => { if (cartState.items.length > 0) (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.12)"; }}
                onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.06)"}
              >
                <Trash2 className="h-4 w-4 text-red-400" />
                <span className="text-red-400">Remove Last</span>
              </button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => sendAction('checkout')}
                disabled={cartState.items.length === 0}
                className="relative flex items-center justify-center space-x-2 rounded-xl px-4 py-3 font-black text-white overflow-hidden disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                  boxShadow: cartState.items.length > 0 ? "0 0 25px rgba(99,102,241,0.4), 0 8px 20px rgba(0,0,0,0.5)" : "none"
                }}
              >
                {cartState.items.length > 0 && (
                  <div className="absolute inset-0 shimmer-btn" />
                )}
                <span className="relative z-10">Checkout</span>
                <CheckCircle2 className="h-5 w-5 relative z-10" />
              </motion.button>
            </div>

            <button
              onClick={() => sendAction('clear')}
              disabled={cartState.items.length === 0}
              className="mt-3 w-full text-center text-xs text-slate-600 hover:text-slate-400 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Clear Cart Completely
            </button>
          </div>
        </div>
      </div>

      {/* Receipt Overlay */}
      <AnimatePresence>
        {showReceipt && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-2xl relative overflow-hidden">
              {/* Receipt edge zig-zag pattern */}
              <div className="absolute top-0 inset-x-0 h-4 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+Cjxwb2x5Z29uIHBvaW50cz0iMCwwIDEwLDEwIDIwLDAgMjAsMjAgMCwyMCIgZmlsbD0id2hpdGUiIC8+Cjwvc3ZnPg==')] opacity-20"></div>

              <div className="mb-6 flex flex-col items-center border-b border-dashed border-slate-300 pb-6">
                <div className="mb-4 rounded-full bg-emerald-100 p-3">
                  <CheckCircle2 className="h-8 w-8 text-emerald-600" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900">Payment Success</h3>
                <p className="text-sm text-slate-500 mt-1">Thank you for shopping at VisionCart</p>
              </div>
              
              <div className="mb-6 space-y-3">
                <div className="flex justify-between text-sm text-slate-600">
                  <span>Date</span>
                  <span className="font-medium text-slate-900">{new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between text-sm text-slate-600">
                  <span>Time</span>
                  <span className="font-medium text-slate-900">{new Date().toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between text-sm text-slate-600">
                  <span>Method</span>
                  <span className="font-medium text-slate-900">VisionCart Auto</span>
                </div>
              </div>
              
              <button
                onClick={() => setShowReceipt(false)}
                className="w-full rounded-xl bg-slate-900 py-3 font-semibold text-white transition-colors hover:bg-slate-800"
              >
                Close Receipt
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
