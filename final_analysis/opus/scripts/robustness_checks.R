#!/usr/bin/env Rscript

# =============================================================================
# ROBUSTNESS AND DESIGN CHECKS
# =============================================================================
# A) Design/robustness checks
# B) Core relationship analyses
# C) Individual differences extensions
# =============================================================================

# Load required packages
packages <- c("readxl", "tidyverse", "lme4", "lmerTest", "MuMIn", 
              "broom", "broom.mixed", "emmeans", "car")

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
  script_dir <- normalizePath(dirname(script_path), winslash = "/", mustWork = FALSE)
  if (basename(script_dir) == "scripts") {
    root <- dirname(dirname(script_dir))
  } else if (basename(script_dir) == "opus") {
    root <- dirname(script_dir)
  } else {
    root <- script_dir
  }
} else {
  root <- getwd()
}
setwd(root)

# Create output directories
output_dir <- file.path(root, "opus")
tables_dir <- file.path(output_dir, "all_tables")
dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)

# Initialize report
report_file <- file.path(output_dir, "robustness_checks_report.txt")
sink(report_file)

cat("=============================================================================\n")
cat("ROBUSTNESS AND DESIGN CHECKS\n")
cat("Generated:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("=============================================================================\n\n")

# =============================================================================
# LOAD AND PREPARE DATA
# =============================================================================
df <- read_excel("Analysis long finals-.xlsx")

# Convert factors and numerics
df$participant_id <- as.factor(df$participant_id)
df$experiment_group <- as.factor(df$experiment_group)
df$structure <- as.factor(df$structure)
df$timing <- as.factor(df$timing)
df$article <- as.factor(df$article)

df$mcq_accuracy <- as.numeric(df$mcq_accuracy)
df$article_accuracy <- as.numeric(df$article_accuracy)
df$ai_summary_accuracy <- as.numeric(as.character(df$ai_summary_accuracy))
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

# Log-transform time variables
df$log_reading_time <- log(df$reading_time_min + 1)
df$log_summary_time <- log(as.numeric(as.character(df$summary_time_sec)) + 1)

# AI-only subset
df_ai <- df %>%
  filter(experiment_group == "AI" & structure != "control" & timing != "control") %>%
  droplevels()

df_ai$structure <- factor(df_ai$structure, levels = c("integrated", "segmented"))
df_ai$timing <- factor(df_ai$timing, levels = c("pre_reading", "synchronous", "post_reading"))
df_ai$log_summary_time <- log(df_ai$summary_time_sec + 1)

cat("Data loaded:", nrow(df), "rows (all),", nrow(df_ai), "rows (AI only)\n\n")

# =============================================================================
# SECTION A: DESIGN/ROBUSTNESS CHECKS
# =============================================================================
cat("\n############################################################\n")
cat("SECTION A: DESIGN / ROBUSTNESS CHECKS\n")
cat("############################################################\n\n")

# -----------------------------------------------------------------------------
# A1: ARTICLE DIFFICULTY ACROSS ALL OUTCOMES
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("A1: ARTICLE DIFFICULTY ACROSS ALL OUTCOMES\n")
cat("==========================================================\n\n")

run_article_model <- function(data, dv, formula_str, model_name) {
  cat("\n---", model_name, "---\n")
  cat("Formula:", formula_str, "\n\n")
  
  model <- tryCatch({
    lmer(as.formula(formula_str), data = data)
  }, error = function(e) {
    cat("Error:", e$message, "\n")
    return(NULL)
  })
  
  if (is.null(model)) return(NULL)
  
  fe <- summary(model)$coefficients
  cat("Fixed Effects:\n")
  print(round(fe, 4))
  cat("\n")
  
  return(model)
}

# Article accuracy (all participants)
mod_a1_article <- run_article_model(
  df, "article_accuracy",
  "article_accuracy ~ article + experiment_group + (1|participant_id)",
  "Article Accuracy ~ Article + Group"
)

# Recall (all participants)
mod_a1_recall <- run_article_model(
  df, "recall_total_score",
  "recall_total_score ~ article + experiment_group + (1|participant_id)",
  "Recall ~ Article + Group"
)

# Summary accuracy (AI only)
mod_a1_summary <- run_article_model(
  df_ai, "ai_summary_accuracy",
  "ai_summary_accuracy ~ article + structure + (1|participant_id)",
  "Summary Accuracy ~ Article + Structure (AI only)"
)

# False lure accuracy (AI only)
mod_a1_fla <- run_article_model(
  df_ai, "false_lure_accuracy",
  "false_lure_accuracy ~ article + structure + (1|participant_id)",
  "False Lure Accuracy ~ Article + Structure (AI only)"
)

# False lures selected (AI only)
mod_a1_fls <- run_article_model(
  df_ai, "false_lures_selected",
  "false_lures_selected ~ article + structure + (1|participant_id)",
  "False Lures Selected ~ Article + Structure (AI only)"
)

# Article difficulty summary
cat("\n--- ARTICLE DIFFICULTY SUMMARY ---\n\n")
article_summary <- df %>%
  group_by(article) %>%
  summarise(
    mcq = mean(mcq_accuracy, na.rm = TRUE),
    article_acc = mean(article_accuracy, na.rm = TRUE),
    recall = mean(recall_total_score, na.rm = TRUE),
    .groups = "drop"
  )

article_summary_ai <- df_ai %>%
  group_by(article) %>%
  summarise(
    summary_acc = mean(ai_summary_accuracy, na.rm = TRUE),
    false_lure_acc = mean(false_lure_accuracy, na.rm = TRUE),
    false_lures = mean(false_lures_selected, na.rm = TRUE),
    .groups = "drop"
  )

cat("All Participants:\n")
print(article_summary)
cat("\nAI Only:\n")
print(article_summary_ai)

write.csv(merge(article_summary, article_summary_ai, by = "article", all = TRUE),
          file.path(tables_dir, "ROB_A1_article_difficulty_all_outcomes.csv"), row.names = FALSE)

# -----------------------------------------------------------------------------
# A2: COUNTERBALANCING CHECK (TIMING × ARTICLE)
# -----------------------------------------------------------------------------
cat("\n\n==========================================================\n")
cat("A2: COUNTERBALANCING CHECK (TIMING × ARTICLE)\n")
cat("==========================================================\n\n")

# Create contingency table
timing_article_table <- table(df_ai$timing, df_ai$article)
cat("Contingency Table (Timing × Article):\n")
print(timing_article_table)
cat("\n")

# Chi-square test
chi_test <- chisq.test(timing_article_table)
cat("Chi-square test of independence:\n")
cat("  X² =", round(chi_test$statistic, 3), 
    ", df =", chi_test$parameter,
    ", p =", round(chi_test$p.value, 4), "\n\n")

if (chi_test$p.value > 0.05) {
  cat("✓ Counterbalancing appears adequate (p > .05)\n")
} else {
  cat("⚠ Counterbalancing may be imbalanced (p < .05)\n")
}

cat("\nExpected counts:\n")
print(round(chi_test$expected, 2))

# -----------------------------------------------------------------------------
# A3: TOPIC-SPECIFIC TIMING EFFECTS (TIMING × ARTICLE)
# -----------------------------------------------------------------------------
cat("\n\n==========================================================\n")
cat("A3: TOPIC-SPECIFIC TIMING EFFECTS (TIMING × ARTICLE)\n")
cat("==========================================================\n\n")

# Summary accuracy ~ timing * article
cat("--- Summary Accuracy ~ Timing × Article + Structure ---\n\n")
mod_a3_summary <- lmer(ai_summary_accuracy ~ timing * article + structure + (1|participant_id), 
                       data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_a3_summary)$coefficients, 4))
cat("\n")

# Test interaction significance
anova_a3_summary <- anova(mod_a3_summary)
cat("ANOVA for Timing × Article interaction:\n")
print(round(anova_a3_summary, 4))
cat("\n")

# MCQ ~ timing * article
cat("--- MCQ Accuracy ~ Timing × Article + Structure ---\n\n")
mod_a3_mcq <- lmer(mcq_accuracy ~ timing * article + structure + (1|participant_id), 
                   data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_a3_mcq)$coefficients, 4))
cat("\n")

anova_a3_mcq <- anova(mod_a3_mcq)
cat("ANOVA for Timing × Article interaction:\n")
print(round(anova_a3_mcq, 4))
cat("\n")

write.csv(broom.mixed::tidy(mod_a3_summary), 
          file.path(tables_dir, "ROB_A3_summary_timing_article.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod_a3_mcq), 
          file.path(tables_dir, "ROB_A3_mcq_timing_article.csv"), row.names = FALSE)

# =============================================================================
# SECTION B: CORE RELATIONSHIP ANALYSES
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION B: CORE RELATIONSHIP ANALYSES\n")
cat("############################################################\n\n")

# -----------------------------------------------------------------------------
# B4: READING TIME → LEARNING (OTHER OUTCOMES)
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("B4: READING TIME → LEARNING (ARTICLE ACC, RECALL)\n")
cat("==========================================================\n\n")

# Article accuracy (all participants)
cat("--- Article Accuracy ~ log(Reading Time) + Group ---\n\n")
mod_b4_article <- lmer(article_accuracy ~ log_reading_time + experiment_group + 
                        (1|participant_id) + (1|article), data = df)
cat("Fixed Effects:\n")
print(round(summary(mod_b4_article)$coefficients, 4))
r2_b4a <- r.squaredGLMM(mod_b4_article)
cat("\nR² (marginal / conditional):", round(r2_b4a[1], 4), "/", round(r2_b4a[2], 4), "\n\n")

# Recall (all participants)
cat("--- Recall ~ log(Reading Time) + Group ---\n\n")
mod_b4_recall <- lmer(recall_total_score ~ log_reading_time + experiment_group + 
                       (1|participant_id) + (1|article), data = df)
cat("Fixed Effects:\n")
print(round(summary(mod_b4_recall)$coefficients, 4))
r2_b4r <- r.squaredGLMM(mod_b4_recall)
cat("\nR² (marginal / conditional):", round(r2_b4r[1], 4), "/", round(r2_b4r[2], 4), "\n\n")

write.csv(broom.mixed::tidy(mod_b4_article), 
          file.path(tables_dir, "ROB_B4_article_reading_time.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod_b4_recall), 
          file.path(tables_dir, "ROB_B4_recall_reading_time.csv"), row.names = FALSE)

# -----------------------------------------------------------------------------
# B5: MENTAL EFFORT AS PREDICTOR
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("B5: MENTAL EFFORT AS PREDICTOR\n")
cat("==========================================================\n\n")

# MCQ (AI only)
cat("--- MCQ ~ Mental Effort + Reading Time + Summary Time (AI only) ---\n\n")
mod_b5_mcq <- lmer(mcq_accuracy ~ mental_effort + log_reading_time + log_summary_time + 
                    timing + structure + (1|participant_id) + (1|article), 
                   data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b5_mcq)$coefficients, 4))
r2_b5m <- r.squaredGLMM(mod_b5_mcq)
cat("\nR² (marginal / conditional):", round(r2_b5m[1], 4), "/", round(r2_b5m[2], 4), "\n\n")

# Summary accuracy (AI only)
cat("--- Summary Accuracy ~ Mental Effort + Reading Time + Summary Time (AI only) ---\n\n")
mod_b5_summary <- lmer(ai_summary_accuracy ~ mental_effort + log_reading_time + log_summary_time + 
                        timing + structure + (1|participant_id) + (1|article), 
                       data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b5_summary)$coefficients, 4))
r2_b5s <- r.squaredGLMM(mod_b5_summary)
cat("\nR² (marginal / conditional):", round(r2_b5s[1], 4), "/", round(r2_b5s[2], 4), "\n\n")

# False lures (AI only)
cat("--- False Lures ~ Mental Effort + Reading Time + Summary Time (AI only) ---\n\n")
mod_b5_fl <- lmer(false_lures_selected ~ mental_effort + log_reading_time + log_summary_time + 
                   timing + structure + (1|participant_id) + (1|article), 
                  data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b5_fl)$coefficients, 4))
r2_b5f <- r.squaredGLMM(mod_b5_fl)
cat("\nR² (marginal / conditional):", round(r2_b5f[1], 4), "/", round(r2_b5f[2], 4), "\n\n")

write.csv(broom.mixed::tidy(mod_b5_mcq), 
          file.path(tables_dir, "ROB_B5_mcq_effort.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod_b5_summary), 
          file.path(tables_dir, "ROB_B5_summary_effort.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod_b5_fl), 
          file.path(tables_dir, "ROB_B5_false_lures_effort.csv"), row.names = FALSE)

# -----------------------------------------------------------------------------
# B6: CONFIDENCE CALIBRATION (TRIAL-LEVEL)
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("B6: CONFIDENCE CALIBRATION (TRIAL-LEVEL)\n")
cat("==========================================================\n\n")

# All participants
cat("--- Recall ~ Confidence × Group ---\n\n")
df$confidence_c <- scale(df$recall_confidence, center = TRUE, scale = FALSE)[,1]
mod_b6_all <- lmer(recall_total_score ~ confidence_c * experiment_group + 
                    (1|participant_id) + (1|article), data = df)
cat("Fixed Effects:\n")
print(round(summary(mod_b6_all)$coefficients, 4))
cat("\n")

# AI only with timing/structure
cat("--- Recall ~ Confidence + Timing + Structure (AI only) ---\n\n")
df_ai$confidence_c <- scale(df_ai$recall_confidence, center = TRUE, scale = FALSE)[,1]
mod_b6_ai <- lmer(recall_total_score ~ confidence_c + timing + structure + 
                   (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b6_ai)$coefficients, 4))
cat("\n")

write.csv(broom.mixed::tidy(mod_b6_all), 
          file.path(tables_dir, "ROB_B6_recall_confidence_group.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod_b6_ai), 
          file.path(tables_dir, "ROB_B6_recall_confidence_ai.csv"), row.names = FALSE)

# -----------------------------------------------------------------------------
# B7: MCQ MECHANISM COMPARISON (SUMMARY VS ARTICLE ACCURACY)
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("B7: MCQ MECHANISM COMPARISON\n")
cat("==========================================================\n\n")

# Model A: MCQ ~ summary accuracy (already done, but for comparison)
cat("--- Model A: MCQ ~ Summary Accuracy ---\n\n")
mod_b7_a <- lmer(mcq_accuracy ~ ai_summary_accuracy + timing + structure + 
                  (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b7_a)$coefficients, 4))
cat("AIC:", round(AIC(mod_b7_a), 2), "\n\n")

# Model B: MCQ ~ article accuracy
cat("--- Model B: MCQ ~ Article Accuracy ---\n\n")
mod_b7_b <- lmer(mcq_accuracy ~ article_accuracy + timing + structure + 
                  (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b7_b)$coefficients, 4))
cat("AIC:", round(AIC(mod_b7_b), 2), "\n\n")

# Model C: MCQ ~ both
cat("--- Model C: MCQ ~ Summary Accuracy + Article Accuracy ---\n\n")
mod_b7_c <- lmer(mcq_accuracy ~ ai_summary_accuracy + article_accuracy + timing + structure + 
                  (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod_b7_c)$coefficients, 4))
cat("AIC:", round(AIC(mod_b7_c), 2), "\n\n")

# Model comparison
cat("--- Model Comparison ---\n")
cat("Model A (Summary only) AIC:", round(AIC(mod_b7_a), 2), "\n")
cat("Model B (Article only) AIC:", round(AIC(mod_b7_b), 2), "\n")
cat("Model C (Both) AIC:", round(AIC(mod_b7_c), 2), "\n\n")

best_model <- c("A (Summary)", "B (Article)", "C (Both)")[which.min(c(AIC(mod_b7_a), AIC(mod_b7_b), AIC(mod_b7_c)))]
cat("Best model:", best_model, "\n\n")

write.csv(broom.mixed::tidy(mod_b7_c), 
          file.path(tables_dir, "ROB_B7_mcq_both_mechanisms.csv"), row.names = FALSE)

# =============================================================================
# SECTION C: INDIVIDUAL DIFFERENCES EXTENSIONS
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION C: INDIVIDUAL DIFFERENCES EXTENSIONS\n")
cat("############################################################\n\n")

# -----------------------------------------------------------------------------
# C8: TRUST/DEPENDENCE/PRIOR KNOWLEDGE → TIME-ON-TASK
# -----------------------------------------------------------------------------
cat("\n==========================================================\n")
cat("C8: TRUST/DEPENDENCE/PRIOR KNOWLEDGE → TIME-ON-TASK\n")
cat("==========================================================\n\n")

# Aggregate to participant level
df_ai_agg <- df_ai %>%
  group_by(participant_id) %>%
  summarise(
    mean_summary_time = mean(summary_time_sec, na.rm = TRUE),
    mean_reading_time = mean(reading_time_min, na.rm = TRUE),
    ai_trust = first(ai_trust),
    ai_dependence = first(ai_dependence),
    prior_knowledge = first(prior_knowledge_familiarity),
    .groups = "drop"
  )

# Summary time
cat("--- Mean Summary Time ~ Trust + Dependence + Prior Knowledge ---\n\n")
reg_c8_summary <- lm(mean_summary_time ~ ai_trust + ai_dependence + prior_knowledge, 
                     data = df_ai_agg)
print(summary(reg_c8_summary))
cat("\n")

# Reading time
cat("--- Mean Reading Time ~ Trust + Dependence + Prior Knowledge ---\n\n")
reg_c8_reading <- lm(mean_reading_time ~ ai_trust + ai_dependence + prior_knowledge, 
                     data = df_ai_agg)
print(summary(reg_c8_reading))
cat("\n")

write.csv(broom::tidy(reg_c8_summary), 
          file.path(tables_dir, "ROB_C8_summary_time_individual_diff.csv"), row.names = FALSE)
write.csv(broom::tidy(reg_c8_reading), 
          file.path(tables_dir, "ROB_C8_reading_time_individual_diff.csv"), row.names = FALSE)

# =============================================================================
# SUMMARY
# =============================================================================
cat("\n\n############################################################\n")
cat("SUMMARY OF ROBUSTNESS CHECKS\n")
cat("############################################################\n\n")

cat("A1) Article Difficulty: Varies across outcomes (see table)\n")
cat("A2) Counterbalancing: X² =", round(chi_test$statistic, 2), ", p =", round(chi_test$p.value, 4), "\n")
cat("A3) Timing × Article: Tested for summary and MCQ\n\n")

cat("B4) Reading Time → Learning: Tested for article acc and recall\n")
cat("B5) Mental Effort: Tested as predictor of MCQ, summary, false lures\n")
cat("B6) Confidence Calibration: Trial-level models with group moderation\n")
cat("B7) MCQ Mechanisms: Summary (A) vs Article (B) vs Both (C)\n")
cat("    Best model:", best_model, "\n\n")

cat("C8) Individual Differences → Time-on-Task: Trust/Dep/PK → summary/reading time\n\n")

cat("=============================================================================\n")
cat("END OF ROBUSTNESS CHECKS\n")
cat("=============================================================================\n")

sink()

cat("\n\n=== ANALYSIS COMPLETE ===\n")
cat("Outputs saved to:", output_dir, "\n")
