## 14_difficulty.R
## Difficulty × Model: grouped bar chart (pass rate) + interactive heatmap.
## More informative than line chart — shows pass/fail counts per cell.
## Outputs: figures/14_difficulty.png (2400×1400)
##          interactive/14_difficulty.html

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales", "tidyr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales); library(tidyr)
})

PALETTE <- c(
  claude   = "#00CED1",
  chatgpt  = "#7FFFD4",
  mistral  = "#A78BFA",
  deepseek = "#4A90D9",
  gemini   = "#FF6B6B"
)
MODEL_LABELS <- c(claude = "Claude", chatgpt = "ChatGPT", mistral = "Mistral",
                  deepseek = "DeepSeek", gemini = "Gemini")
DIFF_COLORS  <- c(basic = "#00FFE0", intermediate = "#FFD700", advanced = "#FF6B6B")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"
ACCENT     <- "#00FFE0"
COMPLETE   <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
DIFF_ORD   <- c("basic", "intermediate", "advanced")

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

df_c <- df %>%
  filter(model_family %in% COMPLETE) %>%
  mutate(
    model_family = factor(model_family, levels = COMPLETE),
    difficulty   = factor(difficulty,   levels = DIFF_ORD)
  )

# Aggregate: pass rate + counts per model × difficulty
diff_agg <- df_c %>%
  group_by(model_family, difficulty) %>%
  summarise(
    n_total  = n(),
    n_pass   = sum(pass, na.rm = TRUE),
    pass_pct = mean(pass, na.rm = TRUE),
    avg_score = mean(final_score, na.rm = TRUE),
    .groups  = "drop"
  ) %>%
  mutate(
    label    = MODEL_LABELS[as.character(model_family)],
    bar_lbl  = paste0(round(pass_pct * 100), "%\n",
                      n_pass, "/", n_total)
  )

# ── Static grouped bar chart ─────────────────────────────────
dark_theme_bar <- theme_minimal(base_size = 12) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.y = element_line(color = "#1E2A50", linewidth = 0.35),
    panel.grid.major.x = element_blank(),
    panel.grid.minor   = element_blank(),
    axis.text          = element_text(color = TEXT_CLR, size = 11),
    axis.title         = element_text(color = TEXT_CLR, size = 11),
    plot.title         = element_text(color = ACCENT, face = "bold",
                                       size = 15, hjust = 0.5),
    plot.subtitle      = element_text(color = "#8BAFC0", size = 9,
                                       hjust = 0.5),
    legend.position    = "top",
    legend.background  = element_rect(fill = DARK_BG, color = NA),
    legend.text        = element_text(color = TEXT_CLR, size = 11),
    legend.title       = element_text(color = ACCENT, size = 10,
                                       face = "bold"),
    plot.margin        = margin(16, 24, 16, 16)
  )

p <- ggplot(diff_agg,
            aes(x = label, y = pass_pct, fill = difficulty)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.68,
           alpha = 0.9, color = NA) +
  geom_text(
    aes(label = paste0(round(pass_pct * 100), "%")),
    position = position_dodge(width = 0.75),
    vjust = -0.5, size = 3.1, fontface = "bold", color = TEXT_CLR
  ) +
  geom_hline(yintercept = 0.5, linetype = "dashed",
             color = ACCENT, linewidth = 0.65, alpha = 0.7) +
  annotate("text", x = 0.4, y = 0.515,
           label = "Pass threshold (50%)",
           color = ACCENT, size = 2.8, hjust = 0, fontface = "italic") +
  scale_fill_manual(
    values = DIFF_COLORS,
    labels = c(basic = "Basic", intermediate = "Intermediate",
               advanced = "Advanced"),
    name   = "Difficulty"
  ) +
  scale_y_continuous(limits = c(0, 1.08),
                     labels = percent_format(accuracy = 1),
                     breaks = seq(0, 1, 0.2)) +
  labs(
    title    = "Pass Rate by Difficulty & Model",
    subtitle = paste0("Grouped bars · each group = one model · ",
                      "dashed = 50% pass threshold"),
    x = NULL, y = "Pass Rate"
  ) +
  dark_theme_bar

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/14_difficulty.png", plot = p,
       width = 2400, height = 1300, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/14_difficulty.png")

# ── Interactive plotly heatmap ────────────────────────────────
heat_wide <- diff_agg %>%
  mutate(
    cell_text = paste0(round(pass_pct * 100), "%<br>",
                       n_pass, " / ", n_total, " tasks"),
    model_lab = label
  )

# Order: models on x, difficulty on y (advanced on top)
model_order <- MODEL_LABELS[COMPLETE]
diff_order  <- rev(DIFF_ORD)

heat_mat <- heat_wide %>%
  mutate(
    model_lab = factor(model_lab, levels = model_order),
    diff_lab  = factor(as.character(difficulty),
                       levels = diff_order,
                       labels = c("Advanced", "Intermediate", "Basic"))
  )

fig_ly <- plot_ly(
  heat_mat,
  x    = ~model_lab,
  y    = ~diff_lab,
  z    = ~pass_pct,
  type = "heatmap",
  colorscale = list(
    list(0,   "#1A0A2E"),
    list(0.3, "#0D3B6E"),
    list(0.6, "#00897B"),
    list(1.0, "#00FFE0")
  ),
  zmin = 0, zmax = 1,
  text = ~cell_text,
  hovertemplate = paste0(
    "<b>%{x}</b> · %{y}<br>",
    "Pass rate: %{z:.0%}<br>",
    "%{text}<extra></extra>"
  ),
  colorbar = list(
    title      = list(text = "Pass Rate", font = list(color = ACCENT)),
    tickformat = ".0%",
    tickfont   = list(color = TEXT_CLR),
    bgcolor    = DARK_BG,
    bordercolor = "rgba(0,255,224,0.2)"
  )
) %>%
  add_annotations(
    x    = ~model_lab,
    y    = ~diff_lab,
    text = ~paste0("<b>", round(pass_pct * 100), "%</b><br><span style='font-size:10px'>",
                   n_pass, "/", n_total, "</span>"),
    xref = "x", yref = "y",
    showarrow = FALSE,
    font = list(color = TEXT_CLR, size = 13)
  ) %>%
  layout(
    title  = list(text = "Pass Rate by Difficulty & Model",
                  font = list(color = ACCENT, size = 17)),
    xaxis  = list(title = "", color = TEXT_CLR,
                  tickfont = list(color = TEXT_CLR, size = 13)),
    yaxis  = list(title = "", color = TEXT_CLR,
                  tickfont = list(color = TEXT_CLR, size = 13)),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR),
    margin = list(l = 100, r = 80, t = 70, b = 60)
  )

htmlwidgets::saveWidget(fig_ly, "interactive/14_difficulty.html",
                        selfcontained = FALSE)
message("Saved: interactive/14_difficulty.html")
message("14_difficulty.R complete.\n")
