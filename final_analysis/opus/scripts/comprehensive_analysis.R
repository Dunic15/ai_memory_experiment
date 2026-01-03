#!/usr/bin/env Rscript

# =============================================================================
# COMPREHENSIVE ANALYSIS FOR AI MEMORY EXPERIMENT
# =============================================================================
# Sections A-G: Full analysis pipeline with mixed models
# Uses long format data (1 row = 1 participant × 1 trial/article)
# =============================================================================

# Load required packages
packages <- c("readxl", "tidyverse", "lme4", "lmerTest", "afex", "emmeans", 
              "effectsize", "ggplot2", "MuMIn", "car", "broom", "broom.mixed")

for (pkg in packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
  library(pkg, character.only = TRUE)
}

# Set working directory
args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])
if (length(script_path) > 0) {
  root <- normalizePath(dirname(script_path), winslash = "/", mustWork = FALSE)
} else {
  root <- getwd()
}
setwd(root)

# Create output directories
output_dir <- file.path(root, "comprehensive_outputs")
tables_dir <- file.path(output_dir, "tables")
plots_dir <- file.path(output_dir, "plots")
dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

# Initialize report
report_file <- file.path(output_dir, "report.txt")
sink(report_file)

cat("=============================================================================\n")
cat("COMPREHENSIVE ANALYSIS REPORT - AI MEMORY EXPERIMENT\n")
cat("Generated:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("=============================================================================\n\n")

# =============================================================================
# LOAD AND PREPARE DATA
# =============================================================================
cat("\n############################################################\n")
cat("DATA LOADING AND PREPARATION\n")
cat("############################################################\n\n")

df <- read_excel("Analysis long finals-.xlsx")
cat("Data loaded: ", nrow(df), "rows x", ncol(df), "columns\n\n")

# Convert factors
df$participant_id <- as.factor(df$participant_id)
df$experiment_group <- as.factor(df$experiment_group)
df$structure <- as.factor(df$structure)
df$timing <- as.factor(df$timing)
df$article <- as.factor(df$article)

# Convert numeric columns (handle potential "Nan" strings)
df$mcq_accuracy <- as.numeric(df$mcq_accuracy)
df$ai_summary_accuracy <- as.numeric(as.character(df$ai_summary_accuracy))
df$article_accuracy <- as.numeric(df$article_accuracy)
df$false_lure_accuracy <- as.numeric(as.character(df$false_lure_accuracy))
df$false_lures_selected <- as.numeric(as.character(df$false_lures_selected))
df$recall_total_score <- as.numeric(df$recall_total_score)
df$recall_confidence <- as.numeric(df$recall_confidence)
df$reading_time_min <- as.numeric(df$reading_time_min)
df$summary_time_sec <- as.numeric(as.character(df$summary_time_sec))
df$mental_effort <- as.numeric(df$mental_effort)
df$prior_knowledge_familiarity <- as.numeric(df$prior_knowledge_familiarity)
df$ai_trust <- as.numeric(as.character(df$ai_trust))
df$ai_dependence <- as.numeric(as.character(df$ai_dependence))

# Create AI-only subset (exclude control conditions)
df_ai <- df %>%
  filter(experiment_group == "AI" & structure != "control" & timing != "control") %>%
  droplevels()

# Ensure proper factor coding
df_ai$structure <- factor(df_ai$structure, levels = c("integrated", "segmented"))
df_ai$timing <- factor(df_ai$timing, levels = c("pre_reading", "synchronous", "post_reading"))

cat("AI-only subset: ", nrow(df_ai), "observations\n")
cat("  - Structure levels:", levels(df_ai$structure), "\n")
cat("  - Timing levels:", levels(df_ai$timing), "\n")
cat("  - Participants:", length(unique(df_ai$participant_id)), "\n")
cat("  - Articles:", levels(df_ai$article), "\n\n")

# =============================================================================
# SECTION A: TIMING EFFECTS ON LEARNING OUTCOMES (AI ONLY)
# =============================================================================
cat("\n############################################################\n")
cat("SECTION A: TIMING EFFECTS ON LEARNING OUTCOMES (AI ONLY)\n")
cat("############################################################\n\n")

# Helper function for mixed ANOVA with random effects
run_mixed_anova <- function(data, dv_name, dv_formula, output_prefix) {
  cat("\n--- Analysis:", dv_name, "---\n\n")
  
  # Run mixed ANOVA using afex
  anova_result <- tryCatch({
    aov_ez(
      id = "participant_id",
      dv = dv_formula,
      data = data,
      between = "structure",
      within = "timing",
      type = 3
    )
  }, error = function(e) {
    cat("Error in ANOVA:", e$message, "\n")
    return(NULL)
  })
  
  if (is.null(anova_result)) return(NULL)
  
  # Print ANOVA table
  cat("ANOVA Table:\n")
  print(anova_result$anova_table)
  cat("\n")
  
  # Descriptive statistics
  desc_stats <- data %>%
    group_by(structure, timing) %>%
    summarise(
      n = n(),
      mean = mean(get(dv_formula), na.rm = TRUE),
      sd = sd(get(dv_formula), na.rm = TRUE),
      se = sd / sqrt(n),
      .groups = "drop"
    )
  
  cat("Descriptive Statistics:\n")
  print(desc_stats)
  cat("\n")
  
  # Save descriptives
  write.csv(desc_stats, file.path(tables_dir, paste0(output_prefix, "_descriptives.csv")), row.names = FALSE)
  
  # Save ANOVA table
  anova_tbl <- as.data.frame(anova_result$anova_table)
  anova_tbl$Effect <- rownames(anova_tbl)
  write.csv(anova_tbl, file.path(tables_dir, paste0(output_prefix, "_anova.csv")), row.names = FALSE)
  
  # Post-hoc for Timing (if significant)
  emm_timing <- emmeans(anova_result, ~ timing)
  timing_posthoc <- pairs(emm_timing, adjust = "holm")
  cat("Pairwise Comparisons for Timing (Holm-adjusted):\n")
  print(timing_posthoc)
  cat("\n")
  
  # Save post-hoc
  ph_df <- as.data.frame(timing_posthoc)
  write.csv(ph_df, file.path(tables_dir, paste0(output_prefix, "_posthoc_timing.csv")), row.names = FALSE)
  
  # Create interaction plot
  p <- ggplot(desc_stats, aes(x = timing, y = mean, color = structure, group = structure)) +
    geom_line(linewidth = 1.2) +
    geom_point(size = 3) +
    geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.15) +
    labs(title = paste(dv_name, "by Structure × Timing"),
         x = "Timing", y = paste(dv_name, "(Mean ± SE)")) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 30, hjust = 1)) +
    scale_color_brewer(palette = "Set1")
  
  ggsave(file.path(plots_dir, paste0(output_prefix, "_plot.png")), p, width = 8, height = 6)
  
  return(anova_result)
}

# A1: MCQ Accuracy
cat("\n=== A1: MCQ Accuracy ===\n")
anova_mcq <- run_mixed_anova(df_ai, "MCQ Accuracy", "mcq_accuracy", "A1_mcq_accuracy")

# A2: Recall Total Score
cat("\n=== A2: Recall Total Score ===\n")
anova_recall <- run_mixed_anova(df_ai, "Recall Total Score", "recall_total_score", "A2_recall_total_score")

# A3: Article Accuracy
cat("\n=== A3: Article Accuracy ===\n")
anova_article <- run_mixed_anova(df_ai, "Article Accuracy", "article_accuracy", "A3_article_accuracy")

# =============================================================================
# SECTION B: MECHANISM TEST - SUMMARY ACCURACY PREDICTS LEARNING
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION B: DOES SUMMARY ACCURACY PREDICT LEARNING? (AI ONLY)\n")
cat("############################################################\n\n")

run_mixed_model <- function(data, formula_str, model_name, output_prefix) {
  cat("\n--- Model:", model_name, "---\n")
  cat("Formula:", formula_str, "\n\n")
  
  model <- tryCatch({
    lmer(as.formula(formula_str), data = data, REML = TRUE)
  }, error = function(e) {
    cat("Error fitting model:", e$message, "\n")
    return(NULL)
  })
  
  if (is.null(model)) return(NULL)
  
  # Fixed effects
  cat("Fixed Effects:\n")
  fe <- summary(model)$coefficients
  print(fe)
  cat("\n")
  
  # Save fixed effects
  fe_df <- as.data.frame(fe)
  fe_df$Term <- rownames(fe_df)
  write.csv(fe_df, file.path(tables_dir, paste0(output_prefix, "_fixed_effects.csv")), row.names = FALSE)
  
  # R-squared
  r2 <- tryCatch({
    r.squaredGLMM(model)
  }, error = function(e) {
    cat("Could not compute R²\n")
    return(NULL)
  })
  
  if (!is.null(r2)) {
    cat("R² (marginal / conditional):", r2[1], "/", r2[2], "\n\n")
  }
  
  return(model)
}

# B1: Trial-level mixed-effects regressions
cat("\n=== B1: AI Summary Accuracy → Learning Outcomes ===\n")

# Model 1: MCQ
model_b1_mcq <- run_mixed_model(
  df_ai,
  "mcq_accuracy ~ ai_summary_accuracy + timing + structure + (1|participant_id) + (1|article)",
  "MCQ ~ Summary Accuracy",
  "B1_mcq_summary"
)

# Model 2: Recall
model_b1_recall <- run_mixed_model(
  df_ai,
  "recall_total_score ~ ai_summary_accuracy + timing + structure + (1|participant_id) + (1|article)",
  "Recall ~ Summary Accuracy",
  "B1_recall_summary"
)

# Model 3: Article Accuracy
model_b1_article <- run_mixed_model(
  df_ai,
  "article_accuracy ~ ai_summary_accuracy + timing + structure + (1|participant_id) + (1|article)",
  "Article Accuracy ~ Summary Accuracy",
  "B1_article_summary"
)

# =============================================================================
# SECTION C: STRUCTURE → FALSE LURES MECHANISM
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION C: EXPLAINING STRUCTURE → FALSE LURES (AI ONLY)\n")
cat("############################################################\n\n")

# C1: False Lure Accuracy ANOVA
cat("\n=== C1: False Lure Accuracy ANOVA ===\n")
anova_fla <- run_mixed_anova(df_ai, "False Lure Accuracy", "false_lure_accuracy", "C1_false_lure_accuracy")

# C2: Is Structure effect explained by effort/time?
cat("\n=== C2: Structure Effect on False Lures - Mechanism Models ===\n")

# Base model
cat("\n-- Base Model --\n")
model_c2_base <- run_mixed_model(
  df_ai,
  "false_lures_selected ~ structure + timing + (1|participant_id) + (1|article)",
  "False Lures ~ Structure + Timing (Base)",
  "C2_false_lures_base"
)

# Mechanism model
cat("\n-- Mechanism Model (adding effort/time) --\n")
model_c2_mech <- run_mixed_model(
  df_ai,
  "false_lures_selected ~ structure + timing + mental_effort + reading_time_min + summary_time_sec + (1|participant_id) + (1|article)",
  "False Lures ~ Structure + Timing + Mechanisms",
  "C2_false_lures_mechanism"
)

# Compare coefficients
if (!is.null(model_c2_base) && !is.null(model_c2_mech)) {
  cat("\n-- Coefficient Comparison (Structure) --\n")
  base_coef <- fixef(model_c2_base)["structuresegmented"]
  mech_coef <- fixef(model_c2_mech)["structuresegmented"]
  cat("Base model structure coefficient:", base_coef, "\n")
  cat("Mechanism model structure coefficient:", mech_coef, "\n")
  cat("Change:", round((mech_coef - base_coef) / base_coef * 100, 2), "%\n\n")
}

# =============================================================================
# SECTION D: EFFORT/TIME AS PROCESS VARIABLES
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION D: EFFORT/TIME AS PROCESS VARIABLES (AI ONLY)\n")
cat("############################################################\n\n")

# D1: Mental Effort
cat("\n=== D1: Mental Effort ===\n")
anova_effort <- run_mixed_anova(df_ai, "Mental Effort", "mental_effort", "D1_mental_effort")

# D2: Summary Time
cat("\n=== D2: Summary Time ===\n")
anova_sumtime <- run_mixed_anova(df_ai, "Summary Time (sec)", "summary_time_sec", "D2_summary_time")

# D3: Reading Time
cat("\n=== D3: Reading Time ===\n")
anova_readtime <- run_mixed_anova(df_ai, "Reading Time (min)", "reading_time_min", "D3_reading_time")

# =============================================================================
# SECTION E: AI TRUST/DEPENDENCE AS MODERATORS
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION E: AI TRUST/DEPENDENCE AS MODERATORS (AI ONLY)\n")
cat("############################################################\n\n")

# E1: Participant-level aggregation
cat("\n=== E1: Trust/Dependence Predict Performance (Participant-level) ===\n")

df_ai_agg <- df_ai %>%
  group_by(participant_id) %>%
  summarise(
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    mean_ai_summary_accuracy = mean(ai_summary_accuracy, na.rm = TRUE),
    mean_false_lures = mean(false_lures_selected, na.rm = TRUE),
    mean_mental_effort = mean(mental_effort, na.rm = TRUE),
    mean_summary_time = mean(summary_time_sec, na.rm = TRUE),
    ai_trust = first(ai_trust),
    ai_dependence = first(ai_dependence),
    prior_knowledge_familiarity = first(prior_knowledge_familiarity),
    .groups = "drop"
  )

# Regression 1: MCQ
cat("\n-- Mean MCQ ~ Trust + Dependence + Prior Knowledge --\n")
reg_e1_mcq <- lm(mean_mcq ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = df_ai_agg)
print(summary(reg_e1_mcq))
write.csv(broom::tidy(reg_e1_mcq), file.path(tables_dir, "E1_mcq_trust_reg.csv"), row.names = FALSE)

# Regression 2: Summary Accuracy
cat("\n-- Mean Summary Accuracy ~ Trust + Dependence + Prior Knowledge --\n")
reg_e1_summary <- lm(mean_ai_summary_accuracy ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = df_ai_agg)
print(summary(reg_e1_summary))
write.csv(broom::tidy(reg_e1_summary), file.path(tables_dir, "E1_summary_trust_reg.csv"), row.names = FALSE)

# Regression 3: False Lures
cat("\n-- Mean False Lures ~ Trust + Dependence + Prior Knowledge --\n")
reg_e1_fl <- lm(mean_false_lures ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = df_ai_agg)
print(summary(reg_e1_fl))
write.csv(broom::tidy(reg_e1_fl), file.path(tables_dir, "E1_false_lures_trust_reg.csv"), row.names = FALSE)

# E2: Moderation - Trust × Timing on Summary Accuracy
cat("\n=== E2: Moderation - Trust/Dependence × Timing ===\n")

# Center predictors for interaction
df_ai$ai_trust_c <- scale(df_ai$ai_trust, center = TRUE, scale = FALSE)
df_ai$ai_dependence_c <- scale(df_ai$ai_dependence, center = TRUE, scale = FALSE)

# Model with Trust × Timing
cat("\n-- Summary Accuracy ~ Timing × Trust + Structure --\n")
model_e2_trust <- run_mixed_model(
  df_ai,
  "ai_summary_accuracy ~ timing * ai_trust_c + structure + (1|participant_id) + (1|article)",
  "Summary Accuracy ~ Timing × Trust",
  "E2_summary_timing_trust"
)

# Model with Dependence × Timing
cat("\n-- Summary Accuracy ~ Timing × Dependence + Structure --\n")
model_e2_dep <- run_mixed_model(
  df_ai,
  "ai_summary_accuracy ~ timing * ai_dependence_c + structure + (1|participant_id) + (1|article)",
  "Summary Accuracy ~ Timing × Dependence",
  "E2_summary_timing_dependence"
)

# =============================================================================
# SECTION F: CONFIDENCE CALIBRATION
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION F: CONFIDENCE CALIBRATION\n")
cat("############################################################\n\n")

# F1: Correlation between confidence and recall
cat("\n=== F1: Confidence-Recall Correlation ===\n")

# Overall correlation
cor_overall <- cor.test(df$recall_confidence, df$recall_total_score, method = "pearson")
cat("\nOverall correlation (all participants):\n")
cat("  r =", round(cor_overall$estimate, 3), 
    ", 95% CI [", round(cor_overall$conf.int[1], 3), ",", round(cor_overall$conf.int[2], 3), "]",
    ", p =", round(cor_overall$p.value, 4), "\n")

# By group
cor_by_group <- df %>%
  group_by(experiment_group) %>%
  summarise(
    r = cor(recall_confidence, recall_total_score, use = "complete.obs"),
    n = n(),
    .groups = "drop"
  )
cat("\nCorrelation by experiment group:\n")
print(cor_by_group)

write.csv(cor_by_group, file.path(tables_dir, "F1_confidence_recall_correlation.csv"), row.names = FALSE)

# F2: Overconfidence index
cat("\n=== F2: Overconfidence Analysis ===\n")

# Compute overconfidence (standardized confidence - standardized recall)
df$overconfidence <- scale(df$recall_confidence) - scale(df$recall_total_score)

# Participant-level mean
overconf_by_participant <- df %>%
  group_by(participant_id, experiment_group) %>%
  summarise(
    mean_overconfidence = mean(overconfidence, na.rm = TRUE),
    .groups = "drop"
  )

# Group comparison
cat("\n-- AI vs NoAI Overconfidence Comparison --\n")
overconf_test <- t.test(mean_overconfidence ~ experiment_group, data = overconf_by_participant)
print(overconf_test)

# Descriptives
overconf_desc <- overconf_by_participant %>%
  group_by(experiment_group) %>%
  summarise(
    n = n(),
    mean = mean(mean_overconfidence, na.rm = TRUE),
    sd = sd(mean_overconfidence, na.rm = TRUE),
    .groups = "drop"
  )
cat("\nDescriptive Statistics:\n")
print(overconf_desc)
write.csv(overconf_desc, file.path(tables_dir, "F2_overconfidence_descriptives.csv"), row.names = FALSE)

# AI-only: Structure × Timing on overconfidence
cat("\n-- AI Only: Overconfidence by Structure × Timing --\n")
df_ai$overconfidence <- scale(df_ai$recall_confidence) - scale(df_ai$recall_total_score)
anova_overconf <- run_mixed_anova(df_ai, "Overconfidence", "overconfidence", "F2_overconfidence")

# =============================================================================
# SECTION G: ARTICLE EFFECTS (ROBUSTNESS)
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION G: ARTICLE EFFECTS (ROBUSTNESS CHECKS)\n")
cat("############################################################\n\n")

# G1: MCQ by Group × Article (all participants)
cat("\n=== G1: MCQ Accuracy ~ Group × Article ===\n")

# All participants model
cat("\n-- All Participants --\n")
model_g1_all <- run_mixed_model(
  df,
  "mcq_accuracy ~ experiment_group * article + (1|participant_id)",
  "MCQ ~ Group × Article",
  "G1_mcq_group_article"
)

# AI-only: Summary Accuracy with Article effect
cat("\n-- AI Only: Summary Accuracy ~ Structure × Timing + Article --\n")
model_g1_ai <- run_mixed_model(
  df_ai,
  "ai_summary_accuracy ~ structure * timing + article + (1|participant_id)",
  "Summary Accuracy ~ Structure × Timing + Article",
  "G1_summary_article"
)

# Article difficulty comparison
cat("\n-- Article Difficulty (MCQ by Article) --\n")
article_difficulty <- df %>%
  group_by(article) %>%
  summarise(
    n = n(),
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    sd_mcq = sd(mcq_accuracy, na.rm = TRUE),
    mean_recall = mean(recall_total_score, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(mean_mcq)

cat("\nArticle Difficulty (sorted by MCQ accuracy):\n")
print(article_difficulty)
write.csv(article_difficulty, file.path(tables_dir, "G1_article_difficulty.csv"), row.names = FALSE)

# =============================================================================
# SUMMARY OF KEY FINDINGS
# =============================================================================
cat("\n\n############################################################\n")
cat("SUMMARY OF KEY FINDINGS\n")
cat("############################################################\n\n")

cat("See individual tables and plots in the comprehensive_outputs folder.\n")
cat("  - Tables: CSV files with ANOVA results, fixed effects, and post-hocs\n")
cat("  - Plots: PNG files with interaction plots\n")
cat("  - This report: Complete text output of all analyses\n\n")

cat("=============================================================================\n")
cat("END OF COMPREHENSIVE ANALYSIS\n")
cat("=============================================================================\n")

sink()

cat("\n\n=== ANALYSIS COMPLETE ===\n")
cat("Outputs saved to:", output_dir, "\n")
cat("  - Tables:", tables_dir, "\n")
cat("  - Plots:", plots_dir, "\n")
cat("  - Report:", report_file, "\n")
