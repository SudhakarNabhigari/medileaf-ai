import React from 'react';
import { Check } from 'lucide-react';

export function MediLeafLogo({ className = 'w-9 h-9' }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className} aria-hidden="true">
      <rect width="64" height="64" rx="16" fill="#064E32" />
      <path
        d="M47 16C31 16 20 26 19 42C19 44.5 19.5 46.5 20 48C21.5 48.5 23.5 49 26 49C41 49 48 36 47 16Z"
        fill="#84CC16"
      />
      <path d="M16 49C23 41 33 31 44 21" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round" />
      <path d="M26 38C27 33 29 29 33 26" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
      <path d="M32 37C36 36 39 34 42 30" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export function LeafScannerGraphic({
  badgeLabel = 'Medicinal Leaf Recognition',
  subLabel,
  compact = false,
}: {
  badgeLabel?: string;
  subLabel?: string;
  compact?: boolean;
}) {
  return (
    <div className={`relative flex items-center justify-center ${compact ? 'w-44 h-36' : 'w-56 h-48'}`}>
      {/* Grid backdrop */}
      <svg viewBox="0 0 220 180" fill="none" className="w-full h-full" aria-hidden="true">
        <defs>
          <radialGradient id="leafGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#A3E635" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#053821" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="scanLeaf" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#A3E635" />
            <stop offset="100%" stopColor="#22C55E" />
          </linearGradient>
        </defs>
        <circle cx="110" cy="90" r="82" fill="url(#leafGlow)" />
        {/* Scanner corner brackets */}
        <path d="M32 42V22H52" stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M168 22H188V42" stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M32 138V158H52" stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M168 158H188V138" stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />

        {/* Central scanned botanical leaf */}
        <path
          d="M66 134C64 84 95 44 156 32C152 92 120 130 66 134Z"
          fill="url(#scanLeaf)"
        />
        <path d="M67 132C94 102 124 72 153 35" stroke="#ECFCCB" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M90 108C94 92 103 80 116 70M108 90C122 88 134 80 142 68" stroke="#ECFCCB" strokeWidth="1.6" strokeOpacity="0.75" strokeLinecap="round" />

        {/* Neural mesh overlay nodes */}
        <circle cx="105" cy="86" r="2.5" fill="#FFFFFF" />
        <circle cx="125" cy="64" r="2.5" fill="#FFFFFF" />
        <circle cx="92" cy="108" r="2.5" fill="#FFFFFF" />
        <path d="M92 108L105 86L125 64" stroke="#FFFFFF" strokeOpacity="0.65" strokeWidth="1" />
      </svg>

      {/* Recognition overlay badge */}
      <div className="absolute bottom-3 right-0 bg-[#052E1C]/90 backdrop-blur border border-emerald-300/35 rounded-xl px-3 py-1.5 flex items-center gap-2 shadow-lg">
        <div className="text-[11px] leading-tight text-white">
          <div className="font-semibold">{badgeLabel}</div>
          {subLabel && <div className="text-[10px] text-lime-300">{subLabel}</div>}
        </div>
        <span className="w-4 h-4 rounded-full bg-[#84CC16] text-[#052E1C] flex items-center justify-center shrink-0">
          <Check className="w-2.5 h-2.5 stroke-[3]" />
        </span>
      </div>
    </div>
  );
}

export function BotanicalHeroArt({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 320 220" fill="none" className={className} aria-hidden="true">
      <defs>
        <linearGradient id="bgLeafGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#22C55E" stopOpacity="0.92" />
          <stop offset="100%" stopColor="#064E32" stopOpacity="0.98" />
        </linearGradient>
      </defs>
      <path d="M65 185C62 115 108 55 198 38C194 122 146 176 65 185Z" fill="url(#bgLeafGrad)" />
      <path d="M67 183C108 138 152 94 196 42" stroke="#DCFCE7" strokeWidth="3" strokeLinecap="round" />
      <path d="M148 192C155 142 192 106 254 96C248 150 210 188 148 192Z" fill="#84CC16" fillOpacity="0.85" />
      <path d="M150 190C182 158 214 126 250 100" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  );
}

export function CornerLeafPattern({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 180 140" fill="none" className={className} aria-hidden="true">
      <path
        d="M25 125C25 75 68 35 135 28C128 84 85 122 25 125Z"
        stroke="#2F855A"
        strokeOpacity="0.22"
        strokeWidth="2"
        fill="#75B798"
        fillOpacity="0.14"
      />
      <path
        d="M28 122C62 88 96 58 132 31"
        stroke="#2F855A"
        strokeOpacity="0.28"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
