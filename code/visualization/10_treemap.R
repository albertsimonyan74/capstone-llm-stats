## 10_treemap.R
## Nested treemap: outer rectangles = tier, inner = task_type.
## Fill = average final_score (diverging palette, 0.5 midpoint).
## Outputs: figures/10_treemap.png (3200×2000)
##          interactive/10_treemap.html

pkgs <- c("dplyr", "ggplot2", "treemapify", "plotly", "htmlwidgets", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(treemapify)
  library(plotly); library(htmlwidgets); library(scales)
})

DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"
TIER_COLORS <- c("1" = "#00FFE0", "2" = "#00BFFF", "3" = "#9B59B6", "4" = "#FF4757")

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
df_c <- df %>% filter(model_family %in% COMPLETE)

# Summarise: n tasks + avg score per (tier, task_type)
task_tree <- df_c %>%
  group_by(tier, task_type) %>%
  summarise(
    avg_score = mean(final_score, na.rm = TRUE),
    n_obs     = n(),
    .groups   = "drop"
  ) %>%
  mutate(
    tier_lab = paste0("Tier ", tier),
    n_tasks  = n_obs / length(COMPLETE)   # unique tasks (divided by model count)
  )

# Static ggplot treemap
p <- ggplot(task_tree,
            aes(area = n_tasks, fill = avg_score,
                label = task_type, subgroup = tier_lab)) +
  geom_treemap(color = DARK_BG, size = 1.5) +
  geom_treemap_subgroup_border(color = "#00FFE066", size = 3) +
  geom_treemap_subgroup_text(
    place = "topleft", grow = FALSE, reflow = TRUE,
    color = "#00FFE0", alpha = 0.9, fontface = "bold", size = 11,
    padding.x = unit(4, "pt"), padding.y = unit(4, "pt")
  ) +
  geom_treemap_text(
    color = "white", alpha = 0.85, size = 8, fontface = "plain",
    place = "centre", reflow = TRUE,
    padding.x = unit(2, "pt"), padding.y = unit(2, "pt")
  ) +
  scale_fill_gradient2(
    low      = "#FF4757",
    mid      = "#FFD700",
    high     = "#00FFE0",
    midpoint = 0.5,
    limits   = c(0, 1),
    name     = "Avg Score",
    labels   = percent_format(1)
  ) +
  labs(
    title    = "Task Coverage Treemap — Avg Score by Task Type",
    subtitle = "Area ∝ number of tasks · Colour = average model score · Grouped by tier"
  ) +
  theme(
    plot.background = element_rect(fill = DARK_BG, color = NA),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text  = element_text(color = TEXT_CLR),
    legend.title = element_text(color = "#00FFE0", face = "bold"),
    plot.title   = element_text(color = "#00FFE0", face = "bold", size = 14,
                                hjust = 0.5, margin = margin(b = 4)),
    plot.subtitle = element_text(color = "#8BAFC0", size = 9,
                                 hjust = 0.5, margin = margin(b = 8)),
    plot.margin  = margin(12, 12, 12, 12)
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/10_treemap.png", plot = p,
       width = 3200, height = 2000, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/10_treemap.png")

# Interactive: plotly treemap
fig_ly <- plot_ly(
  data   = task_tree,
  type   = "treemap",
  labels = ~task_type,
  parents = ~tier_lab,
  values  = ~n_tasks,
  customdata = ~avg_score,
  hovertemplate = paste0(
    "<b>%{label}</b><br>",
    "Tasks: %{value}<br>",
    "Avg score: %{customdata:.3f}<extra></extra>"
  ),
  marker = list(
    colors       = ~avg_score,
    colorscale   = list(c(0,"#FF4757"), c(0.5,"#FFD700"), c(1,"#00FFE0")),
    cmin = 0, cmax = 1,
    showscale    = TRUE,
    colorbar     = list(title = "Avg Score",
                        tickformat = ".0%",
                        tickfont = list(color = TEXT_CLR),
                        titlefont = list(color = "#00FFE0"))
  ),
  branchvalues = "total",
  textfont = list(color = "white")
) %>%
  layout(
    title       = list(text = "Task Coverage Treemap",
                       font = list(color = "#00FFE0", size = 16)),
    paper_bgcolor = DARK_BG,
    font        = list(color = TEXT_CLR)
  )

htmlwidgets::saveWidget(fig_ly, "interactive/10_treemap.html", selfcontained = FALSE)
message("Saved: interactive/10_treemap.html")
message("10_treemap.R complete.\n")
