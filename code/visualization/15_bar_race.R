## 15_bar_race.R
## Animated bar chart race: cumulative avg score per model, animated by task_type.
## Uses gganimate + gifski to export a GIF.
## Also exports final-frame static PNG.
## Outputs: figures/15_bar_race.gif  (800×500)
##          figures/15_bar_race.png  (final frame, 1600×1000)

pkgs <- c("dplyr", "ggplot2", "gganimate", "gifski", "scales")
for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE))
    install.packages(pkg, repos = "https://cloud.r-project.org")
}
suppressPackageStartupMessages({
  library(dplyr); library(ggplot2); library(gganimate)
  library(gifski); library(scales)
})

PALETTE <- c(chatgpt = "#10A37F", deepseek = "#4D9FFF",
             mistral = "#FF7043", claude   = "#CC785C")
DARK_BG    <- "#0A0F1E"
DARK_PANEL <- "#0D1426"
TEXT_CLR   <- "#E8F4F8"

if (!file.exists("data/benchmark_clean.rds")) stop("Run 00_load_data.R first.")
df <- readRDS("data/benchmark_clean.rds")

COMPLETE <- c("claude", "chatgpt", "deepseek", "gemini", "mistral")

# Pick a meaningful ordering of task types by avg difficulty/performance
df_c <- df %>%
  filter(model_family %in% COMPLETE) %>%
  mutate(model_family = factor(model_family, levels = COMPLETE))

# Task types ordered by tier, then by overall avg (ascending = bar race gets exciting)
tt_order <- df_c %>%
  group_by(task_type, tier) %>%
  summarise(overall = mean(final_score, na.rm = TRUE), .groups = "drop") %>%
  arrange(tier, overall) %>%
  pull(task_type)

# Cumulative average score as each task_type is revealed (alphabetical sweep)
# We simulate a "race": at step k, we include all tasks of task_types[1:k]
race_data <- lapply(seq_along(tt_order), function(k) {
  tt_subset <- tt_order[1:k]
  df_c %>%
    filter(task_type %in% tt_subset) %>%
    group_by(model_family) %>%
    summarise(
      cum_avg = mean(final_score, na.rm = TRUE),
      n_tasks = n(),
      .groups = "drop"
    ) %>%
    mutate(
      frame     = k,
      frame_lbl = tt_order[k]
    )
}) %>%
  dplyr::bind_rows()

# Within each frame, assign rank for label positioning
race_data <- race_data %>%
  group_by(frame) %>%
  mutate(rank = rank(-cum_avg, ties.method = "first")) %>%
  ungroup()

p_race <- ggplot(race_data,
                 aes(x = reorder(model_family, -cum_avg),
                     y = cum_avg, fill = model_family)) +
  geom_col(width = 0.72, alpha = 0.9, color = NA) +
  geom_text(
    aes(label = sprintf("%.3f", cum_avg)),
    hjust = -0.1, size = 4.5, color = TEXT_CLR, fontface = "bold"
  ) +
  geom_hline(yintercept = 0.5, linetype = "dashed",
             color = "#FFD700", linewidth = 0.7, alpha = 0.8) +
  coord_flip(clip = "off") +
  scale_fill_manual(values = PALETTE, guide = "none") +
  scale_y_continuous(limits = c(0, 1.12), labels = percent_format(1)) +
  labs(
    title    = "Cumulative Avg Score Race",
    subtitle = "Task type added: {closest_state}",
    x = NULL, y = "Cumulative Average Score"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "#1E2A50", linewidth = 0.3),
    panel.grid.minor  = element_blank(),
    axis.text         = element_text(color = TEXT_CLR, size = 12),
    axis.title        = element_text(color = TEXT_CLR, size = 11),
    plot.title        = element_text(color = "#00FFE0", face = "bold", size = 16, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 10, hjust = 0.5),
    plot.margin       = margin(16, 60, 16, 16)
  ) +
  transition_states(
    states            = frame_lbl,
    transition_length = 1,
    state_length      = 2,
    wrap              = FALSE
  ) +
  ease_aes("cubic-in-out") +
  enter_grow() +
  exit_shrink()

dir.create("figures", showWarnings = FALSE)

# Render GIF
anim <- animate(
  p_race,
  nframes  = length(tt_order) * 3,
  fps      = 8,
  width    = 800,
  height   = 500,
  renderer = gifski_renderer(),
  bg       = DARK_BG
)
anim_save("figures/15_bar_race.gif", animation = anim)
message("Saved: figures/15_bar_race.gif")

# Final frame static PNG — last task_type included
final_frame_data <- race_data %>% filter(frame == max(frame))
p_final <- ggplot(final_frame_data,
                  aes(x = reorder(model_family, -cum_avg),
                      y = cum_avg, fill = model_family)) +
  geom_col(width = 0.72, alpha = 0.9, color = NA) +
  geom_text(
    aes(label = sprintf("%.3f", cum_avg)),
    hjust = -0.1, size = 5, color = TEXT_CLR, fontface = "bold"
  ) +
  geom_hline(yintercept = 0.5, linetype = "dashed",
             color = "#FFD700", linewidth = 0.7, alpha = 0.8) +
  coord_flip(clip = "off") +
  scale_fill_manual(values = PALETTE, guide = "none") +
  scale_y_continuous(limits = c(0, 1.12), labels = percent_format(1)) +
  labs(
    title    = "Final Cumulative Average Score (All Task Types)",
    subtitle = "Dashed line = pass threshold (0.50)",
    x = NULL, y = "Cumulative Average Score"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.background   = element_rect(fill = DARK_BG,    color = NA),
    panel.background  = element_rect(fill = DARK_PANEL, color = NA),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "#1E2A50", linewidth = 0.3),
    panel.grid.minor  = element_blank(),
    axis.text         = element_text(color = TEXT_CLR, size = 13),
    axis.title        = element_text(color = TEXT_CLR, size = 12),
    plot.title        = element_text(color = "#00FFE0", face = "bold", size = 16, hjust = 0.5),
    plot.subtitle     = element_text(color = "#8BAFC0", size = 9, hjust = 0.5),
    plot.margin       = margin(16, 60, 16, 16)
  )

ggsave("figures/15_bar_race.png", plot = p_final,
       width = 1600, height = 1000, units = "px", dpi = 200, bg = DARK_BG)
message("Saved: figures/15_bar_race.png")
message("15_bar_race.R complete.\n")
