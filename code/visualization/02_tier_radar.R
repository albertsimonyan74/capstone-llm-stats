## 02_tier_radar.R
## Slope chart (bump chart): model performance from Tier 1 → Tier 4.
## Much more readable than spider chart — shows which models degrade fastest.
## Exports: figures/02_tier_radar_bar.png + interactive/02_tier_radar.html

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "tidyr", "scales", "ggrepel")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(tidyr); library(scales); library(ggrepel)
})

PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#12193A"
TEXT_CLR   <- "#E8F4F8"
ACCENT     <- "#00FFE0"

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
MODEL_LABELS <- c(claude="Claude", chatgpt="ChatGPT", deepseek="DeepSeek",
                  gemini="Gemini", mistral="Mistral")

tier_agg <- df %>%
  filter(model_family %in% COMPLETE) %>%
  group_by(model_family, tier) %>%
  summarise(
    avg_score = mean(final_score, na.rm = TRUE),
    n = n(),
    .groups = "drop"
  ) %>%
  mutate(
    tier_lab   = paste0("Tier ", tier),
    model_label = MODEL_LABELS[model_family]
  )

tier_agg$tier_lab <- factor(tier_agg$tier_lab,
  levels = c("Tier 1", "Tier 2", "Tier 3", "Tier 4"))

# ── Slope / line chart ────────────────────────────────────────
# Label positions: right side of chart (Tier 4)
right_labels <- tier_agg %>% filter(tier == 4) %>% arrange(desc(avg_score))

p_slope <- ggplot(tier_agg, aes(x = tier_lab, y = avg_score,
                                 color = model_family, group = model_family)) +
  # Pass threshold
  geom_hline(yintercept = 0.5, linetype = "dashed",
             color = ACCENT, linewidth = 0.6, alpha = 0.6) +
  annotate("text", x = 0.55, y = 0.515, label = "Pass threshold",
           color = ACCENT, size = 2.8, hjust = 0, fontface = "italic") +
  # Shaded area under lines
  geom_ribbon(aes(ymin = 0, ymax = avg_score, fill = model_family),
              alpha = 0.04, color = NA) +
  # Lines
  geom_line(linewidth = 1.6, alpha = 0.9) +
  # Points
  geom_point(size = 5, shape = 21, aes(fill = model_family),
             color = "white", stroke = 0.7) +
  # Score labels on points
  geom_text(aes(label = sprintf("%.0f%%", avg_score * 100)),
            vjust = -1.1, size = 3, fontface = "bold") +
  # Right-side model name labels
  geom_text_repel(
    data = right_labels,
    aes(label = model_label),
    direction = "y", hjust = -0.2, size = 3.5, fontface = "bold",
    min.segment.length = 0,
    nudge_x = 0.15,
    segment.color = "transparent"
  ) +
  scale_color_manual(values = PALETTE, name = "Model") +
  scale_fill_manual (values = PALETTE, guide = "none") +
  scale_y_continuous(limits = c(0.25, 1.05),
                     labels = percent_format(accuracy = 1),
                     breaks = seq(0.3, 1.0, 0.1)) +
  scale_x_discrete(expand = expansion(add = c(0.3, 0.8))) +
  labs(
    title    = "Performance Across Difficulty Tiers",
    subtitle = "Each line shows how a model's pass rate changes from Basic (Tier 1) to Expert (Tier 4)",
    x = "Difficulty Tier", y = "Average Score"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.y = element_line(color = "#1E2A50", linewidth = 0.35),
    panel.grid.major.x = element_line(color = "#1E2A5055", linewidth = 0.25, linetype = "dotted"),
    panel.grid.minor   = element_blank(),
    axis.text         = element_text(color = TEXT_CLR, size = 11),
    axis.title        = element_text(color = TEXT_CLR, size = 10),
    legend.position   = "none",
    plot.title        = element_text(color = ACCENT, face = "bold", size = 14, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    plot.margin       = margin(16, 48, 16, 16)
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/02_tier_radar_bar.png", p_slope,
       width = 1800, height = 1100, units = "px", dpi = 150, bg = DARK_BG)
message("Saved: figures/02_tier_radar_bar.png")

# ── Interactive plotly slope chart ────────────────────────────
fig_ly <- plot_ly()

for (mdl in COMPLETE) {
  d <- tier_agg %>% filter(model_family == mdl) %>% arrange(tier)
  fig_ly <- fig_ly %>% add_trace(
    x    = d$tier_lab,
    y    = d$avg_score,
    type = "scatter",
    mode = "lines+markers",
    name = MODEL_LABELS[mdl],
    line   = list(color = PALETTE[mdl], width = 3),
    marker = list(color = PALETTE[mdl], size = 12,
                  line = list(color = "white", width = 2)),
    text   = paste0(MODEL_LABELS[mdl], "<br>", d$tier_lab,
                    "<br>Score: ", round(d$avg_score * 100, 1), "%<br>n = ", d$n),
    hoverinfo = "text"
  )
}

fig_ly <- fig_ly %>%
  layout(
    title  = list(text = "Performance Across Difficulty Tiers",
                  font = list(color = ACCENT, size = 16)),
    xaxis  = list(title = "Difficulty Tier", color = TEXT_CLR,
                  tickfont = list(size = 12)),
    yaxis  = list(title = "Average Score", tickformat = ".0%",
                  color = TEXT_CLR, range = c(0.25, 1.02),
                  gridcolor = "#1E2A50"),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    legend = list(font = list(color = TEXT_CLR)),
    shapes = list(list(
      type = "line", x0 = 0, x1 = 1, xref = "paper",
      y0 = 0.5, y1 = 0.5,
      line = list(color = ACCENT, dash = "dash", width = 1.5)
    ))
  )

htmlwidgets::saveWidget(fig_ly, "interactive/02_tier_radar.html", selfcontained = FALSE)
message("Saved: interactive/02_tier_radar.html")
message("02_tier_radar.R complete.\n")
