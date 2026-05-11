## 11_correlation.R
## Two correlation matrices:
##   (A) Model × Model — pairwise Pearson on per-task scores
##   (B) Task-type × Task-type — avg scores wide matrix
## Outputs: figures/11_correlation.png (3200×1600)
##          interactive/11_correlation.html  (B matrix only, heatmap)

pkgs <- c("dplyr", "ggplot2", "plotly", "htmlwidgets", "scales",
          "tidyr", "patchwork")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(plotly)
  library(htmlwidgets); library(scales); library(tidyr); library(patchwork)
})

PALETTE <- c(chatgpt = "#10A37F", deepseek = "#4D9FFF",
             mistral = "#FF7043", claude   = "#CC785C")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")
df_c <- df %>% filter(model_family %in% COMPLETE)

# ── (A) Model × Model correlation ─────────────────────────────────────────────
wide_model <- df_c %>%
  select(task_id, model_family, final_score) %>%
  pivot_wider(names_from = model_family, values_from = final_score)

cor_mat_m <- cor(wide_model[, COMPLETE], use = "pairwise.complete.obs")

cor_long_m <- as.data.frame(as.table(cor_mat_m)) %>%
  rename(x = Var1, y = Var2, corr = Freq) %>%
  mutate(
    x = factor(x, levels = COMPLETE),
    y = factor(y, levels = rev(COMPLETE)),
    label = sprintf("%.2f", corr)
  )

p_model <- ggplot(cor_long_m, aes(x, y, fill = corr)) +
  geom_tile(color = DARK_BG, linewidth = 0.6) +
  geom_text(aes(label = label), size = 4.5, color = "white", fontface = "bold") +
  scale_fill_gradient2(
    low = "#FF4757", mid = "#0D1426", high = "#00FFE0",
    midpoint = 0, limits = c(-1, 1), name = "r",
    guide = guide_colorbar(barheight = 8, barwidth = 0.8)
  ) +
  coord_fixed() +
  labs(title = "Model × Model Score Correlation",
       subtitle = "Pairwise Pearson on per-task final scores",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 11) +
  theme(
    plot.background  = element_rect(fill = DARK_BG, color = NA),
    panel.background = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid       = element_blank(),
    axis.text        = element_text(color = TEXT_CLR, size = 10),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text      = element_text(color = TEXT_CLR, size = 8),
    legend.title     = element_text(color = "#00FFE0", face = "bold", size = 9),
    plot.title       = element_text(color = "#00FFE0", face = "bold", size = 13, hjust = 0.5),
    plot.subtitle    = element_text(color = "#8BAFC0", size = 8.5, hjust = 0.5),
    plot.margin      = margin(12, 8, 12, 12)
  )

# ── (B) Task-type × Task-type correlation ─────────────────────────────────────
# Avg score per (task_type, model) → wide → correlate task_types
avg_tt <- df_c %>%
  group_by(task_type, model_family) %>%
  summarise(avg = mean(final_score, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(names_from = task_type, values_from = avg)

cor_mat_tt <- cor(avg_tt[, -1], use = "pairwise.complete.obs")

# Order task types by hierarchical clustering for readable plot
ord <- tryCatch(
  order.dendrogram(as.dendrogram(hclust(dist(cor_mat_tt)))),
  error = function(e) seq_len(nrow(cor_mat_tt))
)
tt_levels <- rownames(cor_mat_tt)[ord]

cor_long_tt <- as.data.frame(as.table(cor_mat_tt)) %>%
  rename(x = Var1, y = Var2, corr = Freq) %>%
  mutate(
    x = factor(x, levels = tt_levels),
    y = factor(y, levels = rev(tt_levels))
  )

p_tt <- ggplot(cor_long_tt, aes(x, y, fill = corr)) +
  geom_tile(color = DARK_BG, linewidth = 0.25) +
  scale_fill_gradient2(
    low = "#FF4757", mid = "#0D1426", high = "#00FFE0",
    midpoint = 0, limits = c(-1, 1), name = "r",
    guide = guide_colorbar(barheight = 8, barwidth = 0.8)
  ) +
  coord_fixed() +
  labs(title = "Task-Type × Task-Type Score Correlation",
       subtitle = "Avg model score per task type · Hierarchical order",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 9) +
  theme(
    plot.background  = element_rect(fill = DARK_BG, color = NA),
    panel.background = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid       = element_blank(),
    axis.text.x      = element_text(color = TEXT_CLR, angle = 45, hjust = 1, size = 7),
    axis.text.y      = element_text(color = TEXT_CLR, size = 7),
    legend.background = element_rect(fill = DARK_BG, color = NA),
    legend.text      = element_text(color = TEXT_CLR, size = 7),
    legend.title     = element_text(color = "#00FFE0", face = "bold", size = 8),
    plot.title       = element_text(color = "#00FFE0", face = "bold", size = 12, hjust = 0.5),
    plot.subtitle    = element_text(color = "#8BAFC0", size = 8, hjust = 0.5),
    plot.margin      = margin(12, 12, 12, 8)
  )

# ── Patchwork combine ─────────────────────────────────────────────────────────
p_combined <- p_model + p_tt +
  plot_annotation(
    theme = theme(plot.background = element_rect(fill = DARK_BG, color = NA))
  )

dir.create("figures",     showWarnings = FALSE)
dir.create("interactive", showWarnings = FALSE)

ggsave("figures/11_correlation.png", plot = p_combined,
       width = 3200, height = 1600, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/11_correlation.png")

# Interactive: task-type heatmap via plotly
fig_ly <- plot_ly(
  z         = cor_mat_tt[ord, ord],
  x         = tt_levels,
  y         = tt_levels,
  type      = "heatmap",
  colorscale = list(c(0,"#FF4757"), c(0.5,"#0D1426"), c(1,"#00FFE0")),
  zmin = -1, zmax = 1,
  colorbar = list(title = "r",
                  tickfont = list(color = TEXT_CLR),
                  titlefont = list(color = "#00FFE0")),
  hovertemplate = "%{x} × %{y}<br>r = %{z:.3f}<extra></extra>"
) %>%
  layout(
    title  = list(text = "Task-Type Correlation Matrix",
                  font = list(color = "#00FFE0", size = 15)),
    xaxis  = list(tickfont = list(color = TEXT_CLR, size = 9), tickangle = 45),
    yaxis  = list(tickfont = list(color = TEXT_CLR, size = 9)),
    paper_bgcolor = DARK_BG,
    plot_bgcolor  = DARK_PANEL,
    font   = list(color = TEXT_CLR)
  )

htmlwidgets::saveWidget(fig_ly, "interactive/11_correlation.html", selfcontained = FALSE)
message("Saved: interactive/11_correlation.html")
message("11_correlation.R complete.\n")
