import React from 'react';
import { useEffect, useRef, useState, useCallback } from 'react';

void (import.meta.env.VITE_API_BASE_URL);

/* ---------- Lotus icon (sidebar logo) ---------- */
function LotusIcon({ size = 48, color = 'currentColor' }: { size?: number; color?: string }) {
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 64 64" fill="none" aria-hidden="true" focusable="false">
      {/* center stamen */}
      <circle cx="32" cy="32" r="3.2" fill={color} opacity=".9" />
      {/* petals, back layer */}      {[0,45,90,135,180,225,270,315].map((deg, i) => {
        const rad = deg * Math.PI / 180;
        const px = 32 + Math.cos(rad) * 15;
        const py = 32 + Math.sin(rad) * 15;
        return (<path
            key={i}
            d={`M 29 32 Q ${px - Math.cos(rad) * 7} ${py - Math.sin(rad) * 7} ${px + Math.cos(rad) * 9} ${py + Math.sin(rad) * 9} Q ${px + Math.cos(rad) * 3} ${py + Math.sin(rad) * 3} 35 35 Q ${px - Math.cos(rad) * 3} ${py - Math.sin(rad) * 3} ${29} ${32}`}
            stroke={color}
            strokeWidth={1.2}
            opacity={.75}
            fill="none"
          />
        );
      })}
      {/* inner petals */}
      {[22,67,112,157,202,247,292,337].map((deg, i) => {
        const rad = deg * Math.PI / 180;
        const px = 32 + Math.cos(rad) * 10.5;
        const py = 32 + Math.sin(rad) * 10.5;
        return (
          <path
            key={i + 8}
            d={`M 30 32 Q ${px - Math.cos(rad) * 4.5} ${py - Math.sin(rad) * 4.5} ${px + Math.cos(rad) * 7} ${py + Math.sin(rad) * 7} Q ${px + Math.cos(rad) * 2} ${py + Math.sin(rad) * 2} 33 33 Q ${px - Math.cos(rad) * 2} ${py - Math.sin(rad) * 2} 30 32`}
            stroke={color}
            strokeWidth={1}
            opacity={.6}
            fill="none"
          />
        );
      })}
      {/* subtle outer ring */}
      <circle cx="32" cy="32" r="22" stroke={color} strokeWidth={.5} opacity=".25" fill="none" strokeDasharray="1.5 1.5" />
    </svg>
  );
}

/* ---------- Outline icons for nav + cards ---------- */
const LeafIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M12 22 C6 20 3 17 2 13 C1 9 2 6 5 4 C7 3 10 3 12 4 C14 3 17 3 19 4 C22 6 23 9 22 13 C21 17 18 20 12 22 Z" stroke="currentColor" strokeWidth="1.2" opacity=".85" fill="none" />
    <path d="M12 22 L12 5" stroke="currentColor" strokeWidth=".7" opacity=".5" fill="none" />
  </svg>
);

const BookIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M4 5 C4 4 5 3 6 3 L18 3 C19 3 20 4 20 5 L20 19 C20 20 19 21 18 21 L6 21 C5 21 4 20 4 19 Z" stroke="currentColor" strokeWidth="1.2" opacity=".85" fill="none" />
    <path d="M4 9 L20 9" stroke="currentColor" strokeWidth=".8" opacity=".5" fill="none" />
    <path d="M4 13 L20 13" stroke="currentColor" strokeWidth=".8" opacity=".5" fill="none" />
    <path d="M4 17 L20 17" stroke="currentColor" strokeWidth=".8" opacity=".5" fill="none" />
  </svg>
);

const SearchIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <circle cx="10.5" cy="10.5" r="6" stroke="currentColor" strokeWidth="1.3" opacity=".85" fill="none" />
    <path d="M15 15 L20 20" stroke="currentColor" strokeWidth="1.3" opacity=".85" fill="none" strokeLinecap="round" />
  </svg>
);

const MoleculeIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <circle cx="12" cy="7" r="2.6" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <circle cx="7" cy="16" r="2.2" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <circle cx="17" cy="16" r="2.2" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <path d="M12 9.5 L12 12 M12 12 L8 14.5 M12 12 L16 14.5" stroke="currentColor" strokeWidth=".9" opacity=".65" fill="none" strokeLinecap="round" />
  </svg>
);

const NetworkIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <circle cx="7" cy="7" r="1.6" fill="currentColor" opacity=".85" />
    <circle cx="17" cy="7" r="1.6" fill="currentColor" opacity=".85" />
    <circle cx="12" cy="14.5" r="1.6" fill="currentColor" opacity=".85" />
    <circle cx="9.5" cy="19" r="1.5" fill="currentColor" opacity=".7" />
    <circle cx="14.5" cy="19" r="1.5" fill="currentColor" opacity=".7" />
    <path d="M7 7 L17 7 M7 7 L12 14.5 M17 7 L12 14.5 M12 14.5 L9.5 19 M12 14.5 L14.5 19" stroke="currentColor" strokeWidth=".8" opacity=".6" fill="none" strokeLinecap="round" />
  </svg>
);

const ChartIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <rect x="4" y="14" width="3.2" height="6" rx="1" stroke="currentColor" strokeWidth=".9" opacity=".85" fill="none" />
    <rect x="10.4" y="9.5" width="3.2" height="10.5" rx="1" stroke="currentColor" strokeWidth=".9" opacity=".85" fill="none" />
    <rect x="16.8" y="5" width="3.2" height="15" rx="1" stroke="currentColor" strokeWidth=".9" opacity=".85" fill="none" />
  </svg>
);

const LayersIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M4 6 L20 6 M4 10 L20 10 M4 14 L20 14 M4 18 L20 18" stroke="currentColor" strokeWidth="1.1" opacity=".75" fill="none" strokeLinecap="round" />
    <path d="M4 6 L4 18 M20 6 L20 18" stroke="currentColor" strokeWidth="1.1" opacity=".5" fill="none" />
  </svg>
);

const BellIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M6 9 C6 6.5 8 5 12 5 C16 5 18 6.5 18 9 L18 11 L20 13 L13 18 L13 19 C13 20.1 11.9 21 10.8 21 C9.7 21 8.6 20.1 8.6 19 L8.6 9 Z" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <path d="M9 19 L15 19" stroke="currentColor" strokeWidth="1" opacity=".6" fill="none" />
    <circle cx="11.5" cy="12.5" r=".9" fill="currentColor" opacity=".8" />
  </svg>
);

const GearIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M12 12 C14.5 12 16.5 10.5 17.2 8.5 C17.9 6.5 16.9 4.3 15.1 3.6 C13.3 2.9 11 3.9 10.3 5.7 L6.6 9.4 C5 10.3 4 11.9 3.7 13.6 C3.4 15.3 4 17 5.5 18 C7 19 9 19 11 19 C11.9 19 12.3 19.5 12.1 20.4 L9.3 19.5 C9.5 18.4 10.2 17.4 11.3 16.8 C12.4 16.2 13.7 16 14.6 15.3 L17.2 15.7 C18.4 16.5 19.1 17.7 19.3 19 C19.5 20.3 18.9 21.7 17.3 22.3 C15.7 22.9 13.6 22.2 12.7 20.8 L16 20.1 C15.2 21.2 14.1 21.8 12.9 22.1 C11.7 22.4 10.3 22 9.3 21.2 C8.1 20.2 7.6 18.8 7.8 17.4 L11 17.1 C9.5 16.2 8.4 15 7.6 13.4 C6.8 11.8 6.4 10 6.9 8.5 C7.4 7 8.3 5.8 9.6 5 C10.9 4.2 12.5 4 13.8 4.4 L13.2 7.5 C14.2 7.1 15.2 7 16 6.6 C16.8 6.2 17.3 5.4 17.3 4.5 C17.3 3.6 16.7 2.8 15.7 2.5 C14.7 2.2 13.5 2.6 12.7 3.5 L12.4 4.8 C10.9 4.2 9.4 4.3 8.2 4.9 C6.8 5.6 6 7 6.1 8.6 L11 10.2 C10.6 11.5 10.7 12.8 10 14 C9.3 15.2 9 16.7 9.7 18 C10.4 19.3 11.7 19.9 13 19.6 C14.3 19.3 15.3 18.2 15.6 16.8 L16 16 C16.5 17.2 16.5 18.4 15.9 19.3 C15.3 20.2 14.1 20.6 13 20.3 C11.9 20 11.1 18.9 11.5 17.8 L9 16.9 C9.5 15.5 9.9 14 10.8 12.7 C11.7 11.4 12.9 10.7 14.2 10.5" stroke="currentColor" strokeWidth=".8" opacity=".85" fill="none" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const DiscsIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <ellipse cx="12" cy="7" rx="6.5" ry="2.5" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <ellipse cx="12" cy="12" rx="6.5" ry="2.5" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <ellipse cx="12" cy="17" rx="6.5" ry="2.5" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" />
    <path d="M5.5 7 L18.5 7 M5.5 12 L18.5 12 M5.5 17 L18.5 17" stroke="currentColor" strokeWidth=".7" opacity=".4" fill="none" />
  </svg>
);

const DocCheckIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
    <path d="M4 5 C4 4 5 3 6 3 L18 3 C19 3 20 4 20 5 L20 21 C20 22 19 23 18 23 L6 23 C5 23 4 22 4 21 Z" stroke="currentColor" strokeWidth="1.2" opacity=".85" fill="none" />
    <path d="M7 9 L8.5 10.5 L12 8 L17 13" stroke="currentColor" strokeWidth="1.1" opacity=".85" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M7 14 L10 14" stroke="currentColor" strokeWidth="1.1" opacity=".7" fill="none" strokeLinecap="round" />
    <path d="M13 14 L16 14" stroke="currentColor" strokeWidth="1.1" opacity=".7" fill="none" strokeLinecap="round" />
    <path d="M7 17 L11 17" stroke="currentColor" strokeWidth="1.1" opacity=".7" fill="none" strokeLinecap="round" />
  </svg>
);

/* ---------- Botanical SVG assets ---------- */
function TreeSilhouetteLeftSVG(){ return (<svg className="tree-silhouette branch-sway foliage-sway" viewBox="0 0 400 520" preserveAspectRatio="none" fill="none" aria-hidden="true" focusable="false">
  <g className="trunk">
    <path d="M200 520 C210 460 195 420 200 370 C205 320 195 280 200 220 C205 160 195 120 200 70" stroke="rgba(21,90,82,.26)" strokeWidth="3.6" fill="none" />
  </g>
  <g className="foliage">
    {[70,110,150,190,230,270,310,350].map((y,i)=>(
    <path key={i} d={`M200 ${y} C160 ${y-18} 130 ${y-6} 90 ${y+6} C140 ${y+10} 170 ${y+4} 200 ${y}`} stroke="rgba(21,90,82,.18)" strokeWidth="2.6" fill="none" />
  ))}
    {[70,110,150,190,230,270,310,350].map((y,i)=>(
    <path key={i+100} d={`M200 ${y} C240 ${y-18} 270 ${y-6} 310 ${y+6} C260 ${y+10} 230 ${y+4} 200 ${y}`} stroke="rgba(21,90,82,.18)" strokeWidth="2.6" fill="none" />
  ))}
  </g>
</svg>);}

function TreeSilhouetteRightSVG(){ return (<svg className="tree-silhouette branch-sway-right foliage-sway-right" viewBox="0 0 400 520" preserveAspectRatio="none" fill="none" aria-hidden="true" focusable="false">
  <g className="trunk">
    <path d="M200 520 C190 460 205 420 200 370 C195 320 205 280 200 220 C195 160 205 120 200 70" stroke="rgba(21,90,82,.24)" strokeWidth="3.4" fill="none" />
  </g>
  <g className="foliage">
    {[70,110,150,190,230,270,310,350].map((y,i)=>(
    <path key={i} d={`M200 ${y} C240 ${y-18} 270 ${y-6} 310 ${y+6} C260 ${y+10} 230 ${y+4} 200 ${y}`} stroke="rgba(21,90,82,.16)" strokeWidth="2.4" fill="none" />
  ))}
    {[70,110,150,190,230,270,310,350].map((y,i)=>(
    <path key={i+100} d={`M200 ${y} C160 ${y-18} 130 ${y-6} 90 ${y+6} C140 ${y+10} 170 ${y+4} 200 ${y}`} stroke="rgba(21,90,82,.16)" strokeWidth="2.4" fill="none" />
  ))}
  </g>
</svg>);}

// HangingLeafSVG reserved for future use

function PetalSVG({ color = 'rgba(215,166,75,.55)', w=14, h=18 }:{color?:string;w?:number;h?:number}){
  return (<svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" aria-hidden="true" focusable="false">
    <path d={`M${w/2} ${h-2} C${w/2 - w*0.4} ${h*0.3} ${w/2 + w*0.2} ${h*0.1} ${w/2} ${h*0.05} C${w/2 - w*0.15} ${h*0.12} ${w/2 - w*0.3} ${h*0.35} ${w/2 - w*0.1} ${h*0.6} C${w/2 - w*0.25} ${h*0.75} ${w/2 - w*0.12} ${h*0.92} ${w/2} ${h-2} Z`} stroke={color} strokeWidth="1.1" opacity=".8" fill="none" />
    <path d={`M${w/2} ${h-2} L${w/2} ${h*0.08}`} stroke={color} strokeWidth=".5" opacity=".35" fill="none" />
  </svg>);
}

function LeafSVG({ color = 'rgba(74,184,146,.45)', w=20, h=30 }:{color?:string;w?:number;h?:number}){
  return (<svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" aria-hidden="true" focusable="false">
    <path d={`M${w/2} ${h-2} C${w/2 - w*0.42} ${h*0.18} ${w/2 - w*0.46} ${h*0.52} ${w/2} ${h*0.04} C${w/2 + w*0.46} ${h*0.52} ${w/2 + w*0.42} ${h*0.18} ${w/2} ${h-2} Z`} stroke={color} strokeWidth="1.2" opacity=".8" fill="none" />
    <path d={`M${w/2} ${h-1} L${w/2} ${h*0.06}`} stroke={color} strokeWidth=".6" opacity=".4" fill="none" />
    <path d={`M${w/2} ${h*0.4} L${w/2 - w*0.26} ${h*0.55}`} stroke={color} strokeWidth=".5" opacity=".35" fill="none" />
    <path d={`M${w/2} ${h*0.4} L${w/2 + w*0.26} ${h*0.55}`} stroke={color} strokeWidth=".5" opacity=".35" fill="none" />
    <path d={`M${w/2} ${h*0.72} L${w/2 - w*0.24} ${h*0.82}`} stroke={color} strokeWidth=".5" opacity=".35" fill="none" />
    <path d={`M${w/2} ${h*0.72} L${w/2 + w*0.24} ${h*0.82}`} stroke={color} strokeWidth=".5" opacity=".35" fill="none" />
  </svg>);
}

function FireflySVG({ color = 'rgba(215,166,75,.9)', r=3.5 }:{color?:string;r?:number}){
  return (<svg width={r*3} height={r*3} viewBox={`-${r*1.5} -${r*1.5} ${r*3} ${r*3}`} aria-hidden="true" focusable="false">
    <circle cx="0" cy="0" r={r*1.6} fill={color} opacity=".18" />
    <circle cx="0" cy="0" r={r} fill={color} opacity=".55" />
    <circle cx="0" cy="0" r={r*0.45} fill="#fff" opacity=".95" />
  </svg>);
}

function LotusFlowerSVG({ color = 'rgba(215,166,75,.7)', s=36 }:{color?:string;s?:number}){
  const cx=s/2, cy=s/2;
  const petals=6;
  return (<svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} fill="none" aria-hidden="true" focusable="false">
    {Array.from({length:petals}).map((_,i)=>{
      const a=(i/petals)*Math.PI*2 - Math.PI/2;
      const px=cx+Math.cos(a)*s*0.22;
      const py=cy-s*0.12+Math.sin(a*1)*s*0.18;
      return (<path key={i} d={`M${cx} ${cy - s*0.05} C${px - Math.cos(a)*s*0.18} ${py - Math.sin(a)*s*0.18} ${px + Math.cos(a)*s*0.18} ${py + Math.sin(a)*s*0.18} ${cx + Math.cos(a)*s*0.04} ${cy + s*0.06} Z`}
        stroke={color} strokeWidth="1" opacity=".7" fill="none" />);
    })}
    <circle cx={cx} cy={cy} r={s*0.045} fill={color} opacity=".85" />
    <circle cx={cx} cy={cy} r={s*0.14} stroke={color} strokeWidth=".6" opacity=".4" fill="none" />
  </svg>);
}

function KolamCurveSVG(){
  return (<svg className="kolam-curve" viewBox="0 0 400 400" preserveAspectRatio="none" fill="none" aria-hidden="true" focusable="false">
    <path d="M 200 60 C 240 90 260 90 300 100 C 340 110 360 130 340 160 C 320 190 280 180 260 200 C 240 220 250 250 220 260 C 190 270 160 260 150 230 C 140 200 160 180 180 170 C 200 160 230 170 240 200 C 250 230 230 240 210 235 C 190 230 175 210 185 185 C 195 160 215 155 235 175 C 255 155 260 130 250 110 C 240 90 210 85 200 60" stroke="rgba(47,208,176,.5)" strokeWidth="1" opacity=".7" />
    <path d="M 50 200 C 80 180 110 190 140 210 C 170 230 190 260 220 250 C 250 240 260 210 240 180 C 220 150 180 140 160 160 C 140 180 150 210 120 215 C 90 220 80 200 100 175 C 120 150 150 145 170 160 C 190 175 210 155 200 130 C 190 105 160 100 140 120 C 120 140 150 160 130 180 C 110 200 80 195 75 170" stroke="rgba(32,191,168,.4)" strokeWidth="1" opacity=".6" />
    <path d="M 200 340 C 250 320 290 330 320 310 C 350 290 360 260 340 230 C 320 200 280 210 250 230 C 220 250 230 280 200 290 C 170 300 130 280 120 250 C 110 220 140 190 170 200 C 200 210 230 190 250 210 C 270 230 280 260 270 290 C 260 320 220 340 200 340" stroke="rgba(215,166,75,.4)" strokeWidth="1" opacity=".6" />
  </svg>);
}

/* ---------- Distant atmospheric silhouettes (temple / forest tower / ridge) ---------- */
function DistantSilhouettesSVG(){
  return (<svg className="distant-silhouettes" viewBox="0 0 1200 500" preserveAspectRatio="xMidYMax slice" fill="none" aria-hidden="true" focusable="false">
    {/* far ridge band */}
    <path d="M0 380 L0 300 C80 288 160 296 240 284 C320 272 400 290 480 278 C560 266 640 282 720 270 C800 258 880 274 960 262 C1040 250 1120 266 1200 254 L1200 500 L0 500 Z" fill="rgba(8,20,26,.55)" opacity=".8" />
    {/* mid ridge with temple-tower silhouette */}
    <path d="M0 420 L0 360 C60 350 120 356 180 344 C240 332 300 348 360 336 C420 324 470 340 520 328 C560 318 580 296 600 270 C612 252 620 236 628 224 C636 212 648 204 662 200 C676 196 692 198 708 206 C724 214 738 228 750 244 C762 260 772 276 780 290 C788 304 794 316 800 326 L800 500 L0 500 Z" fill="rgba(8,20,26,.7)" opacity=".85" />
    {/* temple-tower spire detail */}
    <path d="M662 200 C662 200 658 170 662 148 C666 126 674 112 668 96 C662 80 652 76 648 64 C644 52 648 40 656 36 C664 32 672 36 674 48 C676 60 672 70 668 78 C664 86 660 78 658 68" stroke="rgba(32,191,168,.18)" strokeWidth=".8" fill="none" opacity=".7" />
    <path d="M662 200 L662 96" stroke="rgba(32,191,168,.12)" strokeWidth=".6" opacity=".5" />
    {/* canopy bumps along mid ridge */}
    <path d="M180 344 C176 332 184 322 192 318 C200 314 206 322 204 332 C202 340 192 346 184 346 C176 346 174 342 180 344 Z" fill="rgba(8,20,26,.5)" opacity=".6" />
    <path d="M360 336 C356 324 364 314 372 310 C380 306 386 314 384 324 C382 334 372 340 364 340 C356 340 354 336 360 336 Z" fill="rgba(8,20,26,.5)" opacity=".6" />
    <path d="M520 328 C516 316 524 306 532 302 C540 298 546 306 544 316 C542 326 532 332 524 332 C516 332 514 328 520 328 Z" fill="rgba(8,20,26,.5)" opacity=".6" />
    <path d="M750 244 C746 232 754 222 762 218 C770 214 776 222 774 232 C772 242 762 248 754 248 C746 248 744 244 750 244 Z" fill="rgba(8,20,26,.5)" opacity=".6" />
    {/* near forest band */}
    <path d="M0 500 L0 460 C100 452 200 458 300 448 C400 438 500 452 600 442 C700 432 800 446 900 436 C1000 426 1100 440 1200 430 L1200 500 Z" fill="rgba(8,20,26,.82)" opacity=".9" />
  </svg>);
}

/* ---------- Seeded random ---------- */
function seededNext(seed:number, max:number):number{ const x=Math.sin(seed+1)*10000; return Math.abs(x-Math.floor(x))*max; }

/* ---------- Cursor-reactive environment ---------- */
function setLayerStyle(n: Element, name: string, value: string){ (n as HTMLElement & { style: CSSStyleDeclaration }).style.setProperty(name, value); }

function BotanicalBackground(){
  const rootRef = useRef<HTMLDivElement | null>(null);
  const TAMIL_SYMBOLS = [{ glyph: 'அ' }, { glyph: 'ஆ' }, { glyph: 'இ' }, { glyph: 'உ' }, { glyph: 'ம்' }, { glyph: 'ழ்' }, { glyph: 'த்' }, { glyph: 'ற்' }, { glyph: 'ந்' }, { glyph: 'ண்' }];
  const USE_TAMIL = true;
  const PLACE_TAMIL = (i: number) => (i % 2 === 0) && USE_TAMIL;
  const tamilGlyph = (i: number) => TAMIL_SYMBOLS[i % TAMIL_SYMBOLS.length].glyph;
  const pointerRef = useRef({x:0.5, y:0.5});
  const targetRef = useRef({x:0.5, y:0.5});
  const [cursorActive, setCursorActive] = useState(false);
  const [symbols, setSymbols] = useState<Array<{id:number;type:'tamil'|'leaf'|'petal'|'firefly'|'lotus';x:number;y:number;depth:number;cls:string;size?:number;color?:string;glyph?:string}>>([]);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch = window.matchMedia('(hover:none),(pointer:coarse)').matches || 'ontouchstart' in window;

  // Placement
  useEffect(()=>{
    const items: typeof symbols = [];
    for(let i=0;i<42;i++){
      const seed=edgeFor(i);
      const r1=seededNext(seed,1), r2=seededNext(seed+7,1);
      const depth=Math.round(1+r2*4);
      const t=i%7;
      if(t===0){ items.push({id:i,type:'lotus',x:r1,y:0.92-depth*0.06,depth,cls:'lotus-left'+(i%2?'':'-small')}); }
      else if(t===1){ items.push({id:i,type:'lotus',x:r1,y:0.93-depth*0.05,depth,cls:'lotus-right'+(i%3===0?'':'-small')}); }
      else if(t===2){ items.push({id:i,type:'leaf',x:r1,y:0.04+r2*0.14,depth,cls:'hl-top-left'+(i%2?'-2':''),size:14+seededNext(seed+13,14)|0}); }
      else if(t===3){ items.push({id:i,type:'leaf',x:r1,y:0.05+r2*0.12,depth,cls:'hl-top-right'+(i%2?'':'-2'),size:14+seededNext(seed+17,14)|0}); }
      else if(t===4){ items.push({id:i,type:'leaf',x:r1,y:0.62+r2*0.28,depth,cls:'fgl-bottom-left'+(i%2?'':'-right'),size:18+seededNext(seed+21,14)|0}); }
      else if(t===5){ if(PLACE_TAMIL(i)){ items.push({id:i,type:'tamil',x:0.15+r1*0.7,y:0.18+r2*0.18,depth,cls:'tg-'+((i%6)+1),size:14+seededNext(seed+31,8)|0, glyph:tamilGlyph(i)}); } else { items.push({id:i,type:'petal',x:r1,y:0.55+r2*0.25,depth,cls:'fgl-mid-left'+(i%2?'':'-right'),size:10+seededNext(seed+25,10)|0}); } }
      else { items.push({id:i,type:'firefly',x:r1,y:0.18+r2*0.6,depth,cls:'ff-'+(1+(i%8)),size:3+seededNext(seed+29,4)|0}); }
    }
    setSymbols(items);
  },[]);

  function edgeFor(i:number){ return (i*9301+17) % 233280; }

  const commitPointer = useCallback((nx:number, ny:number)=>{
    const c = {x:Math.max(0,Math.min(1,nx)), y:Math.max(0,Math.min(1,ny))};
    const last = targetRef.current;
    if(Math.abs(c.x-last.x)<0.0015 && Math.abs(c.y-last.y)<0.0015) return;
    targetRef.current = c;
    setCursorActive(true);
  }, []);

  useEffect(()=>{
    const el = rootRef.current;
    if(!el || reducedMotion || isTouch){ setCursorActive(false); return; }
    let last = performance.now();
    const onMove = (e:MouseEvent)=>{
      const now = performance.now();
      if(now - last < 8) return;
      last = now;
      const r = el.getBoundingClientRect();
      const nx = (e.clientX - r.left)/r.width;
      const ny = (e.clientY - r.top)/r.height;
      commitPointer(nx, ny);
    };
    const onLeave = ()=>{ setCursorActive(false); targetRef.current={x:0.5,y:0.5}; };
    window.addEventListener('mousemove', onMove, {passive:true});
    window.addEventListener('mouseleave', onLeave);
    return ()=>{ window.removeEventListener('mousemove',onMove); window.removeEventListener('mouseleave',onLeave); };
  },[commitPointer, reducedMotion, isTouch]);

  // Single rAF loop: ease pointer + set CSS vars on all layers
  useEffect(()=>{
    if(reducedMotion) return;
    let cancelled = false;
    let t = 0;
    let id = 0;
    const loop = ()=>{
      if(cancelled) return;
      t += 0.016;
      const px = pointerRef.current.x;
      const py = pointerRef.current.y;
      const tx = targetRef.current.x, ty = targetRef.current.y;
      pointerRef.current = { x: px+(tx-px)*0.12, y: py+(ty-py)*0.12 };
      const p = pointerRef.current;
      const root = rootRef.current;
      if(root){
        const nodes = root.querySelectorAll('[data-layer]');
        for(const n of nodes){
          const depth = parseFloat((n as any).dataset.layer ?? '1');
          const cx = parseFloat((n as any).dataset.cx ?? '0.5');
          const cy = parseFloat((n as any).dataset.cy ?? '0.5');
          const dx = (p.x - cx)*2;
          const dy = (p.y - cy)*2;
          const dist = Math.sqrt(dx*dx+dy*dy);
          const f = Math.min(1, dist < 0.25 ? (0.25-dist)/0.25 : 0);
          const parallax = depth;
          const extraX = dx * (0.5 + f*2.5) * (depth>=3.5 ? -0.3 : 0.3) * (depth>=4?0.6:1);
          const extraY = dy * (0.5 + f*2) * (depth>=3.5 ? -0.2 : 0.2) * (depth>=4?0.5:1);
          setLayerStyle(n, '--lx', `${dx*parallax*0.6 + extraX}px`);
          setLayerStyle(n, '--ly', `${dy*parallax*0.4 + extraY}px`);
          setLayerStyle(n, '--near', String(f));
        }
      }
      id = requestAnimationFrame(loop);
    };
    id = requestAnimationFrame(loop);
    return ()=>{ cancelled = true; if(id) cancelAnimationFrame(id); };
  },[reducedMotion]);

  const showCursorLight = !reducedMotion && !isTouch && cursorActive;

  return (
    <div ref={rootRef} className="environment" aria-hidden="true">
      {/* Layer 0 — distant atmospheric silhouettes (temple / forest tower / ridge) */}
      <div className="layer-distant" data-layer="1.3" data-cx="0.5" data-cy="0.7" style={{ transform:`translate(0px,0px)` }}>
        <DistantSilhouettesSVG />
      </div>

      {/* Layer 1 — deep background parallax */}
      <div className="layer-bg" data-layer="1" data-cx="0.5" data-cy="0.5" style={{ transform:`translate(0px,0px)` }} />

      {/* Layer 1.5 — atmospheric mist / depth haze */}
      <div className="layer-mist" data-layer="1.5" data-cx="0.5" data-cy="0.45" style={{ transform:`translate(0px,0px)` }}>
        <div className="mist-band" data-cx="0.3" data-cy="0.6" data-layer="1.5" />
        <div className="mist-band-2" data-cx="0.7" data-cy="0.7" data-layer="1.5" />
      </div>

      {/* Layer 2 — trees/branches (parallax ~2) */}
      <div className="layer-trees" data-layer="2" data-cx="0.5" data-cy="0.6" style={{ transform:`translate(0px,0px)` }}>
        <TreeSilhouetteLeftSVG />
        <TreeSilhouetteRightSVG />
      </div>

      {/* Layer 3 — hanging leaves near upper corners (parallax ~4) */}
      <div className="layer-hanging-leaves" data-layer="4" data-cx="0.5" data-cy="0.15" style={{ transform:`translate(0px,0px)` }}>
        {symbols.filter(s=>s.type==='leaf' && s.cls.includes('hl-top')).map(s=>(
          <span key={s.id} className={`hanging-leaf ${s.cls}`} data-cx={String(s.x)} data-cy="0.12" data-layer="4" style={{ left:`${s.x*100}%`, top:`${0.04+0.12*0.14}`, fontSize: s.size! }}>
            <LeafSVG color={s.id%2===0 ? 'rgba(74,184,146,.5)' : 'rgba(58,150,120,.5)'} w={s.size!} h={s.size!*1.5} />
          </span>
        ))}
      </div>

      {/* Layer 6 — Tamil literary elements (parallax ~5, proximity glow) */}
      <div className="layer-tamil" data-layer="5" data-cx="0.5" data-cy="0.32" style={{ transform:`translate(0px,0px)` }}>
        {symbols.filter((s:any)=>s.type==='tamil' && s.glyph).map((s:any,i)=>(
          <span key={s.id} className={`tamil-glyph tg-${1+(i%6)}`} data-cx={String(s.x)} data-cy={String(s.y)} data-layer="5" style={{ left:`${s.x*100}%`, top:`${s.y*100}%`, fontSize: s.size ?? 16 }}>
            {s.glyph}
          </span>
        ))}
      </div>

      {/* Foreground leaves + petals (parallax ~4.5) */}
      <div className="layer-foreground" data-layer="4.5" data-cx="0.5" data-cy="0.75" style={{ transform:`translate(0px,0px)` }}>
        {symbols.filter(s=>s.type==='leaf' && s.cls.includes('fgl')).map(s=>(
          <span key={s.id} className={`fg-leaf ${s.cls}`} data-cx={String(s.x)} data-cy={String(0.7)} data-layer="4.5" style={{ left:`${s.x*100}%`, bottom:`${0.04+0.28*0.28}`, fontSize: s.size! }}>
            <LeafSVG color={s.id%2===0?'rgba(74,184,146,.45)':'rgba(58,150,120,.45)'} w={s.size!} h={s.size!*1.5} />
          </span>
        ))}
        {symbols.filter(s=>s.type==='petal').map(s=>(
          <span key={s.id} className={`fg-leaf ${s.cls}`} data-cx={String(s.x)} data-cy={String(0.65)} data-layer="4.5" style={{ left:`${s.x*100}%`, bottom:`${0.05+0.25*0.25}`, fontSize: s.size! }}>
            <PetalSVG color="rgba(215,166,75,.5)" w={s.size!} h={s.size!*1.3} />
          </span>
        ))}
      </div>

      {/* Layer 5 — golden fireflies (parallax ~5.5, proximity brighten) */}
      <div className="layer-particles" data-layer="5.5" data-cx="0.5" data-cy="0.4" style={{ transform:`translate(0px,0px)` }}>
        {symbols.filter(s=>s.type==='firefly').map(s=>(
          <span key={s.id} className={`firefly ${s.cls}`} data-cx={String(s.x)} data-cy={String(s.y)} data-layer="5.5" style={{ left:`${s.x*100}%`, top:`${s.y*100}%`, fontSize:(s.size!*2.5)|0 }}>
            <FireflySVG color="rgba(215,166,75,.9)" r={s.size!} />
          </span>
        ))}
      </div>

      {/* Layer 4 — water + lotus reflections near bottom (parallax ~2.5) */}
      <div className="layer-water" data-layer="2.5" data-cx="0.5" data-cy="0.92" style={{ transform:`translate(0px,0px)` }}>
        <div className="water-shimmer" data-cx="0.5" data-cy="0.92" data-layer="2.5" />
          {symbols.filter(s=>s.type==='lotus').map(s=>(
          <span key={s.id} className={`lotus-float ${s.cls}`} data-cx={String(s.x)} data-cy="0.94" data-layer="2.5" style={{ left:`${s.x*100}%`, bottom:`2%`, fontSize:(s.cls.includes('small')?24:34)|0 }}>
            <LotusFlowerSVG color="rgba(215,166,75,.65)" s={s.cls.includes('small')?24:34} />
          </span>
        ))}
      </div>

      {/* Layer 7 — kolam curves (very subtle, parallax ~1.2) */}
      <div className="layer-kolam" data-layer="1.2" data-cx="0.5" data-cy="0.5" style={{ transform:`translate(0px,0px)` }}>
        <KolamCurveSVG />
      </div>

      {/* Cursor light */}
      {showCursorLight && <div className="cursor-light active" aria-hidden="true" style={{ left: `${pointerRef.current.x*100}%`, top:`${pointerRef.current.y*100}%` }} />}
    </div>
  );
}

/* ---------- Navigation items ---------- */
const NAV_ITEMS = [
  { id:'home', label:'Home', icon:LeafIcon, active:true },
  { id:'texts', label:'Tamil Texts', icon:BookIcon },
  { id:'research', label:'Research', icon:SearchIcon },
  { id:'science', label:'Scientific Literature', icon:MoleculeIcon },
  { id:'connections', label:'Connections', icon:NetworkIcon },
  { id:'analysis', label:'Analysis', icon:ChartIcon },
  { id:'collections', label:'Collections', icon:LayersIcon },
];
const SECONDARY_ITEMS = [
  { id:'notifications', label:'Notifications', icon:BellIcon },
  { id:'settings', label:'Settings', icon:GearIcon },
];

const DISCOVERY_CARDS = [
  { id:'texts', title:'Explore Tamil Texts', desc:'Read and analyse classical Tamil literature', icon:BookIcon, iconKind:'gold' },
  { id:'nature', title:'Discover Natural Knowledge', desc:'Explore plants, environment and traditional understanding', icon:LeafIcon, iconKind:'teal' },
  { id:'science2', title:'View Scientific Evidence', desc:'Find modern research and verify claims', icon:MoleculeIcon, iconKind:'gold' },
  { id:'connects', title:'Find Connections', desc:'Explore relationships between literature and science', icon:NetworkIcon, iconKind:'blue' },
];

const SUGGEST_PILLS = [
  'Siddha medicine',
  'Plants in Sangam literature',
  'Human biology',
  'Ecology',
  'Nutrition',
  'Mind and cognition',
];

function App(){
  const [query, setQuery] = useState('');

  useEffect(()=>{ /* health check — future integration */ },[]);

  // apiState reserved for future backend integration

  function submitSearch(e:React.FormEvent<HTMLFormElement>){
    e.preventDefault();
    if(query.trim()){
      window.alert('Search is not connected yet. The backend contributor will implement the agreed search API.');
    }
  }

  return (
    <div className="app-shell">
      <BotanicalBackground />

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <LotusIcon size={54} />
          <strong>Meynool</strong>
          <small>மெய்நூல்</small>
        </div>
        <div className="nav-caption">Explore</div>
        <nav className="nav-list" aria-label="Main navigation">
          {NAV_ITEMS.map(item=>(
            <a key={item.id} className={`nav-item${item.active?' active':''}`} href={`#${item.id}`}>
              <span className="nav-icon"><item.icon /></span>
              {item.label}
            </a>
          ))}
        </nav>
        <div className="nav-divider" />
        <nav className="nav-list" aria-label="Secondary navigation">
          {SECONDARY_ITEMS.map(item=>(
            <a key={item.id} className="nav-item" href={`#${item.id}`}>
              <span className="nav-icon"><item.icon /></span>
              {item.label}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-quote">“அறிவும் இயற்கையும் ஒன்றே உலகம்”</div>
          <div className="sidebar-version">LOCAL WORKSPACE · STARTER 0.1</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content" id="home">
        {/* Top-right controls */}
        <div className="topbar-controls">
          <button className="control-btn" aria-label="Search" type="button"><SearchIcon /></button>
          <button className="control-btn" aria-label="Notifications" type="button"><BellIcon /></button>
          <div className="topbar-user" role="button" tabIndex={0} aria-label="User menu">
            <div className="topbar-avatar">J</div>
            <span className="topbar-username">Jessie</span>
            <span className="topbar-chevron">▼</span>
          </div>
        </div>

        {/* Hero */}
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><span>TAMIL LITERATURE</span><span className="eyebrow-line" /><span>×</span><span className="eyebrow-line" /><span>SCIENTIFIC EXPLORATION</span></div>
            <h1>
              Ancient wisdom.<br />
              <span className="line-two">Living knowledge.</span>
            </h1>
            <p className="hero-subtitle">Explore Tamil literary heritage alongside modern scientific research.</p>
          </div>
        </section>

        {/* Search + pills */}
        <section style={{ paddingTop:10 }}>
          <form className="search-form" onSubmit={submitSearch}>
            <span className="search-icon"><SearchIcon /></span>
            <input
              aria-label="Search Tamil texts, scientific concepts, or research topics"
              value={query}
              onChange={e=>setQuery(e.target.value)}
              placeholder="Search Tamil texts, scientific concepts, or research topics..."
            />
            <button type="submit" className="search-go" aria-label="Search">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
                <path d="M5 12 L19 12 M15 8 L20.5 13.5 M15 16 L20.5 9.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity=".95" />
                <circle cx="9.5" cy="9.5" r="4" stroke="currentColor" strokeWidth="1.6" opacity=".95" fill="none" />
              </svg>
            </button>
          </form>
          <div className="search-pills">
            <span className="try-label">Try:</span>
            <div className="pill-list">
              {SUGGEST_PILLS.map(p=>(
                <button key={p} className="search-pill" type="button">{p}</button>
              ))}
            </div>
          </div>
        </section>

        {/* Discovery cards */}
        <section style={{ paddingTop:6 }}>
          <div className="cards-row">
            {DISCOVERY_CARDS.map(card=>(
              <article key={card.id} className="discovery-card">
                <div className={`card-icon ${card.iconKind}`}>
                  <card.icon />
                </div>
                <h3>{card.title}</h3>
                <p>{card.desc}</p>
                <button className="card-action" type="button" aria-label={`Explore ${card.title}`}>
                  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
                    <path d="M8 6 L17 12 L8 18" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" opacity=".9" />
                  </svg>
                </button>
              </article>
            ))}
          </div>
        </section>

        {/* Platform status */}
        <section style={{ paddingBottom:4 }}>
          <div className="status-bar">
            <div className="status-header">Platform Status</div>
            <div className="status-col">
              <div className="status-indicator"><LeafIcon /></div>
              <div className="status-title">API</div>
              <div className="status-sub">Not connected</div>
            </div>
            <div className="status-col">
              <div className="status-indicator"><DiscsIcon /></div>
              <div className="status-title">Database</div>
              <div className="status-sub">Not connected</div>
            </div>
            <div className="status-col">
              <div className="status-indicator"><DocCheckIcon /></div>
              <div className="status-title">Research Data</div>
              <div className="status-sub">Not yet available</div>
            </div>
          </div>
        </section>

        <footer className="page-footer">
          <span>மெய்நூல் · MEYNOOL</span>
          <span>Truth. Text. Evidence.</span>
          <span>Local-first · Research use only</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
