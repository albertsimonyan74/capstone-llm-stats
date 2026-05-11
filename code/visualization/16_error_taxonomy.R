## 16_error_taxonomy.R
## Error taxonomy: dark-theme visualizations.
## Run from: report_materials/r_analysis/

pkgs <- c("jsonlite", "ggplot2", "dplyr", "tidyr", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(jsonlite); library(ggplot2); library(dplyr); library(tidyr); library(scales)

DATA_PATH <- "../../data/error_taxonomy_results.json"
FIG_DIR   <- "figures"
if (!dir.exists(FIG_DIR)) dir.create(FIG_DIR, recursive = TRUE)

if (!file.exists(DATA_PATH)) {
  stop("data/error_taxonomy_results.json not found. Run: python scripts/analyze_errors.py")
}

data <- jsonlite::fromJSON(DATA_PATH)

DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"
ACCENT     <- "#00FFE0"

error_labels <- c(
  E1_NUMERICAL_COMPUTATION = "E1: Numerical Computation",
  E2_METHOD_SELECTION      = "E2: Method Selection",
  E3_ASSUMPTION_VIOLATION  = "E3: Assumption Violation",
  E4_FORMAT_FAILURE        = "E4: Format Failure",
  E5_OVERCONFIDENCE        = "E5: Overconfidence",
  E6_CONCEPTUAL_CONFUSION  = "E6: Conceptual Confusion",
  E7_TRUNCATION            = "E7: Truncation (Token Limit)",
  E8_HALLUCINATION         = "E8: Hallucination",
  E9_UNCLASSIFIED          = "E9: Unclassified"
)

# Error colors — distinct, readable on dark bg
ERR_COLORS <- c(
  E1_NUMERICAL_COMPUTATION = "#00CED1",
  E2_METHOD_SELECTION      = "#7FFFD4",
  E3_ASSUMPTION_VIOLATION  = "#FF6B6B",
  E4_FORMAT_FAILURE        = "#FFD700",
  E5_OVERCONFIDENCE        = "#A78BFA",
  E6_CONCEPTUAL_CONFUSION  = "#4A90D9",
  E7_TRUNCATION            = "#FF9A3C",
  E8_HALLUCINATION         = "#F06292",
  E9_UNCLASSIFIED          = "#78909C"
)

dark_theme_horiz <- theme_minimal(base_size = 12) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.x = element_line(color = "#1E2A50", linewidth = 0.35),
    panel.grid.major.y = element_blank(),
    panel.grid.minor   = element_blank(),
    axis.text          = element_text(color = TEXT_CLR, size = 11),
    axis.title         = element_text(color = TEXT_CLR),
    plot.title         = element_text(color = ACCENT, face = "bold", size = 14, hjust = 0.5),
    plot.subtitle      = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    legend.position    = "none",
    plot.margin        = margin(16, 20, 16, 16)
  )

# ── Figure 1: Error distribution ─────────────────────────────
# Build from full error_labels set (fills 0 for missing types like E8, E9)
data_dist <- data.frame(
  error_type = names(data$error_distribution),
  count      = as.integer(unlist(data$error_distribution)),
  stringsAsFactors = FALSE
)

error_df <- data.frame(
  error_type = names(error_labels),
  stringsAsFactors = FALSE
) %>%
  left_join(data_dist, by = "error_type") %>%
  mutate(
    count = ifelse(is.na(count), 0L, count),
    label = error_labels[error_type]
  ) %>%
  arrange(desc(count)) %>%
  mutate(
    label  = factor(label, levels = rev(label)),
    color  = ERR_COLORS[error_type],
    pct    = ifelse(sum(count) > 0, count / sum(count) * 100, 0)
  )

p1 <- ggplot(error_df, aes(x = count, y = label, fill = error_type)) +
  geom_col(width = 0.68, alpha = 0.92) +
  geom_text(aes(label = paste0(count, "  (", round(pct, 0), "%)")),
            hjust = -0.06, size = 3.4, fontface = "bold", color = TEXT_CLR) +
  scale_fill_manual(values = ERR_COLORS) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.22))) +
  labs(
    title    = "Error Taxonomy — All Models, All Failures",
    subtitle = paste0(data$total_failures, " failed runs / ",
                      data$total_benchmark_runs, " total  ·  ",
                      round(data$failure_rate * 100, 1), "% failure rate"),
    x = "Count", y = NULL
  ) +
  dark_theme_horiz

ggsave(file.path(FIG_DIR, "16a_error_distribution.png"), p1,
       width = 2200, height = 1100, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: 16a_error_distribution.png")

# ── Figure 2: Error × Model heatmap ──────────────────────────
model_errors_raw <- data$error_by_model
model_errors_df <- do.call(rbind, lapply(names(model_errors_raw), function(m) {
  errs <- model_errors_raw[[m]]
  data.frame(model_full = m, error = names(errs),
             count = as.integer(unlist(errs)), stringsAsFactors = FALSE)
}))

all_combos <- expand.grid(
  model_full = unique(model_errors_df$model_full),
  error      = names(error_labels), stringsAsFactors = FALSE
)
model_errors_df <- all_combos %>%
  left_join(model_errors_df, by = c("model_full", "error")) %>%
  mutate(
    count      = ifelse(is.na(count), 0L, count),
    short_lbl  = sub("^E[0-9]+: ", "", error_labels[error]),
    model_full = factor(model_full,
                        levels = c("claude","gemini","chatgpt","deepseek","mistral"),
                        labels = c("Claude","Gemini","ChatGPT","DeepSeek","Mistral"))
  )

p2 <- ggplot(model_errors_df, aes(x = short_lbl, y = model_full, fill = count)) +
  geom_tile(color = DARK_BG, linewidth = 0.8) +
  geom_text(aes(label = ifelse(count > 0, count, "—"),
                color = ifelse(count > 30, "black", TEXT_CLR)),
            size = 3.2, fontface = "bold") +
  scale_fill_gradient(low = DARK_PANEL, high = "#FF6B6B",
                      name = "Count", na.value = DARK_PANEL) +
  scale_color_identity() +
  labs(
    title = "Error Types by Model",
    subtitle = "Cell = number of failures in that category",
    x = NULL, y = NULL
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.background   = element_rect(fill = DARK_BG, color = NA),
    panel.background  = element_rect(fill = DARK_BG, color = NA),
    panel.grid        = element_blank(),
    axis.text.x       = element_text(angle = 35, hjust = 1, size = 9, color = TEXT_CLR),
    axis.text.y       = element_text(size = 11, color = TEXT_CLR, face = "bold"),
    plot.title        = element_text(color = ACCENT, face = "bold", size = 13, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text       = element_text(color = TEXT_CLR),
    legend.title      = element_text(color = ACCENT),
    plot.margin       = margin(16, 16, 16, 16)
  )

ggsave(file.path(FIG_DIR, "16b_error_by_model_heatmap.png"), p2,
       width = 2400, height = 900, units = "px", dpi = 180, bg = DARK_BG)
message("Saved: 16b_error_by_model_heatmap.png")

# ── Figure 3: Top tasks stacked by error ─────────────────────
task_errors_raw <- data$error_by_task_type
task_errors_df <- do.call(rbind, lapply(names(task_errors_raw), function(tt) {
  errs <- task_errors_raw[[tt]]
  data.frame(task_type = tt, error = names(errs),
             count = as.integer(unlist(errs)), stringsAsFactors = FALSE)
}))

top_tasks <- task_errors_df %>%
  group_by(task_type) %>%
  summarise(total = sum(count), .groups = "drop") %>%
  slice_max(total, n = 10) %>%
  pull(task_type)

task_errors_top <- task_errors_df %>%
  filter(task_type %in% top_tasks) %>%
  mutate(short_err = sub("^E[0-9]+: ", "", ifelse(
    error %in% names(error_labels), error_labels[error], error)))

p3 <- ggplot(task_errors_top,
             aes(x = reorder(task_type, count, sum), y = count, fill = error)) +
  geom_col(position = "stack", width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = ERR_COLORS,
                    labels = sub("^E[0-9]+: ", "", error_labels),
                    name = "Error Type") +
  labs(
    title    = "Top 10 Task Types by Failure Count",
    subtitle = "Stacked by error category",
    x = NULL, y = "Error Count"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.background  = element_rect(fill = DARK_BG,    color = NA),
    panel.background = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.x = element_line(color = "#1E2A50", linewidth = 0.35),
    panel.grid.major.y = element_blank(),
    panel.grid.minor   = element_blank(),
    axis.text          = element_text(color = TEXT_CLR, size = 10),
    axis.title         = element_text(color = TEXT_CLR),
    plot.title         = element_text(color = ACCENT, face = "bold", size = 13, hjust = 0.5),
    plot.subtitle      = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    legend.background  = element_rect(fill = DARK_BG, color = NA),
    legend.text        = element_text(color = TEXT_CLR, size = 9),
    legend.title       = element_text(color = ACCENT, face = "bold"),
    plot.margin        = margin(16, 16, 16, 16)
  )

ggsave(file.path(FIG_DIR, "16c_error_by_task_type.png"), p3,
       width = 2200, height = 1200, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: 16c_error_by_task_type.png")
message("\n16_error_taxonomy.R complete — 3 figures written to figures/")
