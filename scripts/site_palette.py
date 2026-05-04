"""Canonical site palette and matplotlib theming.

Single source of truth for every visualization-generating script. Import
from here and call apply_site_theme() once at the top of each script.

Mirrors capstone-website/frontend/src/data/sitePalette.js — keep in sync.
"""

from __future__ import annotations

import matplotlib as mpl

# === SITE PALETTE ===
SITE_BG = '#0f1118'            # figure background (dark, blends w/ site)
SITE_FG = '#e2e8f0'            # primary text
SITE_FG_MUTED = '#94a3b8'      # axis labels, captions, muted text
SITE_FG_SUBTLE = '#475569'     # very subtle (footer captions, hints)

# === MODEL COLORS ===
# Used wherever a chart distinguishes models. NEVER deviate.
MODEL_COLORS = {
    'claude':   '#5eead4',  # teal
    'chatgpt':  '#86efac',  # mint
    'gemini':   '#fda4af',  # pink/coral
    'deepseek': '#93c5fd',  # blue
    'mistral':  '#c4b5fd',  # lavender
}

# Uppercase aliases for x-axis labels
MODEL_COLORS_UPPER = {k.upper(): v for k, v in MODEL_COLORS.items()}

# Title-case aliases (e.g. "Claude", "ChatGPT", "DeepSeek")
_TITLE_ALIASES = {
    'Claude':   '#5eead4',
    'ChatGPT':  '#86efac',
    'Chatgpt':  '#86efac',
    'Gemini':   '#fda4af',
    'DeepSeek': '#93c5fd',
    'Deepseek': '#93c5fd',
    'Mistral':  '#c4b5fd',
}

# === L1 BUCKET COLORS (Error Taxonomy) ===
# Used wherever L1 failure buckets appear. NEVER deviate.
BUCKET_COLORS = {
    'Assumption Violation': '#fbbf24',  # amber/gold
    'Mathematical Error':   '#f87171',  # coral
    'Formatting Failure':   '#94a3b8',  # slate
    'Conceptual Error':     '#a78bfa',  # lavender
    # 'Hallucination' deliberately absent — empty bucket per audit
}

# === ACCENT COLORS ===
ACCENT_TEAL = '#5eead4'
ACCENT_PURPLE = '#a78bfa'
ACCENT_CORAL = '#f87171'
ACCENT_GOLD = '#fbbf24'

# === SEMANTIC COLORS ===
COLOR_GOOD = '#10b981'      # green — positive / desirable
COLOR_BAD = '#ef4444'       # red — negative / undesirable
COLOR_NEUTRAL = '#94a3b8'   # slate — neutral


def apply_site_theme():
    """Apply site theme to matplotlib globally. Call once per script."""
    mpl.rcParams.update({
        'figure.facecolor':  SITE_BG,
        'axes.facecolor':    SITE_BG,
        'savefig.facecolor': SITE_BG,

        'axes.edgecolor':    SITE_FG_MUTED,
        'axes.labelcolor':   SITE_FG_MUTED,
        'axes.linewidth':    0.8,
        'axes.titlecolor':   SITE_FG,
        'axes.titlesize':    13,
        'axes.titleweight':  '700',
        'axes.titlepad':     16,

        # Hide top + right spines globally
        'axes.spines.top':   False,
        'axes.spines.right': False,

        'xtick.color':       SITE_FG_MUTED,
        'ytick.color':       SITE_FG_MUTED,
        'xtick.labelsize':   9,
        'ytick.labelsize':   9,

        'grid.color':        '#ffffff',
        'grid.alpha':        0.06,
        'grid.linewidth':    0.5,
        'grid.linestyle':    '-',

        'legend.frameon':    False,
        'legend.fontsize':   10,
        'legend.labelcolor': SITE_FG_MUTED,

        'font.family':       'sans-serif',
        'font.sans-serif':   ['Inter', 'Helvetica', 'Arial', 'sans-serif'],
        'font.size':         10,
        'text.color':        SITE_FG,
    })


def model_color(name: str) -> str:
    """Lookup a model color by any common casing. Falls back to neutral."""
    if not name:
        return COLOR_NEUTRAL
    key = name.lower()
    if key in MODEL_COLORS:
        return MODEL_COLORS[key]
    if name in MODEL_COLORS_UPPER:
        return MODEL_COLORS_UPPER[name]
    if name in _TITLE_ALIASES:
        return _TITLE_ALIASES[name]
    return COLOR_NEUTRAL


def color_code_model_ticks(ax, axis: str = 'x'):
    """After axis tick labels are model names, color each by model.

    Tries lowercase, uppercase, and title-cased keys in turn.
    """
    labels = ax.get_xticklabels() if axis == 'x' else ax.get_yticklabels()
    for tl in labels:
        text = tl.get_text()
        if not text:
            continue
        color = (
            MODEL_COLORS.get(text.lower())
            or MODEL_COLORS_UPPER.get(text)
            or _TITLE_ALIASES.get(text)
        )
        if color:
            tl.set_color(color)
            tl.set_fontweight('700')


def dim_remaining_spines(ax, alpha: float = 0.3):
    """Dim bottom + left spines (top + right hidden globally via rcParams)."""
    for side in ('bottom', 'left'):
        if side in ax.spines:
            ax.spines[side].set_alpha(alpha)


def style_colorbar(cbar, label: str = ''):
    """Apply site theme to a matplotlib Colorbar."""
    if label:
        cbar.set_label(label, color=SITE_FG_MUTED, fontsize=9)
    cbar.ax.tick_params(colors=SITE_FG_MUTED, labelsize=8)
    if cbar.outline is not None:
        cbar.outline.set_edgecolor(SITE_FG_MUTED)
        cbar.outline.set_alpha(0.3)


def model_color_list(names):
    """Return [color] aligned to the input names list."""
    return [model_color(n) for n in names]
