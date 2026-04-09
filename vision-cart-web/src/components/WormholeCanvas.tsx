"use client";

import { useEffect, useRef } from "react";

export default function WormholeCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let W = window.innerWidth;
    let H = window.innerHeight;
    canvas.width = W;
    canvas.height = H;

    const resize = () => {
      W = window.innerWidth; H = window.innerHeight;
      canvas.width = W; canvas.height = H;
    };
    window.addEventListener("resize", resize);

    // ── Stars ──
    const STAR_COUNT = 300;
    const stars = Array.from({ length: STAR_COUNT }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.4 + 0.2,
      alpha: Math.random(),
      speed: Math.random() * 0.004 + 0.001,
      phase: Math.random() * Math.PI * 2,
      amber: Math.random() < 0.08,
    }));

    // ── Dust particles ──
    const DUST_COUNT = 80;
    const dust = Array.from({ length: DUST_COUNT }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 60 + 20,
      alpha: Math.random() * 0.04 + 0.01,
      vx: (Math.random() - 0.5) * 0.08,
      vy: (Math.random() - 0.5) * 0.08,
      hue: Math.random() < 0.5 ? 35 : 220,
    }));

    // ── Wormhole rings ──
    const RING_COUNT = 18;
    const rings = Array.from({ length: RING_COUNT }, (_, i) => ({
      baseR: 40 + i * 28,
      speed: (i % 2 === 0 ? 1 : -1) * (0.0003 + i * 0.00008),
      angle: (i / RING_COUNT) * Math.PI * 2,
      alpha: 0.04 + (1 - i / RING_COUNT) * 0.18,
      width: 0.5 + (1 - i / RING_COUNT) * 1.5,
      segments: 3 + i * 2,
    }));

    // ── Accretion disk particles ──
    const ACCRETION_COUNT = 200;
    const accretion = Array.from({ length: ACCRETION_COUNT }, (_, i) => {
      const angle = (i / ACCRETION_COUNT) * Math.PI * 2;
      const r = 55 + Math.random() * 80;
      return {
        angle, r,
        speed: (0.002 + Math.random() * 0.003) * (r < 90 ? 1.5 : 1),
        alpha: 0.3 + Math.random() * 0.7,
        size: Math.random() * 2 + 0.5,
        color: Math.random() < 0.6 ? [255, 200, 80] : Math.random() < 0.5 ? [255, 240, 180] : [200, 120, 40],
        yScale: 0.28 + Math.random() * 0.08,
      };
    });

    // ── Lens flare streaks ──
    const STREAK_COUNT = 12;
    const streaks = Array.from({ length: STREAK_COUNT }, (_, i) => ({
      angle: (i / STREAK_COUNT) * Math.PI * 2,
      len: 60 + Math.random() * 120,
      alpha: 0.05 + Math.random() * 0.12,
      speed: 0.0005 + Math.random() * 0.001,
      phase: Math.random() * Math.PI * 2,
    }));

    // ── Shooting stars ──
    const shootingStars: { x: number; y: number; vx: number; vy: number; len: number; alpha: number; life: number; maxLife: number }[] = [];
    let shootTimer = 0;

    let t = 0;
    let raf: number;

    const draw = () => {
      t += 0.016;
      ctx.clearRect(0, 0, W, H);

      const cx = W / 2, cy = H / 2;

      // ── Deep space background ──
      const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * 0.8);
      bg.addColorStop(0, "rgba(12,8,3,1)");
      bg.addColorStop(0.3, "rgba(8,5,2,1)");
      bg.addColorStop(0.7, "rgba(4,3,1,1)");
      bg.addColorStop(1, "rgba(2,1,0,1)");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);

      // ── Dust clouds ──
      for (const d of dust) {
        d.x += d.vx; d.y += d.vy;
        if (d.x < -d.r) d.x = W + d.r;
        if (d.x > W + d.r) d.x = -d.r;
        if (d.y < -d.r) d.y = H + d.r;
        if (d.y > H + d.r) d.y = -d.r;
        const dg = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r);
        dg.addColorStop(0, `hsla(${d.hue},60%,40%,${d.alpha})`);
        dg.addColorStop(1, "transparent");
        ctx.fillStyle = dg;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fill();
      }

      // ── Stars ──
      for (const s of stars) {
        const a = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * s.speed * 60 + s.phase));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.amber
          ? `rgba(255,200,100,${a * s.alpha})`
          : `rgba(255,248,230,${a * s.alpha})`;
        ctx.fill();
        // Bright stars get a cross flare
        if (s.r > 1.1) {
          ctx.strokeStyle = s.amber
            ? `rgba(255,200,100,${a * s.alpha * 0.4})`
            : `rgba(255,248,230,${a * s.alpha * 0.3})`;
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(s.x - s.r * 3, s.y); ctx.lineTo(s.x + s.r * 3, s.y);
          ctx.moveTo(s.x, s.y - s.r * 3); ctx.lineTo(s.x, s.y + s.r * 3);
          ctx.stroke();
        }
      }

      // ── Shooting stars ──
      shootTimer += 0.016;
      if (shootTimer > 3 + Math.random() * 4) {
        shootTimer = 0;
        const edge = Math.random();
        let sx = 0, sy = 0;
        if (edge < 0.25) { sx = Math.random() * W; sy = 0; }
        else if (edge < 0.5) { sx = W; sy = Math.random() * H; }
        else if (edge < 0.75) { sx = Math.random() * W; sy = H; }
        else { sx = 0; sy = Math.random() * H; }
        const angle = Math.atan2(cy - sy, cx - sx) + (Math.random() - 0.5) * 0.8;
        const speed = 4 + Math.random() * 6;
        shootingStars.push({
          x: sx, y: sy,
          vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
          len: 80 + Math.random() * 120,
          alpha: 0.8 + Math.random() * 0.2,
          life: 0, maxLife: 60 + Math.random() * 40,
        });
      }
      for (let i = shootingStars.length - 1; i >= 0; i--) {
        const ss = shootingStars[i];
        ss.x += ss.vx; ss.y += ss.vy; ss.life++;
        const progress = ss.life / ss.maxLife;
        const a = ss.alpha * (1 - progress);
        const grad = ctx.createLinearGradient(ss.x, ss.y, ss.x - ss.vx * (ss.len / 5), ss.y - ss.vy * (ss.len / 5));
        grad.addColorStop(0, `rgba(255,248,230,${a})`);
        grad.addColorStop(0.3, `rgba(255,220,140,${a * 0.5})`);
        grad.addColorStop(1, "transparent");
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(ss.x, ss.y);
        ctx.lineTo(ss.x - ss.vx * (ss.len / 5), ss.y - ss.vy * (ss.len / 5));
        ctx.stroke();
        if (ss.life >= ss.maxLife) shootingStars.splice(i, 1);
      }

      // ── Wormhole outer glow ──
      const outerGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 520);
      outerGlow.addColorStop(0, "rgba(194,140,60,0.0)");
      outerGlow.addColorStop(0.3, "rgba(194,140,60,0.06)");
      outerGlow.addColorStop(0.55, "rgba(120,80,20,0.04)");
      outerGlow.addColorStop(0.75, "rgba(60,40,10,0.02)");
      outerGlow.addColorStop(1, "transparent");
      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, 520, 0, Math.PI * 2);
      ctx.fill();

      // ── Wormhole rings ──
      for (const ring of rings) {
        ring.angle += ring.speed;
        const pulse = 1 + 0.03 * Math.sin(t * 0.8 + ring.baseR * 0.05);
        const r = ring.baseR * pulse;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(ring.angle);
        ctx.scale(1, 0.35);
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(194,140,60,${ring.alpha * (0.7 + 0.3 * Math.sin(t + ring.baseR))})`;
        ctx.lineWidth = ring.width;
        ctx.stroke();
        // Dashed segments for some rings
        if (ring.segments > 5) {
          ctx.setLineDash([r * 0.15, r * 0.1]);
          ctx.strokeStyle = `rgba(255,220,140,${ring.alpha * 0.3})`;
          ctx.lineWidth = ring.width * 0.5;
          ctx.beginPath();
          ctx.arc(0, 0, r * 0.98, 0, Math.PI * 2);
          ctx.stroke();
          ctx.setLineDash([]);
        }
        ctx.restore();
      }

      // ── Lens flare streaks ──
      for (const streak of streaks) {
        streak.angle += streak.speed;
        const a = streak.alpha * (0.5 + 0.5 * Math.sin(t * 0.5 + streak.phase));
        const x1 = cx + Math.cos(streak.angle) * 50;
        const y1 = cy + Math.sin(streak.angle) * 18;
        const x2 = cx + Math.cos(streak.angle) * (50 + streak.len);
        const y2 = cy + Math.sin(streak.angle) * (18 + streak.len * 0.35);
        const sg = ctx.createLinearGradient(x1, y1, x2, y2);
        sg.addColorStop(0, `rgba(255,240,180,${a})`);
        sg.addColorStop(0.4, `rgba(194,140,60,${a * 0.6})`);
        sg.addColorStop(1, "transparent");
        ctx.strokeStyle = sg;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
        ctx.stroke();
      }

      // ── Accretion disk ──
      ctx.save();
      ctx.translate(cx, cy);
      for (const p of accretion) {
        p.angle += p.speed;
        const px = Math.cos(p.angle) * p.r;
        const py = Math.sin(p.angle) * p.r * p.yScale;
        const dist = Math.sqrt(px * px + py * py);
        const fade = Math.max(0, 1 - Math.abs(dist - 90) / 60);
        const a = p.alpha * fade * (0.6 + 0.4 * Math.sin(t * 2 + p.angle * 3));
        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color[0]},${p.color[1]},${p.color[2]},${a})`;
        ctx.fill();
      }
      ctx.restore();

      // ── Accretion disk glow band ──
      ctx.save();
      ctx.translate(cx, cy);
      ctx.scale(1, 0.3);
      const diskGlow = ctx.createRadialGradient(0, 0, 40, 0, 0, 160);
      diskGlow.addColorStop(0, "rgba(255,220,140,0.0)");
      diskGlow.addColorStop(0.35, "rgba(255,200,80,0.12)");
      diskGlow.addColorStop(0.55, "rgba(194,140,60,0.18)");
      diskGlow.addColorStop(0.7, "rgba(140,90,30,0.08)");
      diskGlow.addColorStop(1, "transparent");
      ctx.fillStyle = diskGlow;
      ctx.beginPath();
      ctx.arc(0, 0, 160, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // ── Wormhole core — bright center ──
      const coreSize = 45 + 3 * Math.sin(t * 1.2);
      const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreSize);
      coreGrad.addColorStop(0, "rgba(255,255,255,0.95)");
      coreGrad.addColorStop(0.15, "rgba(255,240,180,0.85)");
      coreGrad.addColorStop(0.35, "rgba(255,200,80,0.6)");
      coreGrad.addColorStop(0.6, "rgba(194,140,60,0.3)");
      coreGrad.addColorStop(0.85, "rgba(80,50,15,0.1)");
      coreGrad.addColorStop(1, "transparent");
      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, coreSize, 0, Math.PI * 2);
      ctx.fill();

      // ── Event horizon — black hole center ──
      const ehSize = 18 + 1.5 * Math.sin(t * 0.7);
      const ehGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, ehSize);
      ehGrad.addColorStop(0, "rgba(0,0,0,1)");
      ehGrad.addColorStop(0.6, "rgba(2,1,0,0.95)");
      ehGrad.addColorStop(1, "transparent");
      ctx.fillStyle = ehGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, ehSize, 0, Math.PI * 2);
      ctx.fill();

      // ── Gravitational lensing — light bend arcs ──
      ctx.save();
      ctx.translate(cx, cy);
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * Math.PI * 2 + t * 0.05;
        const r1 = 22, r2 = 55;
        ctx.beginPath();
        ctx.arc(0, 0, r1 + (r2 - r1) * 0.5, a - 0.4, a + 0.4);
        ctx.strokeStyle = `rgba(255,240,180,${0.15 + 0.1 * Math.sin(t + i)})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
      ctx.restore();

      // ── Horizon line across screen ──
      const horizonY = cy + 2 * Math.sin(t * 0.3);
      const hg = ctx.createLinearGradient(0, horizonY, W, horizonY);
      hg.addColorStop(0, "transparent");
      hg.addColorStop(0.1, "rgba(194,140,60,0.08)");
      hg.addColorStop(0.35, "rgba(255,220,140,0.35)");
      hg.addColorStop(0.5, `rgba(255,248,230,${0.5 + 0.3 * Math.sin(t * 0.5)})`);
      hg.addColorStop(0.65, "rgba(255,220,140,0.35)");
      hg.addColorStop(0.9, "rgba(194,140,60,0.08)");
      hg.addColorStop(1, "transparent");
      ctx.strokeStyle = hg;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, horizonY); ctx.lineTo(W, horizonY);
      ctx.stroke();

      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none"
      style={{ zIndex: 0 }} />
  );
}
