## 12_latency_box.R
## Latency violin + boxplot hybrid, log-scale Y axis.
## One violin per model; outlier points shown.
## Outputs: figures/12_latency_box.png (2400×1600)
##          interactive/12_latency_box.html

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales)
})

PALETTE <- c(chatgpt = "#10A37F", deepseek = "#4D9FFF",
             mistral = "#FF7043", claude   = "#CC785C")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
df_c <- df %>%
  filter(model_family %in% COMPLETE, !is.na(latency_ms), latency_ms > 0) %>%
  mutate(model_family = factor(model_family, levels = COMPLETE))

# Median annotation
medians <- df_c %>%
  group_by(model_family) %>%
  summarise(med = median(latency_ms, na.rm = TRUE), .groups = "drop")

p <- ggplot(df_c, aes(x = model_family, y = latency_ms, fill = model_family)) +
  geom_violin(alpha = 0.45, color = NA, scale = "width", bw = "nrd0") +
  geom_boxplot(
    width = 0.18, outlier.shape = NA,
    color = "white", alpha = 0.75, linewidth = 0.5
  ) +
  # Outlier points
  geom_jitter(
    data = df_c %>%
      group_by(model_family) %>%
      filter(latency_ms > quantile(latency_ms, 0.95, na.rm = TRUE)) %>%
      ungroup(),
    aes(color = model_family),
    width = 0.12, size = 1.4, alpha = 0.55, show.legend = FALSE
  ) +
  # Median labels
  geom_label(
    data = medians,
    aes(y = med, label = sprintf("%.0f ms", med)),
    fill = DARK_BG, color = TEXT_CLR, size = 3.2,
    hjust = -0.1, vjust = 0.5, label.size = 0.2
  ) +
  scale_y_log10(
    labels = comma_format(suffix = " ms"),
    breaks = c(500, 1000, 2000, 5000, 10000, 30000, 60000)
  ) +
  scale_fill_manual (values = PALETTE, guide = "none") +
  scale_color_manual(values = PALETTE, guide = "none") +
  labs(
    title    = "Response Latency Distribution by Model",
    subtitle = "Log-scale Y axis · Boxplot + violin · Dots = top 5% outliers",
    x = NULL,
    y = "Latency (ms, log scale)"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major  = element_line(color = "#1E2A50", linewidth = 0.3),
    panel.grid.minor  = element_blank(),
    panel.border      = element_rect(fill = NA, color = "#00FFE022"),
    axis.text         = element_text(color = TEXT_CLR),
    axis.title        = element_text(color = TEXT_CLR),
    plot.title        = element_text(color = "#00FFE0", face = "bold", size = 15, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    plot.margin       = margin(16, 24, 16, 16)
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/12_latency_box.png", plot = p,
       width = 2400, height = 1600, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/12_latency_box.png")

# Interactive plotly violin
fig_ly <- plot_ly()
for (mdl in COMPLETE) {
  sub <- df_c %>% filter(model_family == mdl)
  fig_ly <- fig_ly %>%
    add_trace(
      type      = "violin",
      y         = sub$latency_ms,
      name      = mdl,
      box       = list(visible = TRUE),
      meanline  = list(visible = TRUE, color = "white"),
      points    = "outliers",
      marker    = list(color = PALETTE[mdl], size = 3, opacity = 0.5),
      line      = list(color = PALETTE[mdl]),
      fillcolor = paste0(substr(PALETTE[mdl], 1, 7), "55"),
      side      = "both"
    )
}

fig_ly <- fig_ly %>%
  layout(
    title   = list(text = "Latency by Model (log scale)",
                   font = list(color = "#00FFE0", size = 16)),
    yaxis   = list(type = "log", title = "Latency (ms)",
                   color = TEXT_CLR, tickfont = list(color = TEXT_CLR)),
    xaxis   = list(color = TEXT_CLR, tickfont = list(color = TEXT_CLR)),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font    = list(color = TEXT_CLR),
    legend  = list(font = list(color = TEXT_CLR))
  )

htmlwidgets::saveWidget(fig_ly, "interactive/12_latency_box.html", selfcontained = FALSE)
message("Saved: interactive/12_latency_box.html")
message("12_latency_box.R complete.\n")
