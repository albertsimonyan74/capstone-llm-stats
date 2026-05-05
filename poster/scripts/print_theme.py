"""Print theme for poster figures.

Mirrors scripts/site_palette.py but targets light-background, dark-text
print output for the A0 capstone poster. SVG primary (vector, infinitely
scalable, selectable text) + PNG@600dpi fallback.
"""

# ============================================================================
# Canonical print palette
# ============================================================================

PRINT_BG       = "#ffffff"  # white background
PRINT_FG       = "#0f172a"  # slate-900 dark navy text
PRINT_FG_MUTED = "#475569"  # slate-500 secondary text
PRINT_GRID     = "#e2e8f0"  # slate-200 gridlines

# Print-safe model colors — darker tailwind -600 shades. The website pastels
# (#5eead4, #86efac, etc.) wash out on light bg and lose contrast in CMYK.
MODEL_COLORS_PRINT = {
    "claude":   "#0d9488",  # teal-600    (was #5eead4 on web)
    "chatgpt":  "#16a34a",  # green-600   (was #86efac)
    "gemini":   "#e11d48",  # rose-600    (was #fda4af)
    "deepseek": "#2563eb",  # blue-600    (was #93c5fd)
    "mistral":  "#7c3aed",  # violet-600  (was #c4b5fd)
}

# Generic accents
ACCENT_TEAL_PRINT   = "#0d9488"
ACCENT_PURPLE_PRINT = "#7c3aed"
ACCENT_GOLD_PRINT   = "#d97706"  # amber-600

# Semantic colors
COLOR_GOOD_PRINT    = "#059669"  # emerald-600
COLOR_BAD_PRINT     = "#dc2626"  # red-600
COLOR_NEUTRAL_PRINT = "#64748b"  # slate-500

# Bucket colors (calibration small-multiples)
BUCKET_COLORS_PRINT = {
    0.3: ACCENT_TEAL_PRINT,
    0.5: ACCENT_PURPLE_PRINT,
    0.6: ACCENT_GOLD_PRINT,
}


def apply_print_theme():
    """Set matplotlib rcParams for print-quality SVG + PNG output."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor":  PRINT_BG,
        "axes.facecolor":    PRINT_BG,
        "savefig.facecolor": PRINT_BG,
        "text.color":        PRINT_FG,
        "axes.labelcolor":   PRINT_FG,
        "axes.edgecolor":    PRINT_FG_MUTED,
        "xtick.color":       PRINT_FG,
        "ytick.color":       PRINT_FG,
        "grid.color":        PRINT_GRID,
        "grid.alpha":        0.6,
        "savefig.dpi":       600,
        "svg.fonttype":      "none",  # text stays as text in SVG
        "pdf.fonttype":      42,       # embed fonts in PDF
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size":         12,
        "axes.titlesize":    14,
        "axes.labelsize":    12,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def dim_remaining_spines(ax, alpha: float = 0.3):
    """Dim bottom + left spines (top + right hidden globally via rcParams)."""
    for side in ("bottom", "left"):
        if side in ax.spines:
            ax.spines[side].set_alpha(alpha)


def dual_save(fig, basename, out_dir="poster/figures"):
    """Save figure as both SVG (primary) and PNG@600dpi (fallback)."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(f"{out_dir}/{basename}.svg", format="svg", bbox_inches="tight")
    fig.savefig(f"{out_dir}/{basename}.png", format="png", dpi=600, bbox_inches="tight")
    print(f"  ✓ {out_dir}/{basename}.svg")
    print(f"  ✓ {out_dir}/{basename}.png")
