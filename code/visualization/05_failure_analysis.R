## 05_failure_analysis.R
## Panel A: fail rate by task type (horizontal bar, sorted worst→best).
## Panel B: avg score per model for 10 worst task types.
## Exports wide PNG (3200×1400) and HTML.

pkgs <- c("dplyr", "ggplot2", "patchwork", "plotly", "htmlwidgets",
          "scales", "forcats", "tidyr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(dplyr)
library(ggplot2)
library(patchwork)
library(plotly)
library(htmlwidgets)
library(scales)
library(forcats)
library(tidyr)

# ── Palette & theme ───────────────────────────────────────────────────────────
PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
TIER_COLORS <- c("1" = "#00FFE0", "2" = "#7FFFD4", "3" = "#A78BFA", "4" = "#FF6B6B")

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
    plot.title        = element_text(color = ACCENT, size = 14, face = "bold"),
    plot.subtitle     = element_text(color = TEXT_CLR, size = 9),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text       = element_text(color = TEXT_CLR, size = 9),
    legend.title      = element_text(color = TEXT_CLR, size = 9),
    plot.caption      = element_text(color = TEXT_CLR, size = 7)
  )

# ── Load data ─────────────────────────────────────────────────────────────────
RDS_PATH <- "data/benchmark_clean.rds"
if (!file.exists(RDS_PATH)) { source("00_load_data.R") }
df <- readRDS(RDS_PATH)

df_complete <- df %>% filter(!is.na(model_family))

# Tier per task_type
tier_map <- df_complete %>%
  group_by(task_type) %>%
  summarise(tier = as.character(round(median(tier, na.rm = TRUE))), .groups = "drop")

# ── Panel A: fail rate by task type ──────────────────────────────────────────
fail_data <- df_complete %>%
  group_by(task_type) %>%
  summarise(
    n_total = n(),
    n_fail  = sum(!pass, na.rm = TRUE),
    fail_rate = n_fail / n_total,
    .groups = "drop"
  ) %>%
  left_join(tier_map, by = "task_type") %>%
  arrange(desc(fail_rate)) %>%         # worst at top
  mutate(
    task_type = fct_reorder(task_type, -fail_rate),
    label     = paste0(n_fail, "/", n_total, " failed")
  )

pA <- ggplot(fail_data,
             aes(x = fail_rate, y = task_type, fill = tier)) +
  geom_col(width = 0.72, alpha = 0.90) +
  geom_text(aes(label = label), hjust = -0.07, size = 2.7,
            color = TEXT_CLR, fontface = "bold") +
  geom_vline(xintercept = 0.5, linetype = "dashed", color = ACCENT,
             linewidth = 0.7, alpha = 0.7) +
  scale_fill_manual(values = TIER_COLORS, name = "Tier") +
  scale_x_continuous(limits = c(0, 1.15),
                     labels = percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.25)) +
  labs(
    title    = "A  —  Failure Rate by Task Type",
    subtitle = "Sorted worst → best  |  Dashed = 50% fail rate",
    x        = "Fail Rate",
    y        = NULL
  ) +
  dark_theme +
  theme(axis.text.y = element_text(size = 8, color = TEXT_CLR),
        legend.position = "right")

# ── Panel B: avg score for 10 worst task types ───────────────────────────────
worst10 <- fail_data %>% slice_head(n = 10) %>% pull(task_type) %>% as.character()

worst_data <- df_complete %>%
  filter(task_type %in% worst10) %>%
  group_by(task_type, model_family) %>%
  summarise(avg_score = mean(final_score, na.rm = TRUE), .groups = "drop") %>%
  mutate(
    task_type    = factor(task_type, levels = worst10),
    model_family = factor(model_family, levels = c("claude", "chatgpt", "mistral", "deepseek", "gemini"))
  )

pB <- ggplot(worst_data,
             aes(x = task_type, y = avg_score, fill = model_family, group = model_family)) +
  geom_col(position = position_dodge(width = 0.78), width = 0.70, alpha = 0.92) +
  geom_hline(yintercept = 0.5, linetype = "dashed", color = ACCENT,
             linewidth = 0.7, alpha = 0.7) +
  scale_fill_manual(values = PALETTE, name = "Model") +
  scale_y_continuous(limits = c(0, 1),
                     labels = percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2)) +
  labs(
    title    = "B  —  Model Scores on 10 Worst-Performing Task Types",
    subtitle = "Grouped by model  |  Dashed = pass threshold",
    x        = NULL,
    y        = "Average Score"
  ) +
  dark_theme +
  theme(
    axis.text.x = element_text(angle = 40, hjust = 1, size = 8, color = TEXT_CLR),
    legend.position = "right"
  )

# ── Patchwork combine ─────────────────────────────────────────────────────────
combined <- pA + pB +
  plot_annotation(
    title   = "Failure Analysis — LLM Benchmark on Bayesian Statistics",
    caption = "n = 5 models × 171 tasks. All models complete (2026-04-26).",
    theme   = theme(
      plot.background = element_rect(fill = DARK_BG, color = NA),
      plot.title      = element_text(color = ACCENT, size = 16, face = "bold", hjust = 0.5),
      plot.caption    = element_text(color = TEXT_CLR, size = 8)
    )
  ) +
  plot_layout(widths = c(1, 1.3))

if (!dir.exists("figures")) dir.create("figures", recursive = TRUE)

png_path <- "figures/05_failure_analysis.png"
ggsave(png_path, combined, width = 3200, height = 1400, units = "px", dpi = 200)
message("Saved: ", png_path)

# ── Interactive plotly (two subplots) ─────────────────────────────────────────
# Panel A plotly
pA_plotly <- plot_ly(fail_data,
  x    = ~fail_rate,
  y    = ~task_type,
  type = "bar",
  orientation = "h",
  color = ~tier,
  colors = TIER_COLORS,
  text  = ~label,
  textposition = "outside",
  hoverinfo = "text",
  hovertext = ~paste0(task_type, "<br>Fail rate: ",
                      percent(fail_rate, accuracy = 0.1),
                      "<br>", label)
) %>%
  layout(
    title   = list(text = "A — Failure Rate by Task Type",
                   font = list(color = ACCENT, size = 13)),
    xaxis   = list(range = c(0, 1.15), tickformat = ".0%",
                   color = TEXT_CLR),
    yaxis   = list(color = TEXT_CLR, tickfont = list(size = 9)),
    barmode = "stack",
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font    = list(color = TEXT_CLR),
    shapes  = list(list(type = "line", x0 = 0.5, x1 = 0.5,
                        y0 = 0, y1 = 1, yref = "paper",
                        line = list(color = ACCENT, dash = "dash", width = 2)))
  )

# Panel B plotly
pB_plotly <- plot_ly(worst_data,
  x    = ~task_type,
  y    = ~avg_score,
  color = ~model_family,
  colors = PALETTE[c("claude","chatgpt","mistral","deepseek","gemini")],
  type = "bar",
  text = ~paste0("Model: ", model_family,
                 "<br>Task: ", task_type,
                 "<br>Avg Score: ", round(avg_score, 3)),
  hoverinfo = "text"
) %>%
  layout(
    title   = list(text = "B — Model Scores: 10 Worst Task Types",
                   font = list(color = ACCENT, size = 13)),
    xaxis   = list(color = TEXT_CLR, tickfont = list(size = 9),
                   tickangle = -35),
    yaxis   = list(range = c(0, 1), tickformat = ".0%",
                   color = TEXT_CLR),
    barmode = "group",
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font    = list(color = TEXT_CLR),
    shapes  = list(list(type = "line", x0 = 0, x1 = 1, xref = "paper",
                        y0 = 0.5, y1 = 0.5,
                        line = list(color = ACCENT, dash = "dash", width = 2)))
  )

fig_combined <- subplot(pA_plotly, pB_plotly, nrows = 1,
                        titleX = TRUE, titleY = TRUE,
                        shareX = FALSE, shareY = FALSE) %>%
  layout(
    title  = list(text = "Failure Analysis — LLM Benchmark",
                  font = list(color = ACCENT, size = 17)),
    paper_bgcolor = DARK_BG,
    font   = list(color = TEXT_CLR)
  )

html_path <- "figures/05_failure_analysis.html"
htmlwidgets::saveWidget(fig_combined, file = html_path, selfcontained = FALSE)
message("Saved: ", html_path)
message("05_failure_analysis.R complete.\n")
