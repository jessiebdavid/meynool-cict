import { useCallback, useEffect, useRef, useState } from 'react';

/* ------------------------------------------------------------------ *
 * Deterministic helpers
 * ------------------------------------------------------------------ */
function seeded(seed: number): number {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}

/* ------------------------------------------------------------------ *
 * Small filled artworks
 * ------------------------------------------------------------------ */
function Firefly({ size }: { size: number }) {
  return (
    <svg width={size * 3} height={size * 3} viewBox={`${-size * 1.5} ${-size * 1.5} ${size * 3} ${size * 3}`} aria-hidden="true" focusable="false">
      <circle cx="0" cy="0" r={size * 1.7} fill="rgba(215,166,75,.14)" />
      <circle cx="0" cy="0" r={size * 0.8} fill="rgba(215,166,75,.75)" />
      <circle cx="0" cy="0" r={size * 0.32} fill="#F5EBD3" opacity=".9" />
    </svg>
  );
}

function Petal({ size }: { size: number }) {
  const w = size;
  const h = size * 1.35;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true" focusable="false">
      <path
        d={`M${w / 2} ${h - 1} C${w * 0.08} ${h * 0.62} ${w * 0.16} ${h * 0.2} ${w / 2} 1 C${w * 0.84} ${h * 0.2} ${w * 0.92} ${h * 0.62} ${w / 2} ${h - 1} Z`}
        fill="rgba(245,235,211,.34)"
        stroke="rgba(215,166,75,.30)"
        strokeWidth=".6"
      />
      <path d={`M${w / 2} ${h - 3} L${w / 2} ${h * 0.22}`} stroke="rgba(215,166,75,.34)" strokeWidth=".55" fill="none" />
    </svg>
  );
}

function Lotus({ size, mirror }: { size: number; mirror?: boolean }) {
  return (
    <svg
      className="env-lotus"
      width={size}
      height={size * 0.62}
      viewBox="0 0 100 62"
      aria-hidden="true"
      focusable="false"
      style={mirror ? { transform: 'scaleX(-1)' } : undefined}
    >
      {/* lily pad */}
      <ellipse cx="52" cy="54" rx="44" ry="7.5" fill="rgba(9,42,38,.85)" />
      <path d="M14 54 L52 54" stroke="rgba(6,26,24,.9)" strokeWidth="1.4" />
      {/* petals */}
      <path d="M50 50 C36 44 30 30 36 20 C44 24 49 36 50 50 Z" fill="rgba(245,235,211,.42)" />
      <path d="M50 50 C64 44 70 30 64 20 C56 24 51 36 50 50 Z" fill="rgba(245,235,211,.34)" />
      <path d="M50 51 C42 46 38 34 43 24 C49 30 51 40 50 51 Z" fill="rgba(215,166,75,.30)" />
      <path d="M50 51 C58 46 62 34 57 24 C51 30 49 40 50 51 Z" fill="rgba(215,166,75,.22)" />
      <path d="M50 50 C47 42 47 32 50 24 C53 32 53 42 50 50 Z" fill="rgba(245,235,211,.5)" />
      <circle cx="50" cy="47" r="3" fill="rgba(215,166,75,.7)" />
    </svg>
  );
}

/* ------------------------------------------------------------------ *
 * Distant scenery — misty hills, forest treeline, temple gopuram
 * ------------------------------------------------------------------ */
function DistantScenery() {
  // temple gopuram: stepped tiers narrowing toward the top
  const tiers = [0, 1, 2, 3, 4, 5];
  const baseY = 372;
  const tierH = 26;
  return (
    <svg className="env-art env-art-distant" viewBox="0 0 1600 520" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
      {/* far misty ridge */}
      <path
        d="M0 330 C120 312 240 336 360 322 C480 308 560 330 700 318 C840 306 940 328 1080 314 C1220 300 1340 324 1460 312 C1520 306 1560 314 1600 308 L1600 520 L0 520 Z"
        fill="rgba(7,26,33,.92)"
      />
      <path
        d="M0 360 C140 346 260 368 400 354 C540 340 660 362 800 350 C940 338 1060 358 1200 346 C1340 334 1460 354 1600 344 L1600 520 L0 520 Z"
        fill="rgba(6,21,28,.95)"
      />

      {/* temple gopuram silhouette (right of centre, like the reference) */}
      <g opacity=".96">
        {tiers.map((i) => {
          const y = baseY - i * tierH;
          const half = 64 - i * 8;
          const cx = 1196;
          return (
            <path
              key={i}
              d={`M${cx - half} ${y} L${cx + half} ${y} L${cx + half - 7} ${y - tierH + 3} L${cx - half + 7} ${y - tierH + 3} Z`}
              fill={i % 2 ? 'rgba(4,15,20,.98)' : 'rgba(5,18,24,.98)'}
            />
          );
        })}
        {/* finial */}
        <path d={`M1196 ${baseY - 6 * tierH - 2} L1196 ${baseY - 6 * tierH - 22}`} stroke="rgba(5,18,24,.98)" strokeWidth="4" />
        <circle cx="1196" cy={baseY - 6 * tierH - 26} r="5" fill="rgba(215,166,75,.28)" />
        <circle cx="1196" cy={baseY - 6 * tierH - 34} r="2.6" fill="rgba(215,166,75,.20)" />
        {/* faint moonlit edge on the tower */}
        <path d={`M1132 ${baseY} L1139 ${baseY - 6 * tierH + 3}`} stroke="rgba(154,174,181,.14)" strokeWidth="1.2" fill="none" />
      </g>

      {/* small distant shrine, far left, very faint */}
      <g opacity=".5">
        <path d="M268 372 L268 316 L254 316 L254 306 L282 306 L282 316 L268 316" fill="rgba(5,17,23,.9)" />
        <path d="M268 306 L268 294" stroke="rgba(5,17,23,.9)" strokeWidth="3" />
      </g>

      {/* near treeline with organic canopy bumps */}
      <path
        d="M0 410 C40 404 60 386 96 388 C120 372 150 374 172 386 C200 376 232 380 252 394 C286 384 320 390 344 402 C378 390 410 396 436 406 C470 396 506 400 530 410 C568 398 604 404 628 414 C664 402 702 408 726 418 C764 406 800 412 826 422 C864 410 902 416 928 426 C966 414 1002 420 1028 430 C1066 418 1104 424 1130 434 C1168 422 1206 428 1232 438 C1270 426 1308 432 1334 442 C1372 430 1410 436 1436 446 C1474 434 1516 440 1544 450 C1566 456 1584 462 1600 466 L1600 520 L0 520 Z"
        fill="rgba(3,12,17,.98)"
      />
      {/* ground band under treeline */}
      <rect x="0" y="466" width="1600" height="54" fill="rgba(3,11,15,.98)" />
    </svg>
  );
}

/* ------------------------------------------------------------------ *
 * Canopy — irregular branches, leaf clusters, hanging vines
 * ------------------------------------------------------------------ */
function leafCluster(cx: number, cy: number, n: number, seed: number, scale = 1) {
  const leaves = [];
  for (let i = 0; i < n; i++) {
    const a = seeded(seed + i) * Math.PI * 2;
    const dist = (8 + seeded(seed + i * 3 + 1) * 26) * scale;
    const x = cx + Math.cos(a) * dist;
    const y = cy + Math.sin(a) * dist * 0.72;
    const rot = (seeded(seed + i * 7 + 2) * 90 - 45) | 0;
    const s = (0.7 + seeded(seed + i * 11 + 3) * 0.7) * scale;
    const tone = seeded(seed + i * 13 + 4);
    const fill =
      tone > 0.82 ? 'rgba(21,90,75,.62)' : tone > 0.55 ? 'rgba(14,58,50,.8)' : tone > 0.3 ? 'rgba(10,44,40,.85)' : 'rgba(7,33,32,.9)';
    leaves.push(
      <path
        key={`${cx}-${cy}-${i}`}
        d="M0 0 C10 -13 30 -17 44 -7 C31 7 11 11 0 0 Z"
        fill={fill}
        transform={`translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot}) scale(${s.toFixed(2)})`}
      />,
    );
  }
  return leaves;
}

function vine(x: number, y: number, len: number, seed: number, cls: string) {
  const sway = 1 + Math.round(seeded(seed) * 2); // 1..3 class variant
  const leaves = [];
  for (let i = 1; i <= Math.floor(len / 34); i++) {
    const ly = y + i * 34;
    const side = i % 2 === 0 ? 1 : -1;
    leaves.push(
      <path
        key={i}
        d={`M0 0 C${7 * side} -6 ${15 * side} -5 ${19 * side} 1 C${13 * side} 7 ${5 * side} 7 0 0 Z`}
        fill="rgba(10,46,42,.85)"
        transform={`translate(${(x + Math.sin(i * 1.7 + seed) * 5).toFixed(1)} ${ly}) scale(${side},1)`}
      />,
    );
  }
  return (
    <g className={`env-vine env-vine-${sway}`} key={`v-${x}-${y}`}>
      <path
        d={`M${x} ${y} C${x + 7} ${y + len * 0.34} ${x - 7} ${y + len * 0.66} ${x + 4} ${y + len}`}
        stroke="rgba(4,20,24,.9)"
        strokeWidth="2.4"
        fill="none"
        strokeLinecap="round"
      />
      {leaves}
    </g>
  );
}

function CanopyArt({ side }: { side: 'left' | 'right' }) {
  const m = side === 'left' ? 1 : -1;
  const originX = side === 'left' ? 0 : 640;
  const content = (
    <g transform={side === 'left' ? undefined : `translate(${originX} 0) scale(-1 1)`}>
      {/* primary branch sweeping from the top corner */}
      <path
        d="M-20 26 C110 52 230 84 340 138 C420 178 486 226 540 292"
        stroke="rgba(3,14,18,.96)"
        strokeWidth="17"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M120 56 C180 96 214 148 232 210 C244 252 244 292 236 332"
        stroke="rgba(3,14,18,.92)"
        strokeWidth="8"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M282 116 C330 140 372 178 402 226"
        stroke="rgba(3,14,18,.9)"
        strokeWidth="6"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M40 30 C78 74 96 124 100 178"
        stroke="rgba(3,14,18,.9)"
        strokeWidth="5.5"
        fill="none"
        strokeLinecap="round"
      />
      {/* leaf clusters along the branch */}
      {leafCluster(128, 74, 9, 11, 1.05)}
      {leafCluster(236, 118, 8, 23, 1)}
      {leafCluster(344, 168, 9, 37, 1.1)}
      {leafCluster(452, 244, 7, 51, 0.95)}
      {leafCluster(94, 150, 6, 67, 0.85)}
      {leafCluster(540, 300, 6, 83, 0.9)}
      {leafCluster(24, 40, 7, 97, 1.1)}
      {/* hanging vines */}
      {vine(178, 96, 150, 5, 'a')}
      {vine(312, 148, 190, 9, 'b')}
      {vine(96, 58, 130, 13, 'c')}
      {vine(432, 218, 160, 17, 'a')}
      {vine(520, 282, 120, 21, 'b')}
    </g>
  );
  return (
    <svg
      className={`env-art env-art-canopy env-art-canopy-${side}`}
      viewBox="0 0 640 460"
      preserveAspectRatio={side === 'left' ? 'xMinYMin meet' : 'xMaxYMin meet'}
      aria-hidden="true"
      focusable="false"
    >
      <g className="env-canopy-sway">{content}</g>
    </svg>
  );
}

/* ------------------------------------------------------------------ *
 * Botanical edges — ferns, shrubs, small flowers (bottom corners)
 * ------------------------------------------------------------------ */
function fernFronds(seed: number, count: number) {
  const fronds = [];
  for (let f = 0; f < count; f++) {
    const x0 = 30 + seeded(seed + f) * 340;
    const reach = 90 + seeded(seed + f * 5 + 1) * 120;
    const top = 130 + seeded(seed + f * 9 + 2) * 150;
    const cx = x0 + (seeded(seed + f * 3 + 3) * 80 - 40);
    const leaflets = [];
    const steps = 7;
    for (let i = 1; i <= steps; i++) {
      const t = i / (steps + 1);
      const x = (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * cx + t * t * (x0 + reach);
      const y = (1 - t) * (1 - t) * 380 + 2 * (1 - t) * t * (380 - top * 0.7) + t * t * (380 - top);
      const side = i % 2 === 0 ? 1 : -1;
      const size = 9 - i * 0.7;
      leaflets.push(
        <path
          key={`${f}-${i}`}
          d={`M0 0 C${size * side * 0.6} ${-size * 0.7} ${size * side * 1.5} ${-size * 0.5} ${size * side * 1.8} ${size * 0.15} C${size * side * 1.1} ${size * 0.75} ${size * side * 0.4} ${size * 0.5} 0 0 Z`}
          fill={i % 3 === 0 ? 'rgba(18,72,60,.8)' : 'rgba(9,40,36,.88)'}
          transform={`translate(${x.toFixed(1)} ${y.toFixed(1)})`}
        />,
      );
    }
    fronds.push(
      <g key={`f-${f}`}>
        <path
          d={`M${x0} 380 Q${cx} ${380 - top * 0.75} ${x0 + reach} ${380 - top}`}
          stroke="rgba(5,24,26,.92)"
          strokeWidth="2.6"
          fill="none"
          strokeLinecap="round"
        />
        {leaflets}
      </g>,
    );
  }
  return fronds;
}

function tinyFlowers(seed: number, n: number) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const x = 40 + seeded(seed + i * 7) * 340;
    const y = 250 + seeded(seed + i * 11) * 110;
    out.push(
      <g key={`fl-${i}`} transform={`translate(${x.toFixed(1)} ${y.toFixed(1)})`} opacity=".7">
        {[0, 72, 144, 216, 288].map((a) => (
          <ellipse key={a} cx="0" cy="-4.4" rx="2.1" ry="3.4" fill="rgba(245,235,211,.5)" transform={`rotate(${a})`} />
        ))}
        <circle cx="0" cy="0" r="2" fill="rgba(215,166,75,.8)" />
      </g>,
    );
  }
  return out;
}

function BotanicalEdge({ side }: { side: 'left' | 'right' }) {
  return (
    <svg
      className={`env-art env-art-edge env-art-edge-${side}`}
      viewBox="0 0 420 380"
      preserveAspectRatio={side === 'left' ? 'xMinYMax meet' : 'xMaxYMax meet'}
      aria-hidden="true"
      focusable="false"
    >
      <g className="env-edge-sway">
        {/* shrub mound */}
        <path
          d="M-10 380 C20 340 70 322 120 330 C160 300 230 300 270 328 C320 316 380 336 430 372 L430 380 Z"
          fill="rgba(3,14,17,.94)"
        />
        {fernFronds(side === 'left' ? 3 : 71, 5)}
        {tinyFlowers(side === 'left' ? 11 : 91, 4)}
        {/* low grasses */}
        {Array.from({ length: 9 }).map((_, i) => {
          const x = 20 + i * 46 + (seeded(i + (side === 'left' ? 1 : 40)) * 20 - 10);
          const h = 34 + seeded(i * 3 + (side === 'left' ? 2 : 41)) * 40;
          return (
            <path
              key={`g-${i}`}
              d={`M${x} 380 Q${x + 6} ${380 - h * 0.6} ${x + 12} ${380 - h}`}
              stroke="rgba(6,28,30,.9)"
              strokeWidth="2"
              fill="none"
              strokeLinecap="round"
            />
          );
        })}
      </g>
    </svg>
  );
}

/* ------------------------------------------------------------------ *
 * Pond — dark water, restrained ripples, reflections, lotus
 * ------------------------------------------------------------------ */
function PondArt() {
  const ripples = [
    { x: 60, y: 46, w: 190, o: 0.16, c: 'rgba(32,191,168,' },
    { x: 320, y: 84, w: 260, o: 0.12, c: 'rgba(32,191,168,' },
    { x: 700, y: 58, w: 210, o: 0.14, c: 'rgba(215,166,75,' },
    { x: 980, y: 104, w: 300, o: 0.1, c: 'rgba(32,191,168,' },
    { x: 1340, y: 70, w: 180, o: 0.13, c: 'rgba(215,166,75,' },
    { x: 180, y: 140, w: 240, o: 0.09, c: 'rgba(32,191,168,' },
    { x: 620, y: 158, w: 200, o: 0.08, c: 'rgba(245,235,211,' },
    { x: 1080, y: 176, w: 260, o: 0.07, c: 'rgba(32,191,168,' },
    { x: 420, y: 210, w: 320, o: 0.06, c: 'rgba(215,166,75,' },
    { x: 1240, y: 224, w: 220, o: 0.06, c: 'rgba(32,191,168,' },
  ];
  return (
    <svg className="env-art env-art-pond" viewBox="0 0 1600 260" preserveAspectRatio="none" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="envReflTeal" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(32,191,168,.14)" />
          <stop offset="100%" stopColor="rgba(32,191,168,0)" />
        </linearGradient>
        <linearGradient id="envReflGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(215,166,75,.13)" />
          <stop offset="100%" stopColor="rgba(215,166,75,0)" />
        </linearGradient>
        <linearGradient id="envReflIvory" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(245,235,211,.10)" />
          <stop offset="100%" stopColor="rgba(245,235,211,0)" />
        </linearGradient>
      </defs>
      {/* soft vertical reflections under moon / temple / lantern light */}
      <rect x="1150" y="0" width="96" height="200" fill="url(#envReflGold)" />
      <rect x="1244" y="0" width="46" height="150" fill="url(#envReflIvory)" />
      <rect x="322" y="0" width="70" height="170" fill="url(#envReflTeal)" />
      <rect x="700" y="0" width="54" height="130" fill="url(#envReflTeal)" />
      {/* ripples — short, wavy, restrained */}
      <g className="env-ripples">
        {ripples.map((r, i) => (
          <path
            key={i}
            d={`M${r.x} ${r.y} q ${r.w * 0.25} -4 ${r.w * 0.5} 0 t ${r.w * 0.5} 0`}
            stroke={`${r.c}${r.o})`}
            strokeWidth={1.3}
            fill="none"
            strokeLinecap="round"
          />
        ))}
      </g>
    </svg>
  );
}

/* ------------------------------------------------------------------ *
 * Particle positions (deterministic)
 * ------------------------------------------------------------------ */
type DriftKind = { id: number; x: number; y: number; size: number; kind: 'firefly' | 'petal'; drift: number };

function buildParticles(): DriftKind[] {
  const items: DriftKind[] = [];
  for (let i = 0; i < 11; i++) {
    items.push({
      id: i,
      x: 4 + seeded(i * 17 + 1) * 92,
      y: 12 + seeded(i * 17 + 2) * 62,
      size: 2 + Math.round(seeded(i * 17 + 3) * 3),
      kind: 'firefly',
      drift: 1 + (i % 4),
    });
  }
  for (let i = 0; i < 5; i++) {
    items.push({
      id: 100 + i,
      x: 6 + seeded(i * 29 + 11) * 88,
      y: 18 + seeded(i * 29 + 12) * 55,
      size: 7 + Math.round(seeded(i * 29 + 13) * 5),
      kind: 'petal',
      drift: 1 + (i % 3),
    });
  }
  return items;
}

/* ------------------------------------------------------------------ *
 * Environment root
 * ------------------------------------------------------------------ */
export default function BotanicalEnvironment() {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const pointerRef = useRef({ x: 0.5, y: 0.5 });
  const targetRef = useRef({ x: 0.5, y: 0.5 });
  const [lightOn, setLightOn] = useState(false);
  const [particles] = useState<DriftKind[]>(() => buildParticles());

  const reducedMotion =
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch =
    typeof window !== 'undefined' &&
    (window.matchMedia('(hover:none),(pointer:coarse)').matches || 'ontouchstart' in window);

  const commitPointer = useCallback((nx: number, ny: number) => {
    const c = { x: Math.min(1, Math.max(0, nx)), y: Math.min(1, Math.max(0, ny)) };
    const last = targetRef.current;
    if (Math.abs(c.x - last.x) < 0.002 && Math.abs(c.y - last.y) < 0.002) return;
    targetRef.current = c;
    setLightOn(true);
  }, []);

  // pointer listeners (never on touch / reduced motion)
  useEffect(() => {
    if (reducedMotion || isTouch) return;
    let last = 0;
    const onMove = (e: MouseEvent) => {
      const now = performance.now();
      if (now - last < 16) return;
      last = now;
      const r = rootRef.current?.getBoundingClientRect();
      if (!r || r.width === 0) return;
      commitPointer((e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height);
    };
    const onLeave = () => {
      setLightOn(false);
      targetRef.current = { x: 0.5, y: 0.5 };
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    document.addEventListener('mouseleave', onLeave);
    return () => {
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseleave', onLeave);
    };
  }, [commitPointer, reducedMotion, isTouch]);

  // single rAF loop: eased pointer -> CSS vars (parallax + cursor light)
  useEffect(() => {
    if (reducedMotion || isTouch) return;
    let cancelled = false;
    let raf = 0;
    const loop = () => {
      if (cancelled) return;
      const p = pointerRef.current;
      const t = targetRef.current;
      p.x += (t.x - p.x) * 0.09;
      p.y += (t.y - p.y) * 0.09;
      const root = rootRef.current;
      if (root) {
        // parallax per layer, restrained
        const nodes = root.querySelectorAll<HTMLElement>('[data-depth]');
        for (const n of nodes) {
          const depth = parseFloat(n.dataset.depth || '0');
          const dx = (p.x - 0.5) * 2;
          const dy = (p.y - 0.5) * 2;
          n.style.setProperty('--lx', `${(dx * depth * 4).toFixed(2)}px`);
          n.style.setProperty('--ly', `${(dy * depth * 3).toFixed(2)}px`);
        }
        // cursor light follows the pointer with easing
        root.style.setProperty('--cx', `${(p.x * 100).toFixed(2)}%`);
        root.style.setProperty('--cy', `${(p.y * 100).toFixed(2)}%`);
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      cancelled = true;
      if (raf) cancelAnimationFrame(raf);
    };
  }, [reducedMotion, isTouch]);

  const showLight = !reducedMotion && !isTouch && lightOn;

  return (
    <div ref={rootRef} className="env" aria-hidden="true">
      {/* 1. sky + moonlight + warm horizon glow */}
      <div className="env-layer env-sky" data-depth="0.15" />

      {/* 2. distant scenery: hills, treeline, temple gopuram */}
      <div className="env-layer env-distant" data-depth="0.55">
        <DistantScenery />
      </div>

      {/* 3. atmospheric mist */}
      <div className="env-layer env-mist" data-depth="0.85">
        <span className="env-mist-band env-mist-a" />
        <span className="env-mist-band env-mist-b" />
      </div>

      {/* 4. canopy: branches, leaf clusters, hanging vines */}
      <div className="env-layer env-canopy" data-depth="1.7">
        <CanopyArt side="left" />
        <CanopyArt side="right" />
      </div>

      {/* 5. botanical edges: ferns, shrubs, flowers */}
      <div className="env-layer env-edges" data-depth="2.3">
        <BotanicalEdge side="left" />
        <BotanicalEdge side="right" />
      </div>

      {/* 6. pond: water, reflections, ripples, lotus */}
      <div className="env-layer env-pond" data-depth="1.1">
        <div className="env-pond-water" />
        <PondArt />
        <span className="env-lotus-float env-lotus-a">
          <Lotus size={74} />
        </span>
        <span className="env-lotus-float env-lotus-b">
          <Lotus size={56} mirror />
        </span>
        <span className="env-lotus-float env-lotus-c">
          <Lotus size={44} />
        </span>
      </div>

      {/* 7. particles: a few fireflies + petals */}
      <div className="env-layer env-particles" data-depth="2.8">
        {particles.map((p) =>
          p.kind === 'firefly' ? (
            <span
              key={p.id}
              className={`env-firefly env-firefly-${p.drift}`}
              style={{ left: `${p.x}%`, top: `${p.y}%` }}
            >
              <Firefly size={p.size} />
            </span>
          ) : (
            <span
              key={p.id}
              className={`env-petal env-petal-${p.drift}`}
              style={{ left: `${p.x}%`, top: `${p.y}%` }}
            >
              <Petal size={p.size} />
            </span>
          ),
        )}
      </div>

      {/* 8. deliberate Tamil literary words along the right margin (as in the reference) */}
      <div className="env-layer env-literary" data-depth="1.25">
        <span className="env-word env-word-1">தமிழ்</span>
        <span className="env-word env-word-2">அறிவு</span>
        <span className="env-word env-word-3">இயற்கை</span>
        <span className="env-word env-word-4">மெய்</span>
      </div>

      {/* vignette keeps the centre calm and text readable */}
      <div className="env-vignette" />

      {/* restrained cursor-following ambient light */}
      <div className={`env-cursor-light${showLight ? ' on' : ''}`} />
    </div>
  );
}
