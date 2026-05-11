## run_all.R
## Master runner: sources all 00–16 scripts in order.
## NOTE: 16_error_taxonomy.R requires data/error_taxonomy_results.json.
## Run `python scripts/analyze_errors.py` from project root before running this.
## Creates data/ and figures/ dirs if needed.
## Wraps each script in tryCatch; prints progress and final manifest.
## Run from: report_materials/r_analysis/

cat("\n")
cat("╔══════════════════════════════════════════════════════════════╗\n")
cat("║   LLM Benchmark — R Analysis Suite Runner                   ║\n")
cat("║   DS 299 Capstone                                            ║\n")
cat("╚══════════════════════════════════════════════════════════════╝\n\n")

start_time <- proc.time()

# ── Create required directories ───────────────────────────────────────────────
for (d in c("data", "figures", "interactive")) {
  if (!dir.exists(d)) {
    dir.create(d, recursive = TRUE)
    message("Created directory: ", d)
  }
}

# ── Script registry ───────────────────────────────────────────────────────────
scripts <- list(
  list(
    file    = "00_load_data.R",
    label   = "00 — Load & clean data",
    outputs = c("data/benchmark_clean.rds", "data/benchmark_clean.csv")
  ),
  list(
    file    = "01_model_heatmap.R",
    label   = "01 — Model × task heatmap",
    outputs = c("figures/01_model_heatmap.png", "figures/01_model_heatmap.html")
  ),
  list(
    file    = "02_tier_radar.R",
    label   = "02 — Tier radar + bar chart",
    outputs = c("figures/02_tier_radar.html", "figures/02_tier_radar_bar.png")
  ),
  list(
    file    = "03_distributions.R",
    label   = "03 — Score distributions (ridges)",
    outputs = c("figures/03_distributions.png", "figures/03_distributions.html")
  ),
  list(
    file    = "04_difficulty_scatter.R",
    label   = "04 — Difficulty scatter (faceted)",
    outputs = c("figures/04_difficulty_scatter.png", "figures/04_difficulty_scatter.html")
  ),
  list(
    file    = "05_failure_analysis.R",
    label   = "05 — Failure analysis (patchwork)",
    outputs = c("figures/05_failure_analysis.png", "figures/05_failure_analysis.html")
  ),
  list(
    file    = "06_gt_table.R",
    label   = "06 — Publication gt table",
    outputs = c("figures/06_model_table.html")
  ),
  list(
    file    = "07_latency_accuracy.R",
    label   = "07 — Latency vs accuracy scatter",
    outputs = c("figures/07_latency_accuracy.png", "figures/07_latency_accuracy.html")
  ),
  list(
    file    = "08_grouped_bar.R",
    label   = "08 — Grouped bar chart (tier facets)",
    outputs = c("figures/08_grouped_bar.png", "interactive/08_grouped_bar.html")
  ),
  list(
    file    = "09_ecdf.R",
    label   = "09 — Cumulative score distribution (ECDF)",
    outputs = c("figures/09_ecdf.png", "interactive/09_ecdf.html")
  ),
  list(
    file    = "10_treemap.R",
    label   = "10 — Task coverage treemap",
    outputs = c("figures/10_treemap.png", "interactive/10_treemap.html")
  ),
  list(
    file    = "11_correlation.R",
    label   = "11 — Correlation matrices (model + task-type)",
    outputs = c("figures/11_correlation.png", "interactive/11_correlation.html")
  ),
  list(
    file    = "12_latency_box.R",
    label   = "12 — Latency violin + boxplot (log scale)",
    outputs = c("figures/12_latency_box.png", "interactive/12_latency_box.html")
  ),
  list(
    file    = "13_pass_rate.R",
    label   = "13 — Pass-rate heatmap (tier × model)",
    outputs = c("figures/13_pass_rate.png", "interactive/13_pass_rate.html")
  ),
  list(
    file    = "14_difficulty.R",
    label   = "14 — Difficulty progression line chart",
    outputs = c("figures/14_difficulty.png", "interactive/14_difficulty.html")
  ),
  list(
    file    = "15_bar_race.R",
    label   = "15 — Animated bar chart race (GIF + PNG)",
    outputs = c("figures/15_bar_race.gif", "figures/15_bar_race.png")
  ),
  list(
    file    = "16_error_taxonomy.R",
    label   = "16 — Error taxonomy visualizations (E1-E9)",
    outputs = c("figures/16a_error_distribution.png",
                "figures/16b_error_by_model_heatmap.png",
                "figures/16c_error_by_task_type.png")
  )
)

# ── Rmd rendering (separate step, optional) ───────────────────────────────────
rmd_info <- list(
  file   = "08_master_report.Rmd",
  label  = "08 — Master HTML report (Rmd)",
  output = "benchmark_report.html"
)

# ── Run each script ───────────────────────────────────────────────────────────
results   <- list()
n_scripts <- length(scripts)

for (i in seq_along(scripts)) {
  s <- scripts[[i]]
  cat(sprintf("\n[%d/%d] Running: %s\n", i, n_scripts, s$label))
  cat(sprintf("       File: %s\n", s$file))

  t0 <- proc.time()
  ok <- tryCatch({
    withCallingHandlers(
      source(s$file, local = FALSE),
      warning = function(w) {
        cat(sprintf("  WARNING in %s:\n    %s\n", s$file, conditionMessage(w)))
        invokeRestart("muffleWarning")
      }
    )
    TRUE
  }, error = function(e) {
    cat(sprintf("  ERROR in %s:\n    %s\n", s$file, conditionMessage(e)))
    FALSE
  })

  elapsed <- (proc.time() - t0)[["elapsed"]]
  status  <- if (isTRUE(ok)) "OK" else "FAILED"
  cat(sprintf("       Status: %s  (%.1fs)\n", status, elapsed))

  results[[s$file]] <- list(
    label   = s$label,
    status  = status,
    time_s  = round(elapsed, 1),
    outputs = s$outputs
  )
}

# ── Render Rmd (optional — requires rmarkdown + pandoc) ──────────────────────
cat(sprintf("\n[%d/%d] Rendering: %s\n", n_scripts + 1L, n_scripts + 1L, rmd_info$label))
tryCatch({
  if (!requireNamespace("rmarkdown", quietly = TRUE)) {
    install.packages("rmarkdown", repos = "https://cloud.r-project.org")
  }
  if (!rmarkdown::pandoc_available()) {
    cat("  WARNING: pandoc not found — skipping Rmd render.\n")
    cat("  Install pandoc (https://pandoc.org) then run:\n")
    cat("    rmarkdown::render('08_master_report.Rmd', output_file='benchmark_report.html')\n")
    results[[rmd_info$file]] <- list(
      label   = rmd_info$label,
      status  = "SKIPPED (no pandoc)",
      time_s  = 0,
      outputs = rmd_info$output
    )
  } else {
    t0 <- proc.time()
    rmarkdown::render(
      input       = rmd_info$file,
      output_file = rmd_info$output,
      quiet       = FALSE,
      envir       = new.env(parent = globalenv())
    )
    elapsed <- (proc.time() - t0)[["elapsed"]]
    cat(sprintf("       Status: OK  (%.1fs)\n", elapsed))
    results[[rmd_info$file]] <- list(
      label   = rmd_info$label,
      status  = "OK",
      time_s  = round(elapsed, 1),
      outputs = rmd_info$output
    )
  }
}, error = function(e) {
  cat(sprintf("  ERROR rendering Rmd:\n    %s\n", conditionMessage(e)))
  results[[rmd_info$file]] <<- list(
    label   = rmd_info$label,
    status  = "FAILED",
    time_s  = 0,
    outputs = rmd_info$output
  )
})

# ── Final manifest ─────────────────────────────────────────────────────────────
total_elapsed <- (proc.time() - start_time)[["elapsed"]]

cat("\n")
cat("══════════════════════════════════════════════════════════════\n")
cat("  OUTPUT MANIFEST\n")
cat("══════════════════════════════════════════════════════════════\n")

all_outputs <- character(0)
for (nm in names(results)) {
  r <- results[[nm]]
  status_icon <- if (r$status == "OK") "✓" else if (grepl("SKIP", r$status)) "~" else "✗"
  cat(sprintf("\n  %s  %s  [%s, %.1fs]\n", status_icon, r$label, r$status, r$time_s))
  outs <- unlist(r$outputs)
  for (out in outs) {
    exists_mark <- if (file.exists(out)) "  " else "  (missing)"
    sz <- tryCatch({
      fs <- file.info(out)$size
      if (is.na(fs)) "" else sprintf(" (%.1f KB)", fs / 1024)
    }, error = function(e) "")
    cat(sprintf("       → %s%s%s\n", out, sz, exists_mark))
    all_outputs <- c(all_outputs, out)
  }
}

cat("\n")
cat("══════════════════════════════════════════════════════════════\n")
n_ok      <- sum(sapply(results, function(r) r$status == "OK"))
n_total_s <- length(results)
cat(sprintf("  Scripts: %d/%d succeeded\n", n_ok, n_total_s))
cat(sprintf("  Files:   %d/%d exist\n",
            sum(file.exists(all_outputs)), length(all_outputs)))
cat(sprintf("  Total time: %.1f seconds (%.1f minutes)\n",
            total_elapsed, total_elapsed / 60))
cat("══════════════════════════════════════════════════════════════\n\n")

invisible(results)
