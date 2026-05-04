// Canonical site palette for Recharts components.
// Mirrors scripts/site_palette.py — keep in sync.

export const SITE_PALETTE = {
  bg: '#0f1118',
  fg: '#e2e8f0',
  fgMuted: '#94a3b8',
  fgSubtle: '#475569',
};

export const MODEL_COLORS = {
  claude:   '#5eead4',
  chatgpt:  '#86efac',
  gemini:   '#fda4af',
  deepseek: '#93c5fd',
  mistral:  '#c4b5fd',
};

export const MODEL_COLORS_ARRAY = [
  MODEL_COLORS.claude,
  MODEL_COLORS.chatgpt,
  MODEL_COLORS.gemini,
  MODEL_COLORS.deepseek,
  MODEL_COLORS.mistral,
];

// Lookup helper — accepts any common casing.
export function modelColor(name) {
  if (!name) return SITE_PALETTE.fgMuted;
  const key = String(name).toLowerCase();
  return MODEL_COLORS[key] || SITE_PALETTE.fgMuted;
}

export const BUCKET_COLORS = {
  'Assumption Violation': '#fbbf24',
  'Mathematical Error':    '#f87171',
  'Formatting Failure':    '#94a3b8',
  'Conceptual Error':      '#a78bfa',
};

export const ACCENTS = {
  teal:   '#5eead4',
  purple: '#a78bfa',
  coral:  '#f87171',
  gold:   '#fbbf24',
};

export const SEMANTIC = {
  good:    '#10b981',
  bad:     '#ef4444',
  neutral: '#94a3b8',
};

// === Recharts shared style constants ===
export const RECHARTS_THEME = {
  // Tooltip styling: dark bg, white text, subtle border
  tooltipContentStyle: {
    background: 'rgba(15, 19, 28, 0.96)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: 8,
    padding: '8px 12px',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
  },
  tooltipLabelStyle: {
    color: SITE_PALETTE.fg,
    fontWeight: 600,
    fontSize: 12,
  },
  tooltipItemStyle: {
    color: SITE_PALETTE.fg,
    fontSize: 11,
  },

  // Cartesian grid
  gridStroke: 'rgba(255, 255, 255, 0.06)',
  gridStrokeDasharray: '3 3',

  // Axis
  axisStroke: 'rgba(148, 163, 184, 0.3)',
  axisTickColor: SITE_PALETTE.fgMuted,
  axisTickFontSize: 11,
  axisLabelColor: SITE_PALETTE.fgMuted,
  axisLabelFontSize: 12,

  // Reference lines
  referenceLineStroke: SITE_PALETTE.fgMuted,
  referenceLineStrokeDasharray: '4 4',
};
