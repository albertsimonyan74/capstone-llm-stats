## 04_difficulty_scatter.R
## Scatter: tier (jittered) × score, faceted by model, colored by task type.
## Exports PNG and interactive plotly HTML.

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales", "ggrepel", "tidyr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(dplyr)
library(ggplot2)
library(plotly)
library(htmlwidgets)
library(scales)
library(tidyr)

# ── Palette & theme ───────────────────────────────────────────────────────────
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

dark_theme <- theme_minimal(base_size = 11) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major  = element_line(color = "#1E2A50"),
    panel.grid.minor  = element_blank(),
    axis.text         = element_text(color = TEXT_CLR),
    axis.title        = element_text(color = TEXT_CLR),
    plot.title        = element_text(color = ACCENT, size = 15, face = "bold", hjust = 0.5),
    plot.subtitle     = element_text(color = TEXT_CLR, size = 9,  hjust = 0.5),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text       = element_text(color = TEXT_CLR, size = 7),
    legend.title      = element_text(color = TEXT_CLR, size = 8),
    strip.text        = element_text(color = ACCENT, size = 11, face = "bold"),
    strip.background  = element_rect(fill = "#12193A", color = NA),
    plot.caption      = element_text(color = TEXT_CLR, size = 7),
    panel.border      = element_rect(color = "#1E2A50", fill = NA, linewidth = 0.4)
  )

# ── Load data ─────────────────────────────────────────────────────────────────
RDS_PATH <- "data/benchmark_clean.rds"
if (!file.exists(RDS_PATH)) { source("00_load_data.R") }
df <- readRDS(RDS_PATH)

df_complete <- df %>%
  filter(!is.na(model_family)) %>%
  mutate(
    model_family = factor(model_family,
                          levels = c("claude", "chatgpt", "mistral", "deepseek"),
                          labels = c("Claude", "ChatGPT", "Mistral", "DeepSeek"))
  )

# 31 task types → distinct colors from rainbow
task_types  <- sort(unique(df_complete$task_type))
n_types     <- length(task_types)
task_colors <- setNames(
  grDevices::rainbow(n_types, s = 0.85, v = 0.9),
  task_types
)

set.seed(42)

# ── ggplot2 scatter ───────────────────────────────────────────────────────────
p_scatter <- ggplot(
  df_complete,
  aes(
    x     = jitter(tier, amount = 0.15),
    y     = final_score,
    color = task_type,
    text  = paste0("Task: ", task_id,
                   "\nType: ", task_type,
                   "\nTier: ", tier,
                   "\nScore: ", round(final_score, 3))
  )
) +
  geom_point(alpha = 0.65, size = 1.4) +
  geom_smooth(
    aes(x = tier, y = final_score, group = 1),
    method = "loess", formula = y ~ x,
    color = ACCENT, linewidth = 1.1, se = TRUE,
    fill  = "#00FFE033", alpha = 0.25, inherit.aes = FALSE
  ) +
  geom_hline(yintercept = 0.5, linetype = "dashed",
             color = "white", linewidth = 0.5, alpha = 0.5) +
  scale_color_manual(values = task_colors, name = "Task Type") +
  scale_x_continuous(breaks = 1:4, labels = paste("Tier", 1:4)) +
  scale_y_continuous(limits = c(-0.05, 1.05), breaks = seq(0, 1, 0.25),
                     labels = number_format(accuracy = 0.01)) +
  facet_wrap(~model_family, nrow = 1) +
  labs(
    title    = "Score vs. Tier by Model and Task Type",
    subtitle = "Jitter ±0.15  |  LOESS trend with 95% CI  |  Dashed = pass threshold",
    x        = "Tier",
    y        = "Final Score",
    caption  = "n = 136 tasks per model. Each point = one task run."
  ) +
  guides(color = guide_legend(ncol = 2, override.aes = list(size = 2.5, alpha = 0.9))) +
  dark_theme +
  theme(legend.position = "bottom",
        legend.key.size  = unit(0.5, "lines"))

if (!dir.exists("figures")) dir.create("figures", recursive = TRUE)

png_path <- "figures/04_difficulty_scatter.png"
ggsave(png_path, p_scatter,
       width = 2200, height = 1100, units = "px", dpi = 150)
message("Saved: ", png_path)

# ── Interactive plotly (faceted via subplot) ───────────────────────────────────
models_levels <- c("Claude", "ChatGPT", "Mistral", "DeepSeek")
model_keys    <- c("claude", "chatgpt", "mistral", "deepseek")

subplot_list <- lapply(seq_along(model_keys), function(i) {
  mdl <- model_keys[i]
  sub <- df_complete %>% filter(model_family == models_levels[i])

  plot_ly(sub,
    x     = ~jitter(tier, amount = 0.15),
    y     = ~final_score,
    color = ~task_type,
    colors = task_colors,
    type  = "scatter",
    mode  = "markers",
    marker = list(size = 6, opacity = 0.7),
    text  = ~paste0("Task: ", task_id,
                    "<br>Type: ", task_type,
                    "<br>Tier: ", tier,
                    "<br>Score: ", round(final_score, 3)),
    hoverinfo = "text",
    showlegend = (i == 1),
    name  = ~task_type
  ) %>%
    add_annotations(
      text      = models_levels[i],
      x         = 0.5, y = 1.03,
      xref      = "paper", yref = "paper",
      showarrow = FALSE,
      font      = list(color = ACCENT, size = 13, face = "bold")
    ) %>%
    add_lines(
      data = sub %>%
        group_by(tier) %>%
        summarise(avg = mean(final_score, na.rm = TRUE), .groups = "drop") %>%
        arrange(tier),
      x = ~tier, y = ~avg,
      line = list(color = ACCENT, width = 2, dash = "dot"),
      showlegend = FALSE, inherit = FALSE,
      name = "Avg trend"
    ) %>%
    layout(
      xaxis = list(title = if (i == 2) "Tier" else "",
                   tickvals = 1:4, ticktext = paste("T", 1:4),
                   color = TEXT_CLR, range = c(0.5, 4.5)),
      yaxis = list(title = if (i == 1) "Final Score" else "",
                   range = c(-0.05, 1.05), color = TEXT_CLR)
    )
})

fig_sub <- subplot(subplot_list, nrows = 1, shareY = TRUE, shareX = FALSE,
                   titleX = TRUE, titleY = TRUE) %>%
  layout(
    title  = list(text = "Score vs. Tier by Model & Task Type",
                  font = list(color = ACCENT, size = 17)),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    legend = list(font = list(color = TEXT_CLR, size = 9), x = 1.02, y = 0.5)
  )

html_path <- "figures/04_difficulty_scatter.html"
htmlwidgets::saveWidget(fig_sub, file = html_path, selfcontained = FALSE)
message("Saved: ", html_path)
message("04_difficulty_scatter.R complete.\n")
