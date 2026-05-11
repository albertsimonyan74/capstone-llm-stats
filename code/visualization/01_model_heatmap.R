## 01_model_heatmap.R
## Heatmap: task types × models, fill = avg score.
## Exports PNG (2400×1800) and interactive plotly HTML.

# ── Packages ──────────────────────────────────────────────────────────────────
pkgs <- c("dplyr", "ggplot2", "viridis", "plotly", "htmlwidgets", "tibble",
          "forcats", "scales", "tidyr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(dplyr)
library(ggplot2)
library(viridis)
library(plotly)
library(htmlwidgets)
library(tibble)
library(forcats)
library(scales)
library(tidyr)

# ── Color palette (consistent across all scripts) ────────────────────────────
PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)

DARK_BG   <- "#0A0F1E"
DARK_PANEL <- "#12193A"
TEXT_CLR  <- "#E8F4F8"
ACCENT    <- "#00FFE0"

TIER_COLORS <- c("1" = "#00FFE0", "2" = "#7FFFD4", "3" = "#A78BFA", "4" = "#FF6B6B")

# ── Load data ─────────────────────────────────────────────────────────────────
RDS_PATH <- "data/benchmark_clean.rds"
if (!file.exists(RDS_PATH)) {
  message("RDS not found — running 00_load_data.R first...")
  source("00_load_data.R")
}
df <- readRDS(RDS_PATH)

# All 5 models complete as of 2026-04-26
df_complete <- df %>% filter(!is.na(model_family))

# ── Build heatmap data ────────────────────────────────────────────────────────
hm_data <- df_complete %>%
  group_by(task_type, model_family) %>%
  summarise(avg_score = mean(final_score, na.rm = TRUE), .groups = "drop")

# Task-type ordering: hardest (lowest avg) at bottom
task_order <- hm_data %>%
  group_by(task_type) %>%
  summarise(overall = mean(avg_score, na.rm = TRUE), .groups = "drop") %>%
  arrange(overall) %>%
  pull(task_type)

# Tier per task_type (take mode from df)
tier_map <- df_complete %>%
  group_by(task_type) %>%
  summarise(tier = as.character(round(median(tier, na.rm = TRUE))), .groups = "drop")

hm_data <- hm_data %>%
  mutate(
    task_type    = factor(task_type, levels = task_order),
    model_family = factor(model_family, levels = c("claude", "chatgpt", "mistral", "deepseek", "gemini")),
    label        = sprintf("%.2f", avg_score)
  ) %>%
  left_join(tier_map, by = "task_type")

# ── ggplot2 heatmap ───────────────────────────────────────────────────────────
dark_theme <- theme_minimal(base_size = 11) +
  theme(
    plot.background  = element_rect(fill = DARK_BG,    color = NA),
    panel.background = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid       = element_blank(),
    axis.text        = element_text(color = TEXT_CLR),
    axis.title       = element_text(color = TEXT_CLR),
    plot.title       = element_text(color = ACCENT, size = 16, face = "bold", hjust = 0.5),
    plot.subtitle    = element_text(color = TEXT_CLR, size = 10, hjust = 0.5),
    plot.caption     = element_text(color = TEXT_CLR, size = 8),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text      = element_text(color = TEXT_CLR),
    legend.title     = element_text(color = TEXT_CLR),
    strip.text       = element_text(color = ACCENT)
  )

p_hm <- ggplot(hm_data, aes(x = model_family, y = task_type, fill = avg_score)) +
  geom_tile(color = DARK_BG, linewidth = 0.4) +
  geom_text(aes(label = label), color = "white", size = 2.8, fontface = "bold") +
  scale_fill_viridis(
    option = "plasma", name = "Avg Score",
    limits = c(0, 1), breaks = seq(0, 1, 0.2),
    labels = scales::number_format(accuracy = 0.1)
  ) +
  # Left tier color strip
  geom_tile(
    data = hm_data %>% distinct(task_type, tier),
    aes(x = -0.65, y = task_type, fill = NULL),
    width = 0.25, height = 1,
    color = NA
  ) +
  # We add a separate geom with tier fill using a second scale trick via annotation
  labs(
    title    = "LLM Performance on Bayesian Reasoning Tasks",
    subtitle = "Average score per task type × model  |  All 5 models complete (2026-04-26)",
    x        = "Model",
    y        = "Task Type  (sorted: hardest → easiest)",
    caption  = "n = 5 models × 171 tasks each. Pass threshold ≥ 0.5."
  ) +
  dark_theme +
  theme(
    axis.text.x = element_text(angle = 30, hjust = 1, size = 10, color = TEXT_CLR),
    axis.text.y = element_text(size = 7.5, color = TEXT_CLR),
    legend.position = "right",
    plot.margin = margin(10, 15, 10, 10)
  )

# Add tier strip on left as colored rectangles via annotation
tier_strip_data <- hm_data %>%
  distinct(task_type, tier) %>%
  mutate(
    y_pos = as.integer(factor(task_type, levels = task_order)),
    color = TIER_COLORS[tier]
  )

for (i in seq_len(nrow(tier_strip_data))) {
  p_hm <- p_hm + annotate(
    "rect",
    xmin = 0.35, xmax = 0.5,
    ymin = tier_strip_data$y_pos[i] - 0.48,
    ymax = tier_strip_data$y_pos[i] + 0.48,
    fill = tier_strip_data$color[i],
    alpha = 0.9
  )
}

# ── Save PNG ──────────────────────────────────────────────────────────────────
if (!dir.exists("figures")) dir.create("figures", recursive = TRUE)

png_path <- "figures/01_model_heatmap.png"
ggsave(png_path, p_hm, width = 2400, height = 1800, units = "px", dpi = 200)
message("Saved: ", png_path)

# ── Interactive plotly ────────────────────────────────────────────────────────
# Build a cleaner plotly version for interactivity
hm_wide <- hm_data %>%
  select(task_type, model_family, avg_score) %>%
  tidyr::pivot_wider(names_from = model_family, values_from = avg_score)

models_ordered <- c("claude", "chatgpt", "mistral", "deepseek", "gemini")
z_mat  <- as.matrix(hm_wide[, models_ordered])
rownames(z_mat) <- as.character(hm_wide$task_type)

# Text matrix
text_mat <- matrix(
  sprintf("Task: %s\nModel: %s\nAvg Score: %.3f",
          rep(rownames(z_mat), each = ncol(z_mat)),
          rep(colnames(z_mat), times = nrow(z_mat)),
          as.vector(t(z_mat))),
  nrow = nrow(z_mat), ncol = ncol(z_mat), byrow = TRUE
)

p_plotly <- plot_ly(
  z         = z_mat,
  x         = models_ordered,
  y         = rownames(z_mat),
  type      = "heatmap",
  colorscale = "Plasma",
  zmin      = 0, zmax = 1,
  text      = text_mat,
  hoverinfo = "text"
) %>%
  add_annotations(
    x    = rep(seq_along(models_ordered) - 1, times = nrow(z_mat)),
    y    = rep(seq_len(nrow(z_mat)) - 1, each = length(models_ordered)),
    text = sprintf("%.2f", as.vector(t(z_mat))),
    showarrow = FALSE,
    font = list(color = "white", size = 9)
  ) %>%
  layout(
    title  = list(text = "LLM Performance on Bayesian Reasoning Tasks",
                  font = list(color = ACCENT, size = 18)),
    xaxis  = list(title = "Model", tickfont = list(color = TEXT_CLR),
                  color = TEXT_CLR),
    yaxis  = list(title = "Task Type", tickfont = list(color = TEXT_CLR, size = 9),
                  color = TEXT_CLR),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    margin = list(l = 130, b = 80)
  )

html_path <- "figures/01_model_heatmap.html"
htmlwidgets::saveWidget(p_plotly, file = html_path, selfcontained = FALSE)
message("Saved: ", html_path)
message("01_model_heatmap.R complete.\n")
