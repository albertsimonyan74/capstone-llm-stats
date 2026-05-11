## 08_grouped_bar.R
## Grouped bar chart with ±1 SD error bars, faceted by tier.
## One bar per (model × task_type), sorted by avg score within each tier.
## Outputs: figures/08_grouped_bar.png (4000×2000)
##          interactive/08_grouped_bar.html

# ── Packages ───────────────────────────────────────────────────────────────────
pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales", "forcats", "tidyr")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales); library(forcats); library(tidyr)
})

# ── Palette ────────────────────────────────────────────────────────────────────
PALETTE <- c(chatgpt = "#10A37F", deepseek = "#4D9FFF",
             mistral = "#FF7043", claude   = "#CC785C")
TIER_COLORS <- c("1" = "#00FFE0", "2" = "#00BFFF", "3" = "#9B59B6", "4" = "#FF4757")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"
PASS_THR   <- 0.5

# ── Load data ──────────────────────────────────────────────────────────────────
if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
df_c <- df %>% filter(model_family %in% COMPLETE)

# ── Summarize: mean ± sd per (model, tier, task_type) ─────────────────────────
task_summary <- df_c %>%
  group_by(model_family, tier, task_type) %>%
  summarise(
    mean_score = mean(final_score, na.rm = TRUE),
    sd_score   = sd(final_score,   na.rm = TRUE),
    n          = n(),
    .groups    = "drop"
  ) %>%
  mutate(
    sd_score  = replace_na(sd_score, 0),
    ymin      = pmax(0, mean_score - sd_score),
    ymax      = pmin(1, mean_score + sd_score),
    tier_lab  = paste0("Tier ", tier),
    model_family = factor(model_family, levels = COMPLETE)
  )

# Sort task_types within each tier by avg score (desc)
tier_order <- task_summary %>%
  group_by(tier, task_type) %>%
  summarise(overall = mean(mean_score), .groups = "drop") %>%
  arrange(tier, desc(overall))

# Build ordered factor
task_summary <- task_summary %>%
  mutate(task_type = factor(task_type, levels = rev(unique(tier_order$task_type))))

# ── Plot ───────────────────────────────────────────────────────────────────────
p <- ggplot(task_summary,
            aes(x = task_type, y = mean_score,
                fill = model_family, group = model_family)) +
  geom_col(position = position_dodge(0.8), width = 0.72, alpha = 0.88) +
  geom_errorbar(aes(ymin = ymin, ymax = ymax),
                position = position_dodge(0.8), width = 0.28,
                color = "white", alpha = 0.65, linewidth = 0.4) +
  geom_hline(yintercept = PASS_THR, linetype = "dashed",
             color = "#FFD700", linewidth = 0.6, alpha = 0.8) +
  facet_wrap(~tier_lab, scales = "free_x", ncol = 2,
             labeller = labeller(tier_lab = function(x) x)) +
  scale_fill_manual(values = PALETTE, name = "Model") +
  scale_y_continuous(limits = c(0, 1.05), labels = percent_format(1),
                     breaks = seq(0, 1, 0.25)) +
  coord_flip() +
  labs(
    title    = "Model Performance by Task Type and Difficulty Tier",
    subtitle = "Bars = mean score ±1 SD · Dashed line = pass threshold (0.50)",
    x = NULL, y = "Average Score"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.background  = element_rect(fill = DARK_BG,    color = NA),
    panel.background = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major = element_line(color = "#FFFFFF0D", linewidth = 0.3),
    panel.grid.minor = element_blank(),
    panel.border     = element_rect(fill = NA, color = "#00FFE022"),
    strip.background = element_rect(fill = "#0D1426", color = "#00FFE033"),
    strip.text       = element_text(color = "#00FFE0", face = "bold", size = 10),
    axis.text        = element_text(color = TEXT_CLR, size = 8),
    axis.title       = element_text(color = TEXT_CLR, size = 9),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text      = element_text(color = TEXT_CLR),
    legend.title     = element_text(color = "#00FFE0", face = "bold"),
    plot.title       = element_text(color = "#00FFE0", face = "bold", size = 14, hjust = 0.5),
    plot.subtitle    = element_text(color = "#8BAFC0", size = 9,  hjust = 0.5),
    plot.margin      = margin(16, 16, 16, 16)
  )

# ── Save ───────────────────────────────────────────────────────────────────────
dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/08_grouped_bar.png", plot = p,
       width = 20, height = 10, dpi = 200, bg = DARK_BG)
message("Saved: figures/08_grouped_bar.png")

p_ly <- ggplotly(p, tooltip = c("x", "y", "fill")) %>%
  layout(
    paper_bgcolor = DARK_BG, plot_bgcolor = DARK_PANEL,
    font = list(color = TEXT_CLR),
    legend = list(font = list(color = TEXT_CLR))
  )
htmlwidgets::saveWidget(p_ly, "interactive/08_grouped_bar.html",
                        selfcontained = FALSE)
message("Saved: interactive/08_grouped_bar.html")
message("08_grouped_bar.R complete.\n")
