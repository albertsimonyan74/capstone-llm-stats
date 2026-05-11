## 13_pass_rate.R
## Pass-rate grouped bar chart: X=tier, grouped by model, Y=pass rate.
## Much more readable than heatmap for 4 tiers × 5 models.
## Outputs: figures/13_pass_rate.png (2000×1200)
##          interactive/13_pass_rate.html

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales)
})

PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"
ACCENT     <- "#00FFE0"
PASS_THR   <- 0.5

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
df_c <- df %>%
  filter(model_family %in% COMPLETE) %>%
  mutate(
    model_family = factor(model_family, levels = COMPLETE),
    tier_lab     = paste0("Tier ", tier, " — ", c("1"="Basic","2"="Intermediate","3"="Advanced","4"="Expert")[as.character(tier)])
  )

pass_data <- df_c %>%
  group_by(tier, tier_lab, model_family) %>%
  summarise(
    n_pass  = sum(final_score >= PASS_THR, na.rm = TRUE),
    n_total = n(),
    rate    = n_pass / n_total,
    .groups = "drop"
  ) %>%
  mutate(tier_lab = factor(tier_lab, levels = unique(tier_lab[order(tier)])))

# ── ggplot2 grouped bar chart ─────────────────────────────────
p <- ggplot(pass_data, aes(x = tier_lab, y = rate, fill = model_family)) +
  geom_col(position = position_dodge(width = 0.82), width = 0.70, alpha = 0.92) +
  geom_text(
    aes(label = paste0(round(rate * 100), "%")),
    position = position_dodge(width = 0.82),
    vjust = -0.5, size = 2.8, fontface = "bold", color = TEXT_CLR
  ) +
  geom_hline(yintercept = PASS_THR, linetype = "dashed",
             color = ACCENT, linewidth = 0.7, alpha = 0.75) +
  annotate("text", x = 0.52, y = PASS_THR + 0.025,
           label = "Pass threshold (50%)", color = ACCENT,
           size = 3, hjust = 0, fontface = "italic") +
  scale_fill_manual(values = PALETTE, name = "Model") +
  scale_y_continuous(limits = c(0, 1.08),
                     labels = percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2)) +
  labs(
    title    = "Pass Rate by Difficulty Tier — All 5 Models",
    subtitle = "Grouped bars per tier  ·  Dashed = 50% pass threshold  ·  n = 171 tasks × 5 models",
    x = NULL, y = "Pass Rate"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.y = element_line(color = "#1E2A50", linewidth = 0.4),
    panel.grid.major.x = element_blank(),
    panel.grid.minor   = element_blank(),
    axis.text.x       = element_text(color = TEXT_CLR, size = 11, face = "bold"),
    axis.text.y       = element_text(color = TEXT_CLR, size = 10),
    axis.title.y      = element_text(color = TEXT_CLR),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text       = element_text(color = TEXT_CLR, size = 10),
    legend.title      = element_text(color = ACCENT, face = "bold", size = 10),
    legend.position   = "right",
    plot.title        = element_text(color = ACCENT, face = "bold", size = 14, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    plot.margin       = margin(16, 16, 16, 16)
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/13_pass_rate.png", plot = p,
       width = 2000, height = 1200, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/13_pass_rate.png")

# ── Interactive plotly grouped bar ────────────────────────────
fig_ly <- plot_ly(pass_data,
  x     = ~tier_lab,
  y     = ~rate,
  color = ~model_family,
  colors = PALETTE[c("claude","chatgpt","deepseek","gemini","mistral")],
  type  = "bar",
  text  = ~paste0(model_family, ": ", round(rate*100,1), "%<br>(", n_pass, "/", n_total, " tasks)"),
  hoverinfo = "text"
) %>%
  layout(
    barmode = "group",
    title   = list(text = "Pass Rate by Tier — All 5 Models",
                   font = list(color = ACCENT, size = 16)),
    xaxis   = list(title = "", tickfont = list(color = TEXT_CLR, size = 11)),
    yaxis   = list(title = "Pass Rate", tickformat = ".0%",
                   range = c(0, 1.05),
                   color = TEXT_CLR,
                   gridcolor = "#1E2A50"),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    legend = list(font = list(color = TEXT_CLR)),
    shapes = list(list(
      type = "line", x0 = 0, x1 = 1, xref = "paper",
      y0 = PASS_THR, y1 = PASS_THR,
      line = list(color = ACCENT, dash = "dash", width = 1.5)
    ))
  )

htmlwidgets::saveWidget(fig_ly, "interactive/13_pass_rate.html", selfcontained = FALSE)
message("Saved: interactive/13_pass_rate.html")
message("13_pass_rate.R complete.\n")
