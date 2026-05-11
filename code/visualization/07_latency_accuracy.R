## 07_latency_accuracy.R
## Side-by-side ranked bar comparison: accuracy rank (left) + speed rank (right).
## 5 models, clear ranking, no ambiguous scatter with 5 points.
## Exports PNG and HTML.

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales", "patchwork")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales); library(patchwork)
})

PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
MODEL_LABELS <- c(claude="Claude", chatgpt="ChatGPT", mistral="Mistral",
                  deepseek="DeepSeek", gemini="Gemini")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#12193A"
TEXT_CLR   <- "#E8F4F8"
ACCENT     <- "#00FFE0"

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")
df_complete <- df %>% filter(!is.na(model_family))

model_agg <- df_complete %>%
  group_by(model_family) %>%
  summarise(
    avg_score   = mean(final_score, na.rm = TRUE),
    avg_latency = mean(latency_ms,  na.rm = TRUE),
    pass_rate   = mean(pass,        na.rm = TRUE),
    n_tasks     = n(),
    .groups     = "drop"
  ) %>%
  mutate(
    label       = MODEL_LABELS[model_family],
    color       = PALETTE[model_family],
    acc_rank    = rank(-avg_score),
    speed_rank  = rank(avg_latency),
    lat_sec     = avg_latency / 1000
  ) %>%
  arrange(acc_rank)

dark_bar <- function() {
  theme_minimal(base_size = 12) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.x = element_line(color = "#1E2A50", linewidth = 0.35),
    panel.grid.major.y = element_blank(),
    panel.grid.minor  = element_blank(),
    axis.text         = element_text(color = TEXT_CLR, size = 11),
    axis.title        = element_text(color = TEXT_CLR, size = 10),
    plot.title        = element_text(color = ACCENT, face = "bold", size = 13, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    legend.position   = "none",
    plot.margin       = margin(12, 16, 12, 16)
  )
}

# ── Panel A: Accuracy (sorted best → worst) ───────────────────
agg_acc <- model_agg %>% arrange(avg_score) %>%
  mutate(label = factor(label, levels = label))

pA <- ggplot(agg_acc, aes(x = avg_score, y = label, fill = model_family)) +
  geom_col(width = 0.62, alpha = 0.92) +
  geom_text(aes(label = sprintf("%.1f%%", avg_score * 100)),
            hjust = -0.12, size = 3.5, fontface = "bold", color = TEXT_CLR) +
  geom_vline(xintercept = 0.5, linetype = "dashed",
             color = ACCENT, linewidth = 0.7, alpha = 0.7) +
  scale_fill_manual(values = PALETTE) +
  scale_x_continuous(limits = c(0, 0.85), labels = percent_format(accuracy = 1)) +
  labs(title = "Average Score", subtitle = "Higher = better", x = NULL, y = NULL) +
  dark_bar()

# ── Panel B: Speed (sorted fastest → slowest) ─────────────────
agg_spd <- model_agg %>% arrange(desc(avg_latency)) %>%
  mutate(label = factor(label, levels = label))

pB <- ggplot(agg_spd, aes(x = lat_sec, y = label, fill = model_family)) +
  geom_col(width = 0.62, alpha = 0.92) +
  geom_text(aes(label = sprintf("%.1fs", lat_sec)),
            hjust = -0.12, size = 3.5, fontface = "bold", color = TEXT_CLR) +
  scale_fill_manual(values = PALETTE) +
  scale_x_continuous(limits = c(0, max(agg_spd$lat_sec) * 1.22),
                     labels = number_format(suffix = "s", accuracy = 0.1)) +
  labs(title = "Avg Response Time", subtitle = "Lower = faster", x = NULL, y = NULL) +
  dark_bar()

combined <- pA + pB +
  plot_annotation(
    title   = "Speed vs. Accuracy — All 5 Models",
    subtitle = "Left: benchmark score (higher = better)   ·   Right: response latency (lower = faster)",
    theme = theme(
      plot.background = element_rect(fill = DARK_BG, color = NA),
      plot.title      = element_text(color = ACCENT, face = "bold", size = 15, hjust = 0.5),
      plot.subtitle   = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
      plot.margin     = margin(16, 8, 8, 8)
    )
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/07_latency_accuracy.png", combined,
       width = 2200, height = 1000, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/07_latency_accuracy.png")

# ── Interactive plotly: clean grouped horizontal bars ─────────
model_long <- model_agg %>%
  mutate(
    acc_pct = round(avg_score * 100, 1),
    lat_s   = round(lat_sec, 2)
  )

fig_acc <- plot_ly(
  model_long %>% arrange(avg_score),
  x         = ~avg_score, y = ~label,
  type      = "bar", orientation = "h",
  marker    = list(color = ~color, opacity = 0.92,
                   line = list(color = "rgba(255,255,255,0.1)", width = 0.5)),
  text      = ~paste0(acc_pct, "%"),
  textposition = "outside",
  cliponaxis   = FALSE,
  hovertext = ~paste0("<b>", label, "</b><br>Score: ", acc_pct,
                      "%<br>Pass rate: ", round(pass_rate * 100, 1), "%"),
  hoverinfo = "text",
  name      = "Score"
) %>%
  layout(
    title  = list(text = "Average Benchmark Score",
                  font = list(color = ACCENT, size = 13)),
    xaxis  = list(title = "Score", tickformat = ".0%", color = TEXT_CLR,
                  gridcolor = "#1E2A50", range = c(0, 0.95),
                  tickfont  = list(color = TEXT_CLR)),
    yaxis  = list(title = "", color = TEXT_CLR,
                  tickfont = list(color = TEXT_CLR, size = 12)),
    paper_bgcolor = DARK_BG, plot_bgcolor = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    margin = list(l = 90, r = 40, t = 50, b = 50),
    shapes = list(list(type = "line", x0 = 0.5, x1 = 0.5,
                       y0 = 0, y1 = 1, yref = "paper",
                       line = list(color = ACCENT, dash = "dash", width = 1.5)))
  )

fig_lat <- plot_ly(
  model_long %>% arrange(desc(lat_sec)),
  x         = ~lat_sec, y = ~label,
  type      = "bar", orientation = "h",
  marker    = list(color = ~color, opacity = 0.92,
                   line = list(color = "rgba(255,255,255,0.1)", width = 0.5)),
  text      = ~paste0(lat_s, "s"),
  textposition = "outside",
  cliponaxis   = FALSE,
  hovertext = ~paste0("<b>", label, "</b><br>Latency: ", lat_s, "s"),
  hoverinfo = "text",
  name      = "Latency"
) %>%
  layout(
    title  = list(text = "Avg Response Time (lower = faster)",
                  font = list(color = ACCENT, size = 13)),
    xaxis  = list(title = "Seconds", color = TEXT_CLR, gridcolor = "#1E2A50",
                  range = c(0, max(model_long$lat_sec) * 1.28),
                  tickfont = list(color = TEXT_CLR)),
    yaxis  = list(title = "", color = TEXT_CLR,
                  tickfont = list(color = TEXT_CLR, size = 12)),
    paper_bgcolor = DARK_BG, plot_bgcolor = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    margin = list(l = 90, r = 50, t = 50, b = 50)
  )

fig_combined <- subplot(
  fig_acc, fig_lat,
  nrows = 1, titleX = TRUE, titleY = TRUE,
  shareX = FALSE, shareY = FALSE, margin = 0.08
) %>%
  layout(
    title      = list(text = "Speed vs. Accuracy — All 5 Models",
                      font = list(color = ACCENT, size = 17)),
    paper_bgcolor = DARK_BG,
    font       = list(color = TEXT_CLR),
    showlegend = FALSE,
    margin     = list(l = 20, r = 20, t = 70, b = 40)
  )

htmlwidgets::saveWidget(fig_combined, "interactive/07_latency_accuracy.html",
                        selfcontained = FALSE)
message("Saved: interactive/07_latency_accuracy.html")
message("07_latency_accuracy.R complete.\n")
