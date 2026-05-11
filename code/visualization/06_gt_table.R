## 06_gt_table.R
## Publication-ready gt table: model × summary stats.
## Exports HTML (and attempts PNG via webshot2).

pkgs <- c("dplyr", "gt", "scales", "tibble", "tidyr", "stringr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
library(dplyr)
library(gt)
library(scales)
library(tibble)
library(tidyr)
library(stringr)

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
DARK_BG  <- "#0A0F1E"
TEXT_CLR <- "#E8F4F8"
ACCENT   <- "#00FFE0"

# ── Load data ─────────────────────────────────────────────────────────────────
RDS_PATH <- "data/benchmark_clean.rds"
if (!file.exists(RDS_PATH)) { source("00_load_data.R") }
df <- readRDS(RDS_PATH)

df_complete <- df %>% filter(!is.na(model_family))

# ── Build per-tier scores ─────────────────────────────────────────────────────
tier_scores <- df_complete %>%
  group_by(model_family, tier) %>%
  summarise(avg = round(mean(final_score, na.rm = TRUE), 3), .groups = "drop") %>%
  pivot_wider(names_from = tier, values_from = avg,
              names_prefix = "tier_") %>%
  rename_with(~ paste0("Tier ", sub("tier_", "", .x)), starts_with("tier_"))

# ── Best/worst task types per model ──────────────────────────────────────────
best_worst <- df_complete %>%
  group_by(model_family, task_type) %>%
  summarise(avg = mean(final_score, na.rm = TRUE), .groups = "drop") %>%
  group_by(model_family) %>%
  summarise(
    best_task  = task_type[which.max(avg)],
    worst_task = task_type[which.min(avg)],
    .groups = "drop"
  )

# ── Overall summary ───────────────────────────────────────────────────────────
overall <- df_complete %>%
  group_by(model_family) %>%
  summarise(
    overall_score = round(mean(final_score, na.rm = TRUE), 3),
    pass_rate     = round(mean(pass, na.rm = TRUE), 3),
    avg_latency   = round(mean(latency_ms, na.rm = TRUE), 0),
    .groups = "drop"
  )

# ── Combine ───────────────────────────────────────────────────────────────────
table_data <- overall %>%
  left_join(tier_scores, by = "model_family") %>%
  left_join(best_worst,  by = "model_family") %>%
  mutate(
    Model       = stringr::str_to_title(model_family),
    pass_rate_f = scales::percent(pass_rate, accuracy = 0.1)
  ) %>%
  select(
    Model,
    `Overall Score` = overall_score,
    `Tier 1`, `Tier 2`, `Tier 3`, `Tier 4`,
    `Pass Rate`   = pass_rate_f,
    `Avg Latency (ms)` = avg_latency,
    `Best Task`   = best_task,
    `Worst Task`  = worst_task
  ) %>%
  arrange(desc(`Overall Score`))

# ── Numeric cols for coloring ─────────────────────────────────────────────────
score_cols <- c("Overall Score", "Tier 1", "Tier 2", "Tier 3", "Tier 4")

# Find best value per numeric col to bold
col_maxes <- sapply(score_cols, function(col) max(table_data[[col]], na.rm = TRUE))

# ── gt table ──────────────────────────────────────────────────────────────────
# Color scale helper: white → green
score_color <- function(x) {
  # NA → gray; otherwise interpolate
  ifelse(is.na(x), "#333344",
         scales::col_numeric(
           palette = c("#1A0A2E", "#16213E", "#0D4F3C", "#1DBF73", "#7FFFD4"),
           domain  = c(0, 1)
         )(x))
}

gt_tbl <- table_data %>%
  gt(rowname_col = "Model") %>%
  tab_header(
    title    = md("**LLM Benchmark — Model Comparison**"),
    subtitle = "Bayesian Statistical Reasoning  ·  DS 299 Capstone"
  ) %>%
  tab_spanner(
    label   = "Score by Tier",
    columns = c(`Tier 1`, `Tier 2`, `Tier 3`, `Tier 4`)
  ) %>%
  tab_spanner(
    label   = "Overall",
    columns = c(`Overall Score`, `Pass Rate`)
  ) %>%
  tab_spanner(
    label   = "Performance",
    columns = c(`Avg Latency (ms)`, `Best Task`, `Worst Task`)
  ) %>%
  # Color score cells
  data_color(
    columns = all_of(score_cols),
    target_columns = all_of(score_cols),
    fn = score_color
  ) %>%
  # Bold best value in each score column
  tab_style(
    style  = cell_text(weight = "bold", color = "#00FFE0"),
    locations = cells_body(
      columns = `Overall Score`,
      rows    = `Overall Score` == col_maxes["Overall Score"]
    )
  ) %>%
  tab_style(
    style  = cell_text(weight = "bold", color = "#00FFE0"),
    locations = cells_body(
      columns = `Tier 1`,
      rows    = `Tier 1` == col_maxes["Tier 1"]
    )
  ) %>%
  tab_style(
    style  = cell_text(weight = "bold", color = "#00FFE0"),
    locations = cells_body(
      columns = `Tier 2`,
      rows    = `Tier 2` == col_maxes["Tier 2"]
    )
  ) %>%
  tab_style(
    style  = cell_text(weight = "bold", color = "#00FFE0"),
    locations = cells_body(
      columns = `Tier 3`,
      rows    = `Tier 3` == col_maxes["Tier 3"]
    )
  ) %>%
  tab_style(
    style  = cell_text(weight = "bold", color = "#00FFE0"),
    locations = cells_body(
      columns = `Tier 4`,
      rows    = `Tier 4` == col_maxes["Tier 4"]
    )
  ) %>%
  # Column formatting
  fmt_number(columns = `Avg Latency (ms)`, decimals = 0, use_seps = TRUE) %>%
  fmt_number(columns = all_of(score_cols), decimals = 3) %>%
  # Model color stub
  tab_style(
    style = list(
      cell_fill(color = "#1A0F3A"),
      cell_text(color = ACCENT, weight = "bold")
    ),
    locations = cells_stub(rows = everything())
  ) %>%
  # Header styling
  tab_style(
    style = list(
      cell_fill(color = "#0D1535"),
      cell_text(color = ACCENT, weight = "bold")
    ),
    locations = cells_column_labels()
  ) %>%
  tab_style(
    style = list(
      cell_fill(color = "#0D1535"),
      cell_text(color = ACCENT, weight = "bold", size = px(16))
    ),
    locations = cells_title(groups = "title")
  ) %>%
  tab_style(
    style = list(
      cell_fill(color = "#0D1535"),
      cell_text(color = TEXT_CLR, size = px(12))
    ),
    locations = cells_title(groups = "subtitle")
  ) %>%
  tab_style(
    style = list(
      cell_fill(color = "#0D1535"),
      cell_text(color = ACCENT, weight = "bold")
    ),
    locations = cells_column_spanners()
  ) %>%
  # Row background alternating
  tab_style(
    style = cell_fill(color = "#12193A"),
    locations = cells_body(rows = seq(1, nrow(table_data), 2))
  ) %>%
  tab_style(
    style = cell_fill(color = "#0A0F1E"),
    locations = cells_body(rows = seq(2, nrow(table_data), 2))
  ) %>%
  tab_style(
    style = cell_text(color = TEXT_CLR),
    locations = cells_body()
  ) %>%
  tab_source_note(
    source_note = md(
      "**n = 136 tasks per model.** Pass threshold ≥ 0.5. Gemini excluded (76/136 tasks — daily quota exhausted). \
       Scores: N=0.60, M=0.20, A=0.20. Tier 1 = simplest, Tier 4 = hardest."
    )
  ) %>%
  tab_style(
    style = list(
      cell_fill(color = "#0D1535"),
      cell_text(color = "#8899BB", size = px(10))
    ),
    locations = cells_source_notes()
  ) %>%
  opt_table_font(font = list(google_font("IBM Plex Mono"), default_fonts())) %>%
  opt_table_lines(extent = "none") %>%
  tab_options(
    table.background.color         = DARK_BG,
    table_body.border.top.color    = "#1E2A50",
    table_body.border.bottom.color = "#1E2A50",
    table_body.hlines.color        = "#1E2A50",
    stub.border.color              = "#1E2A50",
    column_labels.border.top.color = "#1E2A50",
    column_labels.border.bottom.color = ACCENT,
    heading.border.bottom.color    = ACCENT,
    source_notes.border.lr.color   = "#1E2A50"
  )

if (!dir.exists("figures")) dir.create("figures", recursive = TRUE)

html_path <- "figures/06_model_table.html"
gtsave(gt_tbl, html_path)
message("Saved: ", html_path)

# Try PNG via webshot2
tryCatch({
  if (!requireNamespace("webshot2", quietly = TRUE)) {
    message("webshot2 not available — skipping PNG export for gt table.")
  } else {
    library(webshot2)
    png_path <- "figures/06_model_table.png"
    gtsave(gt_tbl, png_path)
    message("Saved: ", png_path)
  }
}, error = function(e) {
  message("webshot2 PNG export failed (non-fatal): ", conditionMessage(e))
})

message("06_gt_table.R complete.\n")
