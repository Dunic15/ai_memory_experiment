#!/usr/bin/env Rscript

# =============================================================================
# Mixed Design ANOVA Analysis for AI Memory Experiment
# =============================================================================
# Analysis 1: MCQ Accuracy - AI (6 conditions) vs Non-AI
# Analysis 2: AI Summary Accuracy - 2x3 Mixed Design (Structure x Timing)
# Analysis 3: False Lures Selected - 2x3 Mixed Design (Structure x Timing)
# =============================================================================

# Load required packages
packages <- c("readxl", "tidyverse", "ez", "emmeans", "afex", "effectsize", "ggplot2")
for (pkg in packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
  library(pkg, character.only = TRUE)
}

# Set working directory - use command line args or current directory
args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])
if (length(script_path) > 0) {
  root <- normalizePath(dirname(script_path), winslash = "/", mustWork = FALSE)
} else {
  root <- getwd()
}
setwd(root)

# Read the long format data
cat("\n============================================================\n")
cat("LOADING DATA\n")
cat("============================================================\n\n")

df <- read_excel("Analysis long finals-.xlsx")
cat("Data loaded successfully. Shape:", nrow(df), "rows x", ncol(df), "columns\n")
cat("Columns:", paste(names(df), collapse = ", "), "\n\n")

# Convert factors
df$participant_id <- as.factor(df$participant_id)
df$experiment_group <- as.factor(df$experiment_group)
df$structure <- as.factor(df$structure)
df$timing <- as.factor(df$timing)

# Convert numeric columns
df$mcq_accuracy <- as.numeric(df$mcq_accuracy)
df$ai_summary_accuracy <- as.numeric(df$ai_summary_accuracy)
df$false_lures_selected <- as.numeric(df$false_lures_selected)

# Create output directory
output_dir <- file.path(root, "anova_outputs")
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# =============================================================================
# ANALYSIS 1: MCQ Accuracy - AI vs Non-AI (One-way ANOVA)
# =============================================================================
cat("\n\n############################################################\n")
cat("ANALYSIS 1: MCQ ACCURACY - AI vs NON-AI\n")
cat("############################################################\n\n")

# Calculate mean MCQ accuracy per participant (averaged across articles)
mcq_by_participant <- df %>%
  group_by(participant_id, experiment_group) %>%
  summarise(
    mcq_accuracy = mean(mcq_accuracy, na.rm = TRUE),
    .groups = "drop"
  )

cat("Descriptive Statistics:\n")
mcq_desc <- mcq_by_participant %>%
  group_by(experiment_group) %>%
  summarise(
    n = n(),
    mean = mean(mcq_accuracy, na.rm = TRUE),
    sd = sd(mcq_accuracy, na.rm = TRUE),
    se = sd / sqrt(n),
    .groups = "drop"
  )
print(mcq_desc)

# Run t-test (equivalent to one-way ANOVA with 2 groups)
cat("\nIndependent Samples t-test:\n")
t_result <- t.test(mcq_accuracy ~ experiment_group, data = mcq_by_participant, var.equal = TRUE)
print(t_result)

# Effect size (Cohen's d)
ai_mcq <- mcq_by_participant$mcq_accuracy[mcq_by_participant$experiment_group == "AI"]
noai_mcq <- mcq_by_participant$mcq_accuracy[mcq_by_participant$experiment_group == "NoAI"]
cohens_d_mcq <- cohens_d(ai_mcq, noai_mcq)
cat("\nEffect Size (Cohen's d):\n")
print(cohens_d_mcq)

# Save MCQ plot
mcq_plot <- ggplot(mcq_desc, aes(x = experiment_group, y = mean, fill = experiment_group)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.6) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.2) +
  labs(title = "MCQ Accuracy: AI vs Non-AI",
       x = "Experiment Group", y = "MCQ Accuracy (Mean ± SE)") +
  theme_minimal() +
  theme(legend.position = "none") +
  scale_fill_brewer(palette = "Set2")
ggsave(file.path(output_dir, "mcq_accuracy_ai_vs_noai.png"), mcq_plot, width = 8, height = 6)

# =============================================================================
# ANALYSIS 2: AI Summary Accuracy - 2x3 Mixed Design ANOVA
# =============================================================================
cat("\n\n############################################################\n")
cat("ANALYSIS 2: AI SUMMARY ACCURACY - 2x3 MIXED DESIGN ANOVA\n")
cat("(Structure: between-subjects, Timing: within-subjects)\n")
cat("############################################################\n\n")

# Filter to AI group only (exclude control/NoAI)
df_ai <- df %>%
  filter(experiment_group == "AI" & structure != "control" & timing != "control")

# Ensure factors are properly coded
df_ai$structure <- factor(df_ai$structure, levels = c("integrated", "segmented"))
df_ai$timing <- factor(df_ai$timing, levels = c("pre_reading", "synchronous", "post_reading"))

cat("Data subset for AI conditions:\n")
cat("- Structure levels:", levels(df_ai$structure), "\n")
cat("- Timing levels:", levels(df_ai$timing), "\n")
cat("- N observations:", nrow(df_ai), "\n\n")

# Descriptive statistics
cat("Descriptive Statistics - AI Summary Accuracy:\n")
summary_desc <- df_ai %>%
  group_by(structure, timing) %>%
  summarise(
    n = n(),
    mean = mean(ai_summary_accuracy, na.rm = TRUE),
    sd = sd(ai_summary_accuracy, na.rm = TRUE),
    se = sd / sqrt(n),
    .groups = "drop"
  )
print(summary_desc)

cat("\n\nMarginal Means - Structure:\n")
print(df_ai %>% group_by(structure) %>% 
        summarise(mean = mean(ai_summary_accuracy, na.rm = TRUE), 
                  sd = sd(ai_summary_accuracy, na.rm = TRUE), n = n()))

cat("\nMarginal Means - Timing:\n")
print(df_ai %>% group_by(timing) %>% 
        summarise(mean = mean(ai_summary_accuracy, na.rm = TRUE), 
                  sd = sd(ai_summary_accuracy, na.rm = TRUE), n = n()))

# Run Mixed ANOVA using afex
cat("\n\n--- MIXED ANOVA RESULTS (AI Summary Accuracy) ---\n\n")
anova_summary <- aov_ez(
  id = "participant_id",
  dv = "ai_summary_accuracy",
  data = df_ai,
  between = "structure",
  within = "timing",
  type = 3
)

# Print ANOVA table
cat("ANOVA Table:\n")
print(summary(anova_summary))

# Mauchly's test for sphericity
cat("\n\nMauchly's Test for Sphericity:\n")
print(anova_summary$anova_table)

# Effect sizes
cat("\n\nEffect Sizes (Generalized Eta-Squared):\n")
print(anova_summary$anova_table[, c("ges")])

# Post-hoc tests based on significance
cat("\n\n--- POST-HOC ANALYSES (AI Summary Accuracy) ---\n\n")

# Get emmeans for interaction
emm_interaction <- emmeans(anova_summary, ~ timing | structure)
cat("Estimated Marginal Means by Timing within Structure:\n")
print(emm_interaction)

# Simple effects of timing within each structure level
cat("\n\nSimple Effects of Timing within Structure:\n")
timing_within_structure <- pairs(emm_interaction, adjust = "holm")
print(timing_within_structure)

# Emmeans by structure within timing
emm_structure <- emmeans(anova_summary, ~ structure | timing)
cat("\n\nSimple Effects of Structure within Timing:\n")
structure_within_timing <- pairs(emm_structure, adjust = "holm")
print(structure_within_timing)

# Main effect post-hocs
emm_timing <- emmeans(anova_summary, ~ timing)
cat("\n\nPairwise Comparisons for Timing (main effect):\n")
timing_posthoc <- pairs(emm_timing, adjust = "holm")
print(timing_posthoc)

# Interaction plot
summary_plot <- ggplot(summary_desc, aes(x = timing, y = mean, color = structure, group = structure)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.15) +
  labs(title = "AI Summary Accuracy: Structure × Timing Interaction",
       x = "Timing", y = "AI Summary Accuracy (Mean ± SE)",
       color = "Structure") +
  theme_minimal() +
  scale_color_brewer(palette = "Set1") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave(file.path(output_dir, "ai_summary_accuracy_interaction.png"), summary_plot, width = 10, height = 7)

# =============================================================================
# ANALYSIS 3: False Lures Selected - 2x3 Mixed Design ANOVA
# =============================================================================
cat("\n\n############################################################\n")
cat("ANALYSIS 3: FALSE LURES SELECTED - 2x3 MIXED DESIGN ANOVA\n")
cat("(Structure: between-subjects, Timing: within-subjects)\n")
cat("############################################################\n\n")

# Descriptive statistics
cat("Descriptive Statistics - False Lures Selected:\n")
lures_desc <- df_ai %>%
  group_by(structure, timing) %>%
  summarise(
    n = n(),
    mean = mean(false_lures_selected, na.rm = TRUE),
    sd = sd(false_lures_selected, na.rm = TRUE),
    se = sd / sqrt(n),
    .groups = "drop"
  )
print(lures_desc)

cat("\n\nMarginal Means - Structure:\n")
print(df_ai %>% group_by(structure) %>% 
        summarise(mean = mean(false_lures_selected, na.rm = TRUE), 
                  sd = sd(false_lures_selected, na.rm = TRUE), n = n()))

cat("\nMarginal Means - Timing:\n")
print(df_ai %>% group_by(timing) %>% 
        summarise(mean = mean(false_lures_selected, na.rm = TRUE), 
                  sd = sd(false_lures_selected, na.rm = TRUE), n = n()))

# Run Mixed ANOVA using afex
cat("\n\n--- MIXED ANOVA RESULTS (False Lures Selected) ---\n\n")
anova_lures <- aov_ez(
  id = "participant_id",
  dv = "false_lures_selected",
  data = df_ai,
  between = "structure",
  within = "timing",
  type = 3
)

# Print ANOVA table
cat("ANOVA Table:\n")
print(summary(anova_lures))

# Mauchly's test for sphericity
cat("\n\nMauchly's Test for Sphericity & Corrected Results:\n")
print(anova_lures$anova_table)

# Effect sizes
cat("\n\nEffect Sizes (Generalized Eta-Squared):\n")
print(anova_lures$anova_table[, c("ges")])

# Post-hoc tests
cat("\n\n--- POST-HOC ANALYSES (False Lures Selected) ---\n\n")

# Get emmeans for interaction
emm_lures_interaction <- emmeans(anova_lures, ~ timing | structure)
cat("Estimated Marginal Means by Timing within Structure:\n")
print(emm_lures_interaction)

# Simple effects of timing within each structure level
cat("\n\nSimple Effects of Timing within Structure:\n")
lures_timing_within_structure <- pairs(emm_lures_interaction, adjust = "holm")
print(lures_timing_within_structure)

# Emmeans by structure within timing
emm_lures_structure <- emmeans(anova_lures, ~ structure | timing)
cat("\n\nSimple Effects of Structure within Timing:\n")
lures_structure_within_timing <- pairs(emm_lures_structure, adjust = "holm")
print(lures_structure_within_timing)

# Main effect post-hocs
emm_lures_timing <- emmeans(anova_lures, ~ timing)
cat("\n\nPairwise Comparisons for Timing (main effect):\n")
lures_timing_posthoc <- pairs(emm_lures_timing, adjust = "holm")
print(lures_timing_posthoc)

# Interaction plot
lures_plot <- ggplot(lures_desc, aes(x = timing, y = mean, color = structure, group = structure)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.15) +
  labs(title = "False Lures Selected: Structure × Timing Interaction",
       x = "Timing", y = "False Lures Selected (Mean ± SE)",
       color = "Structure") +
  theme_minimal() +
  scale_color_brewer(palette = "Set1") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave(file.path(output_dir, "false_lures_interaction.png"), lures_plot, width = 10, height = 7)

# =============================================================================
# SUMMARY OF ALL RESULTS
# =============================================================================
cat("\n\n############################################################\n")
cat("SUMMARY OF ALL ANALYSES\n")
cat("############################################################\n\n")

cat("ANALYSIS 1: MCQ Accuracy (AI vs Non-AI)\n")
cat("----------------------------------------\n")
cat(sprintf("t(%d) = %.3f, p = %.4f\n", t_result$parameter, t_result$statistic, t_result$p.value))
cat(sprintf("AI: M = %.3f, SD = %.3f (n = %d)\n", 
            mcq_desc$mean[mcq_desc$experiment_group == "AI"],
            mcq_desc$sd[mcq_desc$experiment_group == "AI"],
            mcq_desc$n[mcq_desc$experiment_group == "AI"]))
cat(sprintf("NoAI: M = %.3f, SD = %.3f (n = %d)\n", 
            mcq_desc$mean[mcq_desc$experiment_group == "NoAI"],
            mcq_desc$sd[mcq_desc$experiment_group == "NoAI"],
            mcq_desc$n[mcq_desc$experiment_group == "NoAI"]))
cat(sprintf("Cohen's d = %.3f\n\n", cohens_d_mcq$Cohens_d))

cat("ANALYSIS 2: AI Summary Accuracy (2x3 Mixed ANOVA)\n")
cat("-------------------------------------------------\n")
print(anova_summary$anova_table)

cat("\n\nANALYSIS 3: False Lures Selected (2x3 Mixed ANOVA)\n")
cat("---------------------------------------------------\n")
print(anova_lures$anova_table)

cat("\n\nPlots saved to:", output_dir, "\n")
cat("\nAnalysis complete!\n")

# Save summary to file
sink(file.path(output_dir, "anova_summary_results.txt"))
cat("============================================================\n")
cat("MIXED DESIGN ANOVA ANALYSIS - SUMMARY RESULTS\n")
cat("============================================================\n\n")

cat("ANALYSIS 1: MCQ Accuracy (AI vs Non-AI)\n")
cat("----------------------------------------\n")
cat(sprintf("t(%d) = %.3f, p = %.4f\n", t_result$parameter, t_result$statistic, t_result$p.value))
cat(sprintf("AI: M = %.3f, SD = %.3f (n = %d)\n", 
            mcq_desc$mean[mcq_desc$experiment_group == "AI"],
            mcq_desc$sd[mcq_desc$experiment_group == "AI"],
            mcq_desc$n[mcq_desc$experiment_group == "AI"]))
cat(sprintf("NoAI: M = %.3f, SD = %.3f (n = %d)\n", 
            mcq_desc$mean[mcq_desc$experiment_group == "NoAI"],
            mcq_desc$sd[mcq_desc$experiment_group == "NoAI"],
            mcq_desc$n[mcq_desc$experiment_group == "NoAI"]))
cat(sprintf("Cohen's d = %.3f\n\n", cohens_d_mcq$Cohens_d))

cat("\nANALYSIS 2: AI Summary Accuracy (2x3 Mixed ANOVA)\n")
cat("-------------------------------------------------\n")
print(anova_summary$anova_table)

cat("\n\nANALYSIS 3: False Lures Selected (2x3 Mixed ANOVA)\n")
cat("---------------------------------------------------\n")
print(anova_lures$anova_table)
sink()
