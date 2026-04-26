## 16_error_taxonomy.R
## Error taxonomy visualizations from analyze_errors.py output.
## Run from: report_materials/r_analysis/

pkgs <- c("jsonlite", "ggplot2", "dplyr", "tidyr", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(jsonlite)
library(ggplot2)
library(dplyr)
library(tidyr)
library(scales)

DATA_PATH <- "../../data/error_taxonomy_results.json"
FIG_DIR   <- "figures"
if (!dir.exists(FIG_DIR)) dir.create(FIG_DIR, recursive = TRUE)

if (!file.exists(DATA_PATH)) {
  stop("data/error_taxonomy_results.json not found. Run: python scripts/analyze_errors.py")
}

data <- jsonlite::fromJSON(DATA_PATH)

# ── Readable error labels ─────────────────────────────────────────────────────
error_labels <- c(
  E1_NUMERICAL_COMPUTATION = "E1: Numerical\nComputation",
  E2_METHOD_SELECTION      = "E2: Method\nSelection",
  E3_ASSUMPTION_VIOLATION  = "E3: Assumption\nViolation",
  E4_FORMAT_FAILURE        = "E4: Format\nFailure",
  E5_OVERCONFIDENCE        = "E5: Over-\nconfidence",
  E6_CONCEPTUAL_CONFUSION  = "E6: Conceptual\nConfusion",
  E7_TRUNCATION            = "E7: Truncation\n(Token Limit)",
  E8_HALLUCINATION         = "E8: Hallucination",
  E9_UNCLASSIFIED          = "E9: Unclassified"
)

# ── Figure 1: Error distribution bar chart ────────────────────────────────────
error_df <- data.frame(
  error_type = names(data$error_distribution),
  count      = as.integer(unlist(data$error_distribution))
) %>%
  mutate(
    label = ifelse(error_type %in% names(error_labels),
                   error_labels[error_type], error_type)
  ) %>%
  arrange(desc(count))

p1 <- ggplot(error_df, aes(x = reorder(label, count), y = count, fill = count)) +
  geom_col(width = 0.7, show.legend = FALSE) +
  geom_text(aes(label = count), hjust = -0.2, size = 3.5) +
  coord_flip() +
  scale_fill_gradient(low = "#92c5de", high = "#2166ac") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(
    title    = "Error Taxonomy Distribution (All Models, All Failures)",
    subtitle = paste0(data$total_failures, " failed runs / ", data$total_benchmark_runs,
                      " total (", round(data$failure_rate * 100, 1), "% failure rate)"),
    x = NULL, y = "Count"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title    = element_text(face = "bold", size = 13),
    axis.text.y   = element_text(size = 10),
    panel.grid.major.y = element_blank()
  )

ggsave(file.path(FIG_DIR, "16a_error_distribution.png"), p1,
       width = 10, height = 6, dpi = 150)
message("Saved: 16a_error_distribution.png")

# ── Figure 2: Error type × model heatmap ─────────────────────────────────────
model_errors_raw <- data$error_by_model
model_errors_df <- do.call(rbind, lapply(names(model_errors_raw), function(m) {
  errs <- model_errors_raw[[m]]
  data.frame(
    model      = toupper(substr(m, 1, 1)),
    model_full = m,
    error      = names(errs),
    count      = as.integer(unlist(errs)),
    stringsAsFactors = FALSE
  )
})) %>%
  mutate(
    label = ifelse(error %in% names(error_labels), error_labels[error], error)
  )

# Ensure all error × model combos present
all_combos <- expand.grid(
  model_full = unique(model_errors_df$model_full),
  error      = names(error_labels),
  stringsAsFactors = FALSE
)
model_errors_df <- all_combos %>%
  left_join(model_errors_df, by = c("model_full", "error")) %>%
  mutate(
    count = ifelse(is.na(count), 0L, count),
    label = ifelse(error %in% names(error_labels), error_labels[error], error),
    model_full = factor(model_full,
                        levels = c("claude", "gemini", "chatgpt", "deepseek", "mistral"),
                        labels = c("Claude", "Gemini", "ChatGPT", "DeepSeek", "Mistral"))
  )

p2 <- ggplot(model_errors_df, aes(x = label, y = model_full, fill = count)) +
  geom_tile(color = "white", linewidth = 0.6) +
  geom_text(aes(label = ifelse(count > 0, count, "")), size = 3) +
  scale_fill_gradient(low = "#f7f7f7", high = "#2166ac",
                      name = "Count", na.value = "white") +
  labs(
    title = "Error Types by Model",
    x = NULL, y = NULL
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title       = element_text(face = "bold", size = 13),
    axis.text.x      = element_text(angle = 35, hjust = 1, size = 9),
    axis.text.y      = element_text(size = 11),
    legend.position  = "right",
    panel.grid       = element_blank()
  )

ggsave(file.path(FIG_DIR, "16b_error_by_model_heatmap.png"), p2,
       width = 13, height = 5, dpi = 150)
message("Saved: 16b_error_by_model_heatmap.png")

# ── Figure 3: Top task types by failure, stacked by error category ────────────
task_errors_raw <- data$error_by_task_type
task_errors_df <- do.call(rbind, lapply(names(task_errors_raw), function(tt) {
  errs <- task_errors_raw[[tt]]
  data.frame(
    task_type  = tt,
    error      = names(errs),
    count      = as.integer(unlist(errs)),
    stringsAsFactors = FALSE
  )
}))

# Top 12 task types by total error count
top_tasks <- task_errors_df %>%
  group_by(task_type) %>%
  summarise(total = sum(count), .groups = "drop") %>%
  slice_max(total, n = 12) %>%
  pull(task_type)

task_errors_top <- task_errors_df %>%
  filter(task_type %in% top_tasks) %>%
  mutate(
    short_label = ifelse(error %in% names(error_labels),
                         sub("\n.*", "", error_labels[error]), error)
  )

# Color palette for error types
err_colors <- c(
  E1_NUMERICAL_COMPUTATION = "#4dac26",
  E2_METHOD_SELECTION      = "#d01c8b",
  E3_ASSUMPTION_VIOLATION  = "#f1a340",
  E4_FORMAT_FAILURE        = "#998ec3",
  E5_OVERCONFIDENCE        = "#f6e8c3",
  E6_CONCEPTUAL_CONFUSION  = "#92c5de",
  E7_TRUNCATION            = "#2166ac",
  E8_HALLUCINATION         = "#d73027",
  E9_UNCLASSIFIED          = "#aaaaaa"
)

p3 <- ggplot(task_errors_top,
             aes(x = reorder(task_type, count, sum), y = count, fill = error)) +
  geom_col(position = "stack", width = 0.75) +
  coord_flip() +
  scale_fill_manual(values = err_colors, labels = error_labels,
                    name = "Error Type") +
  labs(
    title    = "Failure Error Mix by Task Type (Top 12)",
    subtitle = "Stacked by error category; E7=Truncation, E3=Assumption Violation",
    x = NULL, y = "Error Count"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title  = element_text(face = "bold", size = 13),
    legend.text = element_text(size = 8),
    legend.key.size = unit(0.5, "cm")
  )

ggsave(file.path(FIG_DIR, "16c_error_by_task_type.png"), p3,
       width = 13, height = 7, dpi = 150)
message("Saved: 16c_error_by_task_type.png")

message("\n16_error_taxonomy.R complete — 3 figures written to figures/")
