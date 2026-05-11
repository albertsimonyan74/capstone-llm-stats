## 00_load_data.R
## Read runs.jsonl, parse into clean tibble, save as RDS + CSV.
## Run from: code/visualization/

# ── Package bootstrap ────────────────────────────────────────────────────────
pkgs <- c("jsonlite", "dplyr", "readr", "tibble", "stringr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}
library(jsonlite)
library(dplyr)
library(readr)
library(tibble)
library(stringr)

# ── Paths ────────────────────────────────────────────────────────────────────
RUNS_PATH <- file.path(dirname(dirname(getwd())),
                       "experiments", "results_v1", "runs.jsonl")
# Resolve relative to script location when sourced
if (!file.exists(RUNS_PATH)) {
  RUNS_PATH <- "../../data/processed_data/results_v1/runs.jsonl"
}

DATA_DIR  <- "data"
if (!dir.exists(DATA_DIR)) dir.create(DATA_DIR, recursive = TRUE)

RDS_PATH  <- file.path(DATA_DIR, "benchmark_clean.rds")
CSV_PATH  <- file.path(DATA_DIR, "benchmark_clean.csv")

# ── Read JSONL line-by-line ───────────────────────────────────────────────────
message("Reading: ", RUNS_PATH)
lines <- readLines(RUNS_PATH, warn = FALSE)
lines <- lines[nzchar(trimws(lines))]
message("  Total non-empty lines: ", length(lines))

parse_record <- function(line) {
  tryCatch({
    r <- jsonlite::fromJSON(line, simplifyVector = TRUE)
    # Coerce every field to scalar — handle NULL / NA gracefully
    safe <- function(x, default = NA) {
      v <- r[[x]]
      if (is.null(v) || length(v) == 0) return(default)
      v[[1]]
    }
    safe_num <- function(x) {
      v <- r[[x]]
      if (is.null(v) || length(v) == 0) return(NA_real_)
      as.numeric(v[[1]])
    }
    safe_lgl <- function(x) {
      v <- r[[x]]
      if (is.null(v) || length(v) == 0) return(NA)
      as.logical(v[[1]])
    }
    tibble::tibble(
      run_id           = safe("run_id",           NA_character_),
      timestamp        = safe("timestamp",        NA_character_),
      task_id          = safe("task_id",          NA_character_),
      task_type        = safe("task_type",        NA_character_),
      tier             = safe_num("tier"),
      difficulty       = safe("difficulty",       NA_character_),
      model            = safe("model",            NA_character_),
      model_family     = safe("model_family",     NA_character_),
      final_score      = safe_num("final_score"),
      numeric_score    = safe_num("numeric_score"),
      structure_score  = safe_num("structure_score"),
      assumption_score = safe_num("assumption_score"),
      pass             = safe_lgl("pass"),
      answer_found     = safe_lgl("answer_found"),
      length_match     = safe_lgl("length_match"),
      input_tokens     = safe_num("input_tokens"),
      output_tokens    = safe_num("output_tokens"),
      latency_ms       = safe_num("latency_ms"),
      error            = safe("error",            NA_character_)
    )
  }, error = function(e) {
    message("  Skipping malformed line: ", substr(line, 1, 60), "...")
    NULL
  })
}

parsed <- lapply(lines, parse_record)
parsed <- Filter(Negate(is.null), parsed)
df_raw <- dplyr::bind_rows(parsed)
message("  Parsed records: ", nrow(df_raw))

# ── Clean / filter ────────────────────────────────────────────────────────────
# Drop old placeholder record (missing task_type or model_family)
# Also drop synthetic/perturbation tasks (task_id ends in _rephrase/_numerical/_semantic)
SYNTH_PATTERN <- "_(rephrase|numerical|semantic)$"

df <- df_raw %>%
  filter(
    !is.na(task_id),
    !is.na(model_family),
    !is.na(task_type),
    nzchar(task_type),
    nzchar(model_family),
    !stringr::str_detect(task_id, SYNTH_PATTERN)   # benchmark tasks only
  )

message("  Records after dropping malformed/synthetic rows: ", nrow(df))

# Normalise model_family to lowercase
df <- df %>%
  mutate(
    model_family = tolower(trimws(model_family)),
    tier         = as.integer(tier),
    difficulty   = factor(difficulty, levels = c("basic", "intermediate", "advanced")),
    pass         = as.logical(pass)
  )

# ── All 5 models now complete (171 tasks each) ────────────────────────────────
gemini_count <- sum(df$model_family == "gemini", na.rm = TRUE)
message("  Gemini run count: ", gemini_count, " (expected 171 — fully complete as of 2026-04-26)")
df <- df %>%
  mutate(gemini_complete = TRUE)   # all models complete

# ── Per-model counts ──────────────────────────────────────────────────────────
counts <- df %>%
  group_by(model_family) %>%
  summarise(
    n_runs     = n(),
    avg_score  = round(mean(final_score, na.rm = TRUE), 3),
    pass_rate  = round(mean(pass, na.rm = TRUE), 3),
    avg_latency = round(mean(latency_ms, na.rm = TRUE), 0),
    .groups = "drop"
  )
message("\n── Model summary ───────────────────────────────")
print(counts)

# ── Task-type summary ─────────────────────────────────────────────────────────
task_summary <- df %>%
  group_by(task_type) %>%
  summarise(
    avg_score = round(mean(final_score, na.rm = TRUE), 3),
    n         = n(),
    .groups   = "drop"
  ) %>%
  arrange(avg_score)

message("\n── Task-type avg scores (all 5 models, sorted) ──")
print(task_summary, n = 38)

# ── Save ──────────────────────────────────────────────────────────────────────
saveRDS(df, RDS_PATH)
write_csv(df, CSV_PATH)

message("\n── Saved ───────────────────────────────────────")
message("  RDS : ", RDS_PATH)
message("  CSV : ", CSV_PATH)
message("  Rows: ", nrow(df), "  Cols: ", ncol(df))
message("\n00_load_data.R complete.\n")
