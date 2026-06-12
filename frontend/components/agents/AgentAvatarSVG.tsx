'use client';
import { useId } from 'react';
import type { Agent } from '@/lib/types';
import { AVATAR_CONFIG } from '@/lib/data';

interface Props {
  agent: Agent;
  size?: number;
  className?: string;
  showBadge?: boolean;
}

/**
 * Hand-drawn SVG avatar for each Angeleck agent.
 * Morphology (skin, hair, outfit, glasses, crown…) comes from AVATAR_CONFIG.
 */
export default function AgentAvatarSVG({ agent, size = 90, className = '', showBadge = true }: Props) {
  const uid = useId().replace(/:/g, '');
  const cfg = AVATAR_CONFIG[agent.id] ?? { skin: '#D4A76A', hair: '#2C1810', outfit: agent.color };
  const { skin, hair, outfit, female, hasGlasses, hasCrown, hasTie, hasBeard, braids, hasBeret, hasBob } = cfg;
  const bg = agent.gradient;
  const color = agent.color;
  const darkEye = '#1A1A2E';
  const g = `av_${uid}`;

  // ── Hair shapes ──────────────────────────────────────────────
  let hairSVG: JSX.Element | null = null;
  if (hasCrown) {
    hairSVG = (
      <>
        <path d="M36 30 L39 20 L48 27 L50 16 L52 27 L61 20 L64 30 Z" fill="#F59E0B" />
        <circle cx="50" cy="18" r="3" fill="#EF4444" />
        <circle cx="39" cy="25" r="2" fill="#3B82F6" />
        <circle cx="61" cy="25" r="2" fill="#10B981" />
      </>
    );
  } else if (braids) {
    hairSVG = (
      <>
        <ellipse cx="50" cy="28" rx="20" ry="14" fill={hair} />
        <ellipse cx="50" cy="22" rx="16" ry="10" fill={hair} />
        <circle cx="38" cy="25" r="5" fill={hair} />
        <circle cx="62" cy="25" r="5" fill={hair} />
        <circle cx="30" cy="35" r="4" fill={hair} />
        <circle cx="70" cy="35" r="4" fill={hair} />
      </>
    );
  } else if (hasBeret) {
    hairSVG = (
      <>
        <path d="M30 38 Q30 22 50 20 Q70 22 70 38" fill={hair} />
        <ellipse cx="52" cy="24" rx="22" ry="9" fill="#881337" />
      </>
    );
  } else if (hasBob) {
    hairSVG = <path d="M30 45 Q28 25 50 22 Q72 25 70 45 L68 55 Q50 60 32 55 Z" fill={hair} />;
  } else if (female && !braids) {
    hairSVG = (
      <>
        <path d="M30 40 Q28 22 50 20 Q72 22 70 40 L72 65 Q50 72 28 65 Z" fill={hair} opacity={0.9} />
        <path d="M30 40 Q28 22 50 20 Q72 22 70 40" fill={hair} />
      </>
    );
  } else {
    hairSVG = <path d="M31 42 Q30 24 50 22 Q70 24 69 42 Q65 30 50 28 Q35 30 31 42 Z" fill={hair} />;
  }

  const beardSVG = hasBeard ? (
    <path d="M37 57 Q50 66 63 57 Q62 68 50 70 Q38 68 37 57 Z" fill={hair} opacity={0.6} />
  ) : null;

  const glassesSVG = hasGlasses ? (
    <>
      <rect x="35" y="43" width="13" height="9" rx="4" fill="none" stroke={darkEye} strokeWidth="1.5" opacity={0.6} />
      <rect x="52" y="43" width="13" height="9" rx="4" fill="none" stroke={darkEye} strokeWidth="1.5" opacity={0.6} />
      <line x1="48" y1="47" x2="52" y2="47" stroke={darkEye} strokeWidth="1.2" opacity={0.6} />
    </>
  ) : null;

  const tieSVG = hasTie ? (
    <path d="M46 75 L50 90 L54 75 L52 73 L50 76 L48 73 Z" fill={color} opacity={0.8} />
  ) : null;

  const outfitSVG = female ? (
    <>
      <path d="M20 100 Q22 80 35 76 L44 73 Q50 82 56 73 L65 76 Q78 80 80 100 Z" fill={outfit} />
      <path d="M44 73 L50 82 L56 73" fill="white" opacity={0.2} />
    </>
  ) : (
    <>
      <path d="M20 100 Q22 78 36 74 L46 71 Q50 82 54 71 L64 74 Q78 78 80 100 Z" fill={outfit} />
      <path d="M46 71 L50 80 L54 71" fill="white" opacity={0.15} />
      {tieSVG}
    </>
  );

  const hairBehind = !hasCrown && female && !braids;
  const hairFront = hasCrown || !female || braids || hasBeret;

  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <radialGradient id={g} cx="50%" cy="35%">
          <stop offset="0%" stopColor={bg[0]} stopOpacity={0.35} />
          <stop offset="100%" stopColor={bg[1]} stopOpacity={0.2} />
        </radialGradient>
        <clipPath id={`${g}clip`}>
          <circle cx="50" cy="50" r="50" />
        </clipPath>
      </defs>
      <circle cx="50" cy="50" r="50" fill={`url(#${g})`} />
      <g clipPath={`url(#${g}clip)`}>
        {outfitSVG}
        {hairBehind && hairSVG}
        <circle cx="50" cy="46" r="22" fill={skin} />
        <ellipse cx="28" cy="46" rx="4.5" ry="6" fill={skin} opacity={0.9} />
        <ellipse cx="72" cy="46" rx="4.5" ry="6" fill={skin} opacity={0.9} />
        {hairFront && hairSVG}
        {/* Eyes */}
        <ellipse cx="43" cy="43" rx="4.5" ry="5" fill="white" />
        <circle cx="44" cy="44" r="2.8" fill={darkEye} />
        <circle cx="45" cy="43" r="1" fill="white" />
        <ellipse cx="57" cy="43" rx="4.5" ry="5" fill="white" />
        <circle cx="58" cy="44" r="2.8" fill={darkEye} />
        <circle cx="59" cy="43" r="1" fill="white" />
        {/* Eyebrows */}
        <path d="M38 37 Q43 34.5 47 37" stroke={hair} strokeWidth="1.8" strokeLinecap="round" fill="none" />
        <path d="M53 37 Q57 34.5 62 37" stroke={hair} strokeWidth="1.8" strokeLinecap="round" fill="none" />
        {/* Nose */}
        <path d="M48.5 47 L47 52 L53 52" stroke={skin} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={0.6} />
        {/* Mouth */}
        <path d="M44 56 Q50 62 56 56" stroke={hair} strokeWidth="1.8" strokeLinecap="round" fill="none" opacity={0.7} />
        {beardSVG}
        {glassesSVG}
        <rect x="46" y="65" width="8" height="9" rx="2" fill={skin} opacity={0.95} />
      </g>
      {showBadge && (
        <>
          <circle cx="78" cy="78" r="14" fill={bg[1]} stroke="rgb(var(--bg-2))" strokeWidth="2.5" />
          <text x="78" y="83" textAnchor="middle" fontSize="13">{agent.emoji}</text>
        </>
      )}
    </svg>
  );
}
