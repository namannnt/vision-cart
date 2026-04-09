"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Camera,
  ShoppingCart,
  Trash2,
  CheckCircle2,
  RefreshCcw,
  LogOut,
  PackageOpen,
  Plus,
  Minus,
  PenLine,
  X,
} from "lucide-react";
import Link from "next/link";
import dynamic from "next/dynamic";

const WormholeCanvas = dynamic(() => import("@/components/WormholeCanvas"), {
  ssr: false,
});

type CartItem = {
  name: string;
  price: number;
  confidence: number;
  timestamp: string;
  quantity: number;
};

type CartState = {
  items: CartItem[];
  total: number;
  status: string;
  stock_updated?: boolean;
};

export default function BillingPage() {
  const [cart, setCart] = useState<CartState>({
    items: [],
    total: 0,
    status: "Awaiting cargo...",
  });
  const [connected, setConnected] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);
  const [manualName, setManualName] = useState("");
  const [manualPrice, setManualPrice] = useState("");
  const [receiptData, setReceiptData] = useState<{
    date: string;
    time: string;
    total: number;
  } | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const qtyOverridesRef = useRef<Record<string, number>>({});
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const calcTotal = (items: CartItem[]) =>
    items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const connectWS = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/cart");
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };

    ws.onmessage = (event) => {
      try {
        const data: CartState = JSON.parse(event.data);
        const mergedItems = data.items.map((item) => {
          const key = item.name;
          const overrideQty = qtyOverridesRef.current[key];
          return overrideQty !== undefined
            ? { ...item, quantity: overrideQty }
            : { ...item, quantity: item.quantity ?? 1 };
        });
        setCart({
          ...data,
          items: mergedItems,
          total: calcTotal(mergedItems),
          status: data.status || "Awaiting cargo...",
        });
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimer.current = setTimeout(connectWS, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  };

  useEffect(() => {
    connectWS();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendAction = (action: string, payload?: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...payload }));
    }
  };

  const changeQty = (name: string, delta: number) => {
    setCart((prev) => {
      const updated = prev.items.map((item) => {
        if (item.name === name) {
          const newQty = Math.max(1, item.quantity + delta);
          qtyOverridesRef.current[name] = newQty;
          return { ...item, quantity: newQty };
        }
        return item;
      });
      return { ...prev, items: updated, total: calcTotal(updated) };
    });
  };

  const addManual = () => {
    const name = manualName.trim();
    const price = parseFloat(manualPrice);
    if (!name || isNaN(price) || price <= 0) return;

    setCart((prev) => {
      const existing = prev.items.find((i) => i.name === name);
      let updated: CartItem[];
      if (existing) {
        updated = prev.items.map((i) =>
          i.name === name ? { ...i, quantity: i.quantity + 1 } : i
        );
        qtyOverridesRef.current[name] =
          (qtyOverridesRef.current[name] ?? existing.quantity) + 1;
      } else {
        const newItem: CartItem = {
          name,
          price,
          confidence: 1,
          timestamp: new Date().toLocaleTimeString(),
          quantity: 1,
        };
        qtyOverridesRef.current[name] = 1;
        updated = [...prev.items, newItem];
      }
      return { ...prev, items: updated, total: calcTotal(updated) };
    });

    setManualName("");
    setManualPrice("");
    setShowManual(false);
  };

  const handleCheckout = async () => {
    const now = new Date();
    const total = cart.total;
    try {
      await fetch("/api/sales", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: cart.items, total }),
      });
    } catch {
      // proceed anyway
    }
    sendAction("checkout");
    qtyOverridesRef.current = {};
    setReceiptData({
      date: now.toLocaleDateString(),
      time: now.toLocaleTimeString(),
      total,
    });
    setShowReceipt(true);
    setCart({ items: [], total: 0, status: "Awaiting cargo..." });
  };

  const removeLast = () => {
    setCart((prev) => {
      if (prev.items.length === 0) return prev;
      const last = prev.items[prev.items.length - 1];
      delete qtyOverridesRef.current[last.name];
      const updated = prev.items.slice(0, -1);
      sendAction("remove_last");
      return { ...prev, items: updated, total: calcTotal(updated) };
    });
  };

  const clearAll = () => {
    qtyOverridesRef.current = {};
    sendAction("clear");
    setCart({ items: [], total: 0, status: "Awaiting cargo..." });
  };

  // ─── Palette ────────────────────────────────────────────────────────────────
  const amber = "#c28c3c";
  const amberBright = "#e8b84b";
  const starWhite = "#f0e6d0";
  const dust = "#8a7060";
  const panelBg = "rgba(16,10,4,0.95)";
  const green = "#8fbc8f";
  const red = "#c87060";

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        fontFamily: "'Courier New', monospace",
        background: "#0a0604",
      }}
    >
      {/* Wormhole background */}
      <div style={{ position: "fixed", inset: 0, zIndex: 0 }}>
        <WormholeCanvas />
      </div>

      {/* Vignette */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 1,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.85) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Main layout */}
      <div
        style={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          height: "100vh",
          gap: "12px",
          padding: "12px",
          boxSizing: "border-box",
        }}
      >

        {/* ── LEFT PANEL: Camera Feed ── */}
        <div
          style={{
            flex: "0 0 55%",
            display: "flex",
            flexDirection: "column",
            background: panelBg,
            border: `1px solid ${amber}`,
            borderRadius: "8px",
            backdropFilter: "blur(12px)",
            boxShadow: `0 0 32px rgba(194,140,60,0.25), inset 0 0 60px rgba(0,0,0,0.5)`,
            overflow: "hidden",
          }}
        >
          {/* Top bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "10px 16px",
              borderBottom: `1px solid rgba(194,140,60,0.3)`,
              background: "rgba(194,140,60,0.05)",
            }}
          >
            {/* Connection dot */}
            <div style={{ position: "relative", width: 10, height: 10 }}>
              <div
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: connected ? green : red,
                  boxShadow: connected ? `0 0 8px ${green}` : "none",
                }}
              />
              {connected && (
                <motion.div
                  animate={{ scale: [1, 2], opacity: [0.6, 0] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                  style={{
                    position: "absolute",
                    inset: 0,
                    borderRadius: "50%",
                    background: green,
                  }}
                />
              )}
            </div>

            <Camera size={18} color={amber} />
            <span
              style={{
                color: amberBright,
                fontWeight: "bold",
                fontSize: "15px",
                letterSpacing: "2px",
                textTransform: "uppercase",
              }}
            >
              VisionCart
            </span>

            <span
              style={{
                marginLeft: "auto",
                color: cart.status?.includes("Confirming") ? amberBright : 
                       cart.status?.includes("✅") ? green :
                       cart.status?.includes("⚠️") ? red : dust,
                fontSize: "11px",
                letterSpacing: "1px",
                fontWeight: cart.status?.includes("Confirming") ? "bold" : "normal",
              }}
            >
              {cart.status || (cart.items.length === 0 ? "Awaiting cargo..." : "Ready")}
            </span>

            <Link href="/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                  background: "rgba(200,112,96,0.15)",
                  border: `1px solid ${red}`,
                  borderRadius: "5px",
                  color: red,
                  padding: "4px 10px",
                  fontSize: "11px",
                  cursor: "pointer",
                  letterSpacing: "1px",
                }}
              >
                <LogOut size={12} />
                EXIT
              </motion.button>
            </Link>
          </div>

          {/* Camera feed area */}
          <div
            style={{
              flex: 1,
              position: "relative",
              overflow: "hidden",
              background: "#000",
            }}
          >
            {/* Corner accents */}
            {[
              { top: 8, left: 8, rotate: "0deg" },
              { top: 8, right: 8, rotate: "90deg" },
              { bottom: 8, right: 8, rotate: "180deg" },
              { bottom: 8, left: 8, rotate: "270deg" },
            ].map((pos, i) => (
              <div
                key={i}
                style={{
                  position: "absolute",
                  width: 20,
                  height: 20,
                  zIndex: 3,
                  ...pos,
                  borderTop: `2px solid ${amber}`,
                  borderLeft: `2px solid ${amber}`,
                  transform: `rotate(${pos.rotate})`,
                  pointerEvents: "none",
                }}
              />
            ))}

            {/* Camera image */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="http://127.0.0.1:8000/video_feed"
              alt="Camera Feed"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                display: "block",
              }}
            />

            {/* Scan line */}
            <motion.div
              animate={{ top: ["0%", "100%", "0%"] }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                height: "2px",
                background: `linear-gradient(90deg, transparent, ${amber}, transparent)`,
                opacity: 0.6,
                zIndex: 4,
                pointerEvents: "none",
              }}
            />

            {/* AI Scanner badge */}
            <div
              style={{
                position: "absolute",
                bottom: 12,
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 5,
                background: "rgba(16,10,4,0.8)",
                border: `1px solid ${amber}`,
                borderRadius: "20px",
                padding: "4px 14px",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <motion.div
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: amberBright,
                }}
              />
              <span
                style={{
                  color: amberBright,
                  fontSize: "10px",
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                AI Scanner Active
              </span>
            </div>
          </div>
        </div>


        {/* ── RIGHT PANEL: Cart ── */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            background: panelBg,
            border: `1px solid ${amber}`,
            borderRadius: "8px",
            backdropFilter: "blur(12px)",
            boxShadow: `0 0 32px rgba(194,140,60,0.2), inset 0 0 60px rgba(0,0,0,0.5)`,
            overflow: "hidden",
          }}
        >
          {/* Cart header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "10px 16px",
              borderBottom: `1px solid rgba(194,140,60,0.3)`,
              background: "rgba(194,140,60,0.05)",
            }}
          >
            <ShoppingCart size={18} color={amber} />
            <span
              style={{
                color: amberBright,
                fontWeight: "bold",
                fontSize: "14px",
                letterSpacing: "2px",
                textTransform: "uppercase",
              }}
            >
              Current Bill
            </span>

            {cart.items.length > 0 && (
              <span
                style={{
                  background: amber,
                  color: "#0a0604",
                  borderRadius: "10px",
                  padding: "1px 8px",
                  fontSize: "11px",
                  fontWeight: "bold",
                }}
              >
                {cart.items.length}
              </span>
            )}

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowManual((v) => !v)}
              style={{
                marginLeft: "auto",
                display: "flex",
                alignItems: "center",
                gap: "5px",
                background: showManual
                  ? `rgba(194,140,60,0.2)`
                  : "rgba(194,140,60,0.08)",
                border: `1px solid ${amber}`,
                borderRadius: "5px",
                color: amber,
                padding: "4px 10px",
                fontSize: "11px",
                cursor: "pointer",
                letterSpacing: "1px",
              }}
            >
              <PenLine size={12} />
              MANUAL
            </motion.button>
          </div>

          {/* Manual entry form */}
          <AnimatePresence>
            {showManual && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                style={{
                  overflow: "hidden",
                  borderBottom: `1px solid rgba(194,140,60,0.3)`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    padding: "10px 16px",
                    background: "rgba(194,140,60,0.05)",
                    alignItems: "center",
                  }}
                >
                  <input
                    value={manualName}
                    onChange={(e) => setManualName(e.target.value)}
                    placeholder="Product name"
                    style={{
                      flex: 2,
                      background: "rgba(16,10,4,0.8)",
                      border: `1px solid rgba(194,140,60,0.4)`,
                      borderRadius: "4px",
                      color: starWhite,
                      padding: "6px 10px",
                      fontSize: "12px",
                      outline: "none",
                    }}
                  />
                  <input
                    value={manualPrice}
                    onChange={(e) => setManualPrice(e.target.value)}
                    placeholder="Price"
                    type="number"
                    min="0"
                    style={{
                      flex: 1,
                      background: "rgba(16,10,4,0.8)",
                      border: `1px solid rgba(194,140,60,0.4)`,
                      borderRadius: "4px",
                      color: starWhite,
                      padding: "6px 10px",
                      fontSize: "12px",
                      outline: "none",
                    }}
                  />
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={addManual}
                    style={{
                      background: `linear-gradient(135deg, ${amber}, ${amberBright})`,
                      border: "none",
                      borderRadius: "4px",
                      color: "#0a0604",
                      padding: "6px 14px",
                      fontSize: "12px",
                      fontWeight: "bold",
                      cursor: "pointer",
                      letterSpacing: "1px",
                    }}
                  >
                    ADD
                  </motion.button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Cart items list */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "8px",
              scrollbarWidth: "thin",
              scrollbarColor: `${amber} transparent`,
            }}
          >
            <AnimatePresence>
              {cart.items.length === 0 ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100%",
                    gap: "12px",
                    color: dust,
                    paddingTop: "60px",
                  }}
                >
                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <PackageOpen size={48} color={dust} />
                  </motion.div>
                  <span style={{ fontSize: "12px", letterSpacing: "2px" }}>
                    NO ITEMS DETECTED
                  </span>
                </motion.div>
              ) : (
                cart.items.map((item, idx) => (
                  <motion.div
                    key={item.name + idx}
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -30 }}
                    transition={{ duration: 0.25 }}
                    whileHover={{
                      borderColor: amberBright,
                      boxShadow: `0 0 12px rgba(232,184,75,0.2)`,
                    }}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      background: "rgba(194,140,60,0.05)",
                      border: `1px solid rgba(194,140,60,0.2)`,
                      borderRadius: "6px",
                      marginBottom: "6px",
                      padding: "8px 10px",
                      position: "relative",
                      overflow: "hidden",
                    }}
                  >
                    {/* Left accent bar */}
                    <div
                      style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: "3px",
                        background: `linear-gradient(180deg, ${amber}, ${amberBright})`,
                        borderRadius: "3px 0 0 3px",
                      }}
                    />

                    {/* Item info */}
                    <div style={{ flex: 1, paddingLeft: "6px" }}>
                      <div
                        style={{
                          color: starWhite,
                          fontSize: "13px",
                          fontWeight: "bold",
                          letterSpacing: "0.5px",
                        }}
                      >
                        {item.name}
                      </div>
                      <div
                        style={{
                          display: "flex",
                          gap: "10px",
                          marginTop: "2px",
                        }}
                      >
                        <span style={{ color: green, fontSize: "10px" }}>
                          {Math.round(item.confidence * 100)}% match
                        </span>
                        <span style={{ color: dust, fontSize: "10px" }}>
                          {item.timestamp}
                        </span>
                      </div>
                    </div>

                    {/* Quantity controls */}
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <motion.button
                        whileTap={{ scale: 0.85 }}
                        onClick={() => changeQty(item.name, -1)}
                        style={{
                          width: 22,
                          height: 22,
                          borderRadius: "4px",
                          background: `rgba(200,112,96,0.2)`,
                          border: `1px solid ${red}`,
                          color: red,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          padding: 0,
                        }}
                      >
                        <Minus size={12} />
                      </motion.button>
                      <span
                        style={{
                          color: starWhite,
                          fontSize: "13px",
                          fontWeight: "bold",
                          minWidth: "20px",
                          textAlign: "center",
                        }}
                      >
                        {item.quantity}
                      </span>
                      <motion.button
                        whileTap={{ scale: 0.85 }}
                        onClick={() => changeQty(item.name, 1)}
                        style={{
                          width: 22,
                          height: 22,
                          borderRadius: "4px",
                          background: `rgba(143,188,143,0.2)`,
                          border: `1px solid ${green}`,
                          color: green,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          padding: 0,
                        }}
                      >
                        <Plus size={12} />
                      </motion.button>
                    </div>

                    {/* Price */}
                    <div
                      style={{
                        color: amber,
                        fontSize: "14px",
                        fontWeight: "bold",
                        minWidth: "60px",
                        textAlign: "right",
                      }}
                    >
                      ₹{(item.price * item.quantity).toFixed(2)}
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>


          {/* Bottom section */}
          <div
            style={{
              borderTop: `1px solid rgba(194,140,60,0.3)`,
              padding: "12px 16px",
              background: "rgba(194,140,60,0.04)",
            }}
          >
            {/* Total */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "12px",
              }}
            >
              <span
                style={{
                  color: dust,
                  fontSize: "12px",
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                Total
              </span>
              <span
                style={{
                  color: amberBright,
                  fontSize: "26px",
                  fontWeight: "bold",
                  letterSpacing: "1px",
                }}
              >
                ₹{cart.total.toFixed(2)}
              </span>
            </div>

            {/* Action buttons */}
            <div style={{ display: "flex", gap: "8px" }}>
              {/* Remove Last */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={removeLast}
                disabled={cart.items.length === 0}
                style={{
                  flex: 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "5px",
                  background: "rgba(200,112,96,0.1)",
                  border: `1px solid ${red}`,
                  borderRadius: "5px",
                  color: red,
                  padding: "8px",
                  fontSize: "11px",
                  cursor: cart.items.length === 0 ? "not-allowed" : "pointer",
                  opacity: cart.items.length === 0 ? 0.4 : 1,
                  letterSpacing: "1px",
                }}
              >
                <RefreshCcw size={12} />
                REMOVE LAST
              </motion.button>

              {/* Checkout */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleCheckout}
                disabled={cart.items.length === 0}
                style={{
                  flex: 2,
                  position: "relative",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  background:
                    cart.items.length === 0
                      ? "rgba(194,140,60,0.1)"
                      : `linear-gradient(135deg, #8b6914, ${amberBright}, #8b6914)`,
                  border: `1px solid ${amberBright}`,
                  borderRadius: "5px",
                  color: cart.items.length === 0 ? dust : "#0a0604",
                  padding: "8px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  cursor: cart.items.length === 0 ? "not-allowed" : "pointer",
                  opacity: cart.items.length === 0 ? 0.4 : 1,
                  letterSpacing: "2px",
                }}
              >
                {cart.items.length > 0 && (
                  <motion.div
                    animate={{ x: ["-100%", "200%"] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    style={{
                      position: "absolute",
                      top: 0,
                      bottom: 0,
                      width: "40%",
                      background:
                        "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
                      pointerEvents: "none",
                    }}
                  />
                )}
                <CheckCircle2 size={14} />
                CHECKOUT
              </motion.button>

              {/* Clear All */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={clearAll}
                disabled={cart.items.length === 0}
                style={{
                  flex: 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "5px",
                  background: "rgba(200,112,96,0.08)",
                  border: `1px solid rgba(200,112,96,0.5)`,
                  borderRadius: "5px",
                  color: red,
                  padding: "8px",
                  fontSize: "11px",
                  cursor: cart.items.length === 0 ? "not-allowed" : "pointer",
                  opacity: cart.items.length === 0 ? 0.4 : 1,
                  letterSpacing: "1px",
                }}
              >
                <Trash2 size={12} />
                CLEAR
              </motion.button>
            </div>
          </div>
        </div>
      </div>


      {/* ── RECEIPT OVERLAY ── */}
      <AnimatePresence>
        {showReceipt && receiptData && (
          <motion.div
            key="receipt"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 50,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(0,0,0,0.75)",
              backdropFilter: "blur(8px)",
            }}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 20 }}
              style={{
                background: panelBg,
                border: `1px solid ${amber}`,
                borderRadius: "10px",
                padding: "32px 40px",
                minWidth: "320px",
                boxShadow: `0 0 60px rgba(194,140,60,0.4)`,
                position: "relative",
              }}
            >
              {/* Horizon lines */}
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  height: "3px",
                  background: `linear-gradient(90deg, transparent, ${amber}, transparent)`,
                  borderRadius: "10px 10px 0 0",
                }}
              />
              <div
                style={{
                  position: "absolute",
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: "3px",
                  background: `linear-gradient(90deg, transparent, ${amber}, transparent)`,
                  borderRadius: "0 0 10px 10px",
                }}
              />

              {/* Close button */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setShowReceipt(false)}
                style={{
                  position: "absolute",
                  top: 12,
                  right: 12,
                  background: "transparent",
                  border: `1px solid rgba(194,140,60,0.4)`,
                  borderRadius: "4px",
                  color: dust,
                  cursor: "pointer",
                  padding: "3px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <X size={14} />
              </motion.button>

              {/* Icon */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  marginBottom: "16px",
                }}
              >
                <motion.div
                  animate={{ boxShadow: [`0 0 20px ${green}`, `0 0 40px ${green}`, `0 0 20px ${green}`] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  style={{ borderRadius: "50%", padding: "4px" }}
                >
                  <CheckCircle2 size={48} color={green} />
                </motion.div>
              </div>

              {/* Heading */}
              <h2
                style={{
                  textAlign: "center",
                  fontSize: "22px",
                  fontWeight: "bold",
                  letterSpacing: "3px",
                  textTransform: "uppercase",
                  background: `linear-gradient(135deg, ${amber}, ${amberBright})`,
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  marginBottom: "24px",
                }}
              >
                Payment Done
              </h2>

              {/* Receipt rows */}
              {[
                { label: "Date", value: receiptData.date },
                { label: "Time", value: receiptData.time },
                { label: "Total", value: `₹${receiptData.total.toFixed(2)}` },
              ].map((row) => (
                <div
                  key={row.label}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "8px 0",
                    borderBottom: `1px solid rgba(194,140,60,0.15)`,
                  }}
                >
                  <span
                    style={{
                      color: dust,
                      fontSize: "12px",
                      letterSpacing: "1px",
                      textTransform: "uppercase",
                    }}
                  >
                    {row.label}
                  </span>
                  <span
                    style={{
                      color: row.label === "Total" ? amberBright : starWhite,
                      fontSize: row.label === "Total" ? "18px" : "13px",
                      fontWeight: row.label === "Total" ? "bold" : "normal",
                    }}
                  >
                    {row.value}
                  </span>
                </div>
              ))}

              {/* Close button bottom */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setShowReceipt(false)}
                style={{
                  marginTop: "20px",
                  width: "100%",
                  background: `linear-gradient(135deg, #8b6914, ${amberBright}, #8b6914)`,
                  border: "none",
                  borderRadius: "5px",
                  color: "#0a0604",
                  padding: "10px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  cursor: "pointer",
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                Close
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
