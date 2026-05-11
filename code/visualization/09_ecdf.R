## 09_ecdf.R
## Cumulative Score Distribution (ECDF) — one line per model.
## Vertical reference lines at 0.5, 0.6, 0.8 with per-model pass-rate annotations.
## Outputs: figures/09_ecdf.png (2400×1600)
##          interactive/09_ecdf.html

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
  filter(model_family %in% COMPLETE) %>%
  mutate(model_family = factor(model_family, levels = COMPLETE))

# Per-model pass rates at three thresholds
THRESHOLDS <- c(0.5, 0.6, 0.8)
pass_rates <- df_c %>%
  group_by(model_family) %>%
  summarise(
    pass50 = mean(final_score >= 0.5, na.rm = TRUE),
    pass60 = mean(final_score >= 0.6, na.rm = TRUE),
    pass80 = mean(final_score >= 0.8, na.rm = TRUE),
    .groups = "drop"
  )

# ECDF per model (compute manually for fill-under-curve)
ecdf_data <- df_c %>%
  group_by(model_family) %>%
  arrange(final_score, .by_group = TRUE) %>%
  mutate(
    ecdf_y = seq_along(final_score) / n()
  ) %>%
  ungroup()

# Annotation data — place text just right of each threshold
annot <- pass_rates %>%
  tidyr::pivot_longer(c(pass50), names_to = "thr", values_to = "pass_rate") %>%
  mutate(
    x_pos   = 0.52,
    y_pos   = pass_rate,
    label   = sprintf("%s: %.0f%%", model_family, pass_rate * 100)
  )

VLINES <- data.frame(xint = THRESHOLDS,
                     lbl  = c("Pass 50%", "Pass 60%", "Pass 80%"))

p <- ggplot(ecdf_data, aes(x = final_score, color = model_family)) +
  # Fill area under ECDF
  geom_ribbon(
    aes(ymin = 0, ymax = ecdf_y, fill = model_family),
    alpha = 0.08, color = NA
  ) +
  # ECDF step lines
  geom_step(aes(y = ecdf_y), linewidth = 0.9, alpha = 0.9) +
  # Vertical reference lines
  geom_vline(data = VLINES, aes(xintercept = xint),
             linetype = "dashed", color = "#FFD700", linewidth = 0.55, alpha = 0.7,
             inherit.aes = FALSE) +
  geom_text(data = VLINES,
            aes(x = xint + 0.015, y = 0.07, label = lbl),
            color = "#FFD700", size = 2.8, hjust = 0, fontface = "italic",
            inherit.aes = FALSE) +
  scale_color_manual(values = PALETTE, name = "Model") +
  scale_fill_manual (values = PALETTE, guide = "none") +
  scale_x_continuous(limits = c(0, 1.02), breaks = seq(0, 1, 0.2),
                     labels = percent_format(1)) +
  scale_y_continuous(limits = c(0, 1.02), breaks = seq(0, 1, 0.25),
                     labels = percent_format(1)) +
  labs(
    title    = "Cumulative Score Distribution by Model (ECDF)",
    subtitle = "Each step = one task · Shading shows area under curve",
    x = "Final Score",
    y = "Cumulative Proportion of Tasks"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major  = element_line(color = "#1E2A50", linewidth = 0.3),
    panel.grid.minor  = element_blank(),
    panel.border      = element_rect(fill = NA, color = "#00FFE022"),
    axis.text         = element_text(color = TEXT_CLR, size = 10),
    axis.title        = element_text(color = TEXT_CLR, size = 11),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text       = element_text(color = TEXT_CLR),
    legend.title      = element_text(color = "#00FFE0", face = "bold"),
    plot.title        = element_text(color = "#00FFE0", face = "bold", size = 15, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    plot.margin       = margin(16, 24, 16, 16)
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/09_ecdf.png", plot = p,
       width = 2400, height = 1600, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/09_ecdf.png")

p_ly <- ggplotly(p, tooltip = c("x", "y", "colour")) %>%
  layout(
    paper_bgcolor = DARK_BG, plot_bgcolor = DARK_PANEL,
    font = list(color = TEXT_CLR),
    legend = list(font = list(color = TEXT_CLR))
  )
htmlwidgets::saveWidget(p_ly, "interactive/09_ecdf.html", selfcontained = FALSE)
message("Saved: interactive/09_ecdf.html")
message("09_ecdf.R complete.\n")
