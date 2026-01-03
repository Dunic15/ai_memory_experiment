#!/usr/bin/env Rscript

# =============================================================================
# INDIVIDUAL DIFFERENCES ANALYSIS - AI MEMORY EXPERIMENT
# =============================================================================
# 1) Trust/Dependence/Prior Knowledge → Outcomes (participant-level)
# 2) Moderation of Timing effects by individual differences
# 3) Prior Knowledge × Group interaction
# 4) Reading/Summary time → Outcomes
# 5) Summary accuracy as mechanism for Timing → MCQ
# =============================================================================

# Load required packages
packages <- c("readxl", "tidyverse", "lme4", "lmerTest", "emmeans", 
              "effectsize", "ggplot2", "MuMIn", "broom", "broom.mixed", "interactions")

for (pkg in packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
  library(pkg, character.only = TRUE)
}

# Set working directory to final_analysis (where data is)
args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])
if (length(script_path) > 0) {
  script_dir <- normalizePath(dirname(script_path), winslash = "/", mustWork = FALSE)
  # If script is in opus subfolder, go up one level
  if (basename(script_dir) == "opus") {
    root <- dirname(script_dir)
  } else {
    root <- script_dir
  }
} else {
  root <- getwd()
}
setwd(root)

# Create output directories (in opus folder)
output_dir <- file.path(root, "opus", "individual_differences")
tables_dir <- file.path(output_dir, "tables")
plots_dir <- file.path(output_dir, "plots")
dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

# Initialize report
report_file <- file.path(output_dir, "report.txt")
sink(report_file)

cat("=============================================================================\n")
cat("INDIVIDUAL DIFFERENCES ANALYSIS - AI MEMORY EXPERIMENT\n")
cat("Generated:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("=============================================================================\n\n")

# =============================================================================
# LOAD AND PREPARE DATA
# =============================================================================
cat("\n############################################################\n")
cat("DATA LOADING AND PREPARATION\n")
cat("############################################################\n\n")

df <- read_excel("Analysis long finals-.xlsx")
cat("Data loaded:", nrow(df), "rows x", ncol(df), "columns\n\n")

# Convert factors
df$participant_id <- as.factor(df$participant_id)
df$experiment_group <- as.factor(df$experiment_group)
df$structure <- as.factor(df$structure)
df$timing <- as.factor(df$timing)
df$article <- as.factor(df$article)

# Convert numeric columns
df$mcq_accuracy <- as.numeric(df$mcq_accuracy)
df$ai_summary_accuracy <- as.numeric(as.character(df$ai_summary_accuracy))
df$article_accuracy <- as.numeric(df$article_accuracy)
df$false_lure_accuracy <- as.numeric(as.character(df$false_lure_accuracy))
df$false_lures_selected <- as.numeric(as.character(df$false_lures_selected))
df$recall_total_score <- as.numeric(df$recall_total_score)
df$reading_time_min <- as.numeric(df$reading_time_min)
df$summary_time_sec <- as.numeric(as.character(df$summary_time_sec))
df$mental_effort <- as.numeric(df$mental_effort)
df$prior_knowledge_familiarity <- as.numeric(df$prior_knowledge_familiarity)
df$ai_trust <- as.numeric(as.character(df$ai_trust))
df$ai_dependence <- as.numeric(as.character(df$ai_dependence))

# Create AI-only subset
df_ai <- df %>%
  filter(experiment_group == "AI" & structure != "control" & timing != "control") %>%
  droplevels()

df_ai$structure <- factor(df_ai$structure, levels = c("integrated", "segmented"))
df_ai$timing <- factor(df_ai$timing, levels = c("pre_reading", "synchronous", "post_reading"))

# Log-transform time variables (due to skew)
df$log_reading_time <- log(df$reading_time_min + 1)
df_ai$log_reading_time <- log(df_ai$reading_time_min + 1)
df_ai$log_summary_time <- log(df_ai$summary_time_sec + 1)

# Center continuous predictors for interactions
df_ai$trust_c <- scale(df_ai$ai_trust, center = TRUE, scale = FALSE)[,1]
df_ai$dependence_c <- scale(df_ai$ai_dependence, center = TRUE, scale = FALSE)[,1]
df_ai$prior_knowledge_c <- scale(df_ai$prior_knowledge_familiarity, center = TRUE, scale = FALSE)[,1]

df$prior_knowledge_c <- scale(df$prior_knowledge_familiarity, center = TRUE, scale = FALSE)[,1]

cat("AI-only subset:", nrow(df_ai), "observations,", length(unique(df_ai$participant_id)), "participants\n")
cat("All data:", nrow(df), "observations,", length(unique(df$participant_id)), "participants\n\n")

# =============================================================================
# SECTION 1: INDIVIDUAL DIFFERENCES → OUTCOMES (PARTICIPANT-LEVEL)
# =============================================================================
cat("\n############################################################\n")
cat("SECTION 1: DO TRUST/DEPENDENCE/PRIOR KNOWLEDGE PREDICT OUTCOMES?\n")
cat("(Participant-level regressions, AI only)\n")
cat("############################################################\n\n")

# Aggregate to participant level
df_ai_agg <- df_ai %>%
  group_by(participant_id) %>%
  summarise(
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    mean_summary_accuracy = mean(ai_summary_accuracy, na.rm = TRUE),
    mean_false_lures = mean(false_lures_selected, na.rm = TRUE),
    ai_trust = first(ai_trust),
    ai_dependence = first(ai_dependence),
    prior_knowledge = first(prior_knowledge_familiarity),
    .groups = "drop"
  )

cat("Participant-level data:", nrow(df_ai_agg), "participants\n\n")

# Regression 1: Mean MCQ
cat("\n=== 1A: Mean MCQ ~ Trust + Dependence + Prior Knowledge ===\n\n")
reg1_mcq <- lm(mean_mcq ~ ai_trust + ai_dependence + prior_knowledge, data = df_ai_agg)
print(summary(reg1_mcq))
cat("\nStandardized coefficients:\n")
print(effectsize::standardize_parameters(reg1_mcq))
write.csv(broom::tidy(reg1_mcq), file.path(tables_dir, "1A_mcq_individual_diff.csv"), row.names = FALSE)

# Regression 2: Mean Summary Accuracy
cat("\n=== 1B: Mean Summary Accuracy ~ Trust + Dependence + Prior Knowledge ===\n\n")
reg1_summary <- lm(mean_summary_accuracy ~ ai_trust + ai_dependence + prior_knowledge, data = df_ai_agg)
print(summary(reg1_summary))
cat("\nStandardized coefficients:\n")
print(effectsize::standardize_parameters(reg1_summary))
write.csv(broom::tidy(reg1_summary), file.path(tables_dir, "1B_summary_individual_diff.csv"), row.names = FALSE)

# Regression 3: Mean False Lures
cat("\n=== 1C: Mean False Lures ~ Trust + Dependence + Prior Knowledge ===\n\n")
reg1_fl <- lm(mean_false_lures ~ ai_trust + ai_dependence + prior_knowledge, data = df_ai_agg)
print(summary(reg1_fl))
cat("\nStandardized coefficients:\n")
print(effectsize::standardize_parameters(reg1_fl))
write.csv(broom::tidy(reg1_fl), file.path(tables_dir, "1C_false_lures_individual_diff.csv"), row.names = FALSE)

# =============================================================================
# SECTION 2: MODERATION OF TIMING EFFECTS
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION 2: DO TRUST/DEPENDENCE/PRIOR KNOWLEDGE MODERATE TIMING EFFECTS?\n")
cat("(Trial-level mixed models, AI only)\n")
cat("############################################################\n\n")

run_moderation_model <- function(data, formula_str, model_name, output_prefix, moderator_name) {
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
  print(round(fe, 4))
  cat("\n")
  
  # Save fixed effects
  fe_df <- as.data.frame(fe)
  fe_df$Term <- rownames(fe_df)
  write.csv(fe_df, file.path(tables_dir, paste0(output_prefix, "_fixed_effects.csv")), row.names = FALSE)
  
  # R-squared
  r2 <- tryCatch({
    r.squaredGLMM(model)
  }, error = function(e) NULL)
  
  if (!is.null(r2)) {
    cat("R² (marginal / conditional):", round(r2[1], 4), "/", round(r2[2], 4), "\n\n")
  }
  
  # Check for significant interaction
  fe_df_check <- as.data.frame(fe)
  interaction_rows <- grep("timing.*:", rownames(fe_df_check))
  
  if (length(interaction_rows) > 0) {
    sig_interactions <- fe_df_check[interaction_rows, "Pr(>|t|)"] < 0.05
    if (any(sig_interactions, na.rm = TRUE)) {
      cat("*** SIGNIFICANT INTERACTION DETECTED - Computing simple slopes ***\n\n")
      
      # Simple slopes at low (-1 SD) and high (+1 SD) of moderator
      tryCatch({
        emm <- emmeans(model, ~ timing, at = list(setNames(list(c(-1, 1) * sd(data[[moderator_name]], na.rm = TRUE)), 
                                                            paste0(moderator_name, "_c"))))
        cat("EMMs at -1 SD and +1 SD of", moderator_name, ":\n")
        print(emm)
      }, error = function(e) {
        cat("Could not compute simple slopes:", e$message, "\n")
      })
    }
  }
  
  return(model)
}

# 2A: Moderation of Timing on Summary Accuracy
cat("\n========== 2A: MODERATION OF TIMING ON SUMMARY ACCURACY ==========\n")

mod2a_trust <- run_moderation_model(
  df_ai,
  "ai_summary_accuracy ~ timing * trust_c + structure + (1|participant_id) + (1|article)",
  "Summary Accuracy ~ Timing × Trust",
  "2A_summary_timing_trust",
  "ai_trust"
)

mod2a_dep <- run_moderation_model(
  df_ai,
  "ai_summary_accuracy ~ timing * dependence_c + structure + (1|participant_id) + (1|article)",
  "Summary Accuracy ~ Timing × Dependence",
  "2A_summary_timing_dependence",
  "ai_dependence"
)

mod2a_pk <- run_moderation_model(
  df_ai,
  "ai_summary_accuracy ~ timing * prior_knowledge_c + structure + (1|participant_id) + (1|article)",
  "Summary Accuracy ~ Timing × Prior Knowledge",
  "2A_summary_timing_prior_knowledge",
  "prior_knowledge_familiarity"
)

# 2B: Moderation of Timing on MCQ
cat("\n========== 2B: MODERATION OF TIMING ON MCQ ACCURACY ==========\n")

mod2b_trust <- run_moderation_model(
  df_ai,
  "mcq_accuracy ~ timing * trust_c + structure + (1|participant_id) + (1|article)",
  "MCQ ~ Timing × Trust",
  "2B_mcq_timing_trust",
  "ai_trust"
)

mod2b_dep <- run_moderation_model(
  df_ai,
  "mcq_accuracy ~ timing * dependence_c + structure + (1|participant_id) + (1|article)",
  "MCQ ~ Timing × Dependence",
  "2B_mcq_timing_dependence",
  "ai_dependence"
)

mod2b_pk <- run_moderation_model(
  df_ai,
  "mcq_accuracy ~ timing * prior_knowledge_c + structure + (1|participant_id) + (1|article)",
  "MCQ ~ Timing × Prior Knowledge",
  "2B_mcq_timing_prior_knowledge",
  "prior_knowledge_familiarity"
)

# =============================================================================
# SECTION 3: PRIOR KNOWLEDGE × GROUP INTERACTION
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION 3: DOES PRIOR KNOWLEDGE CHANGE AI VS NOAI EFFECT?\n")
cat("(Participant-level regression)\n")
cat("############################################################\n\n")

# Aggregate all participants
df_all_agg <- df %>%
  group_by(participant_id, experiment_group) %>%
  summarise(
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    prior_knowledge = first(prior_knowledge_familiarity),
    .groups = "drop"
  )

cat("=== Mean MCQ ~ Group × Prior Knowledge ===\n\n")
reg3 <- lm(mean_mcq ~ experiment_group * prior_knowledge, data = df_all_agg)
print(summary(reg3))

cat("\nStandardized coefficients:\n")
print(effectsize::standardize_parameters(reg3))

write.csv(broom::tidy(reg3), file.path(tables_dir, "3_mcq_group_prior_knowledge.csv"), row.names = FALSE)

# Create interaction plot
p3 <- ggplot(df_all_agg, aes(x = prior_knowledge, y = mean_mcq, color = experiment_group)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(title = "MCQ Accuracy by Prior Knowledge and Group",
       x = "Prior Knowledge", y = "Mean MCQ Accuracy",
       color = "Group") +
  theme_minimal() +
  scale_color_brewer(palette = "Set1")
ggsave(file.path(plots_dir, "3_mcq_group_prior_knowledge.png"), p3, width = 8, height = 6)

# Simple slopes if interaction significant
if (summary(reg3)$coefficients["experiment_groupNoAI:prior_knowledge", "Pr(>|t|)"] < 0.10) {
  cat("\n*** Interaction marginal/significant - Computing simple slopes ***\n")
  
  # Effect of group at low/high prior knowledge
  low_pk <- mean(df_all_agg$prior_knowledge) - sd(df_all_agg$prior_knowledge)
  high_pk <- mean(df_all_agg$prior_knowledge) + sd(df_all_agg$prior_knowledge)
  
  cat("\nEffect of Group at Low Prior Knowledge (M - 1SD =", round(low_pk, 2), "):\n")
  df_all_agg$pk_centered_low <- df_all_agg$prior_knowledge - low_pk
  reg3_low <- lm(mean_mcq ~ experiment_group * pk_centered_low, data = df_all_agg)
  print(summary(reg3_low)$coefficients["experiment_groupNoAI", ])
  
  cat("\nEffect of Group at High Prior Knowledge (M + 1SD =", round(high_pk, 2), "):\n")
  df_all_agg$pk_centered_high <- df_all_agg$prior_knowledge - high_pk
  reg3_high <- lm(mean_mcq ~ experiment_group * pk_centered_high, data = df_all_agg)
  print(summary(reg3_high)$coefficients["experiment_groupNoAI", ])
}

# =============================================================================
# SECTION 4: TIME-ON-TASK → OUTCOMES
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION 4: ARE READING/SUMMARY TIME RELATED TO OUTCOMES?\n")
cat("(Trial-level mixed models)\n")
cat("############################################################\n\n")

# 4A: Reading time → MCQ (all participants)
cat("\n========== 4A: READING TIME → MCQ (ALL PARTICIPANTS) ==========\n")

cat("\n--- Model: MCQ ~ Reading Time + Group ---\n")
mod4a_base <- lmer(mcq_accuracy ~ log_reading_time + experiment_group + (1|participant_id) + (1|article), 
                   data = df)
cat("Fixed Effects:\n")
print(round(summary(mod4a_base)$coefficients, 4))
r2_4a <- r.squaredGLMM(mod4a_base)
cat("\nR² (marginal / conditional):", round(r2_4a[1], 4), "/", round(r2_4a[2], 4), "\n")
write.csv(broom.mixed::tidy(mod4a_base), file.path(tables_dir, "4A_mcq_reading_time.csv"), row.names = FALSE)

cat("\n--- Model: MCQ ~ Reading Time × Group (moderation) ---\n")
mod4a_int <- lmer(mcq_accuracy ~ log_reading_time * experiment_group + (1|participant_id) + (1|article), 
                  data = df)
cat("Fixed Effects:\n")
print(round(summary(mod4a_int)$coefficients, 4))
write.csv(broom.mixed::tidy(mod4a_int), file.path(tables_dir, "4A_mcq_reading_time_interaction.csv"), row.names = FALSE)

# 4B: Summary time → outcomes (AI only)
cat("\n========== 4B: SUMMARY TIME → OUTCOMES (AI ONLY) ==========\n")

cat("\n--- Model: Summary Accuracy ~ Summary Time + Timing + Structure ---\n")
mod4b_summary <- lmer(ai_summary_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article), 
                      data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod4b_summary)$coefficients, 4))
r2_4b1 <- r.squaredGLMM(mod4b_summary)
cat("\nR² (marginal / conditional):", round(r2_4b1[1], 4), "/", round(r2_4b1[2], 4), "\n")
write.csv(broom.mixed::tidy(mod4b_summary), file.path(tables_dir, "4B_summary_summary_time.csv"), row.names = FALSE)

cat("\n--- Model: MCQ ~ Summary Time + Timing + Structure ---\n")
mod4b_mcq <- lmer(mcq_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article), 
                  data = df_ai)
cat("Fixed Effects:\n")
print(round(summary(mod4b_mcq)$coefficients, 4))
r2_4b2 <- r.squaredGLMM(mod4b_mcq)
cat("\nR² (marginal / conditional):", round(r2_4b2[1], 4), "/", round(r2_4b2[2], 4), "\n")
write.csv(broom.mixed::tidy(mod4b_mcq), file.path(tables_dir, "4B_mcq_summary_time.csv"), row.names = FALSE)

# Create scatter plots
p4a <- ggplot(df, aes(x = reading_time_min, y = mcq_accuracy, color = experiment_group)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(title = "MCQ Accuracy by Reading Time",
       x = "Reading Time (min)", y = "MCQ Accuracy",
       color = "Group") +
  theme_minimal() +
  scale_color_brewer(palette = "Set1")
ggsave(file.path(plots_dir, "4A_mcq_reading_time.png"), p4a, width = 8, height = 6)

p4b <- ggplot(df_ai, aes(x = summary_time_sec, y = ai_summary_accuracy, color = timing)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(title = "Summary Accuracy by Summary Time (AI only)",
       x = "Summary Time (sec)", y = "Summary Accuracy",
       color = "Timing") +
  theme_minimal() +
  scale_color_brewer(palette = "Set2")
ggsave(file.path(plots_dir, "4B_summary_summary_time.png"), p4b, width = 8, height = 6)

# =============================================================================
# SECTION 5: SUMMARY ACCURACY AS MECHANISM FOR TIMING → MCQ
# =============================================================================
cat("\n\n############################################################\n")
cat("SECTION 5: DOES SUMMARY ACCURACY EXPLAIN TIMING → MCQ EFFECT?\n")
cat("(Comparing models with/without summary accuracy)\n")
cat("############################################################\n\n")

cat("\n=== Model 1: MCQ ~ Timing + Structure (base) ===\n")
mod5_base <- lmer(mcq_accuracy ~ timing + structure + (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
fe_base <- summary(mod5_base)$coefficients
print(round(fe_base, 4))
r2_base <- r.squaredGLMM(mod5_base)
cat("\nR² (marginal / conditional):", round(r2_base[1], 4), "/", round(r2_base[2], 4), "\n")
cat("AIC:", round(AIC(mod5_base), 2), "\n")

cat("\n=== Model 2: MCQ ~ Timing + Structure + Summary Accuracy ===\n")
mod5_mech <- lmer(mcq_accuracy ~ timing + structure + ai_summary_accuracy + (1|participant_id) + (1|article), data = df_ai)
cat("Fixed Effects:\n")
fe_mech <- summary(mod5_mech)$coefficients
print(round(fe_mech, 4))
r2_mech <- r.squaredGLMM(mod5_mech)
cat("\nR² (marginal / conditional):", round(r2_mech[1], 4), "/", round(r2_mech[2], 4), "\n")
cat("AIC:", round(AIC(mod5_mech), 2), "\n")

# Model comparison
cat("\n=== Model Comparison ===\n")
anova_comparison <- anova(mod5_base, mod5_mech)
print(anova_comparison)

# Compare timing coefficients
cat("\n=== Timing Coefficient Change ===\n")
timing_sync_base <- fe_base["timingsynchronous", "Estimate"]
timing_sync_mech <- fe_mech["timingsynchronous", "Estimate"]
timing_post_base <- fe_base["timingpost_reading", "Estimate"]
timing_post_mech <- fe_mech["timingpost_reading", "Estimate"]

cat("Timing (synchronous):\n")
cat("  Base model:", round(timing_sync_base, 4), "\n")
cat("  With summary accuracy:", round(timing_sync_mech, 4), "\n")
cat("  Change:", round((timing_sync_mech - timing_sync_base) / abs(timing_sync_base) * 100, 1), "%\n\n")

cat("Timing (post_reading):\n")
cat("  Base model:", round(timing_post_base, 4), "\n")
cat("  With summary accuracy:", round(timing_post_mech, 4), "\n")
cat("  Change:", round((timing_post_mech - timing_post_base) / abs(timing_post_base) * 100, 1), "%\n\n")

cat("Summary accuracy coefficient:", round(fe_mech["ai_summary_accuracy", "Estimate"], 4), 
    ", p =", round(fe_mech["ai_summary_accuracy", "Pr(>|t|)"], 4), "\n")

# Save comparison
write.csv(broom.mixed::tidy(mod5_base), file.path(tables_dir, "5_mcq_timing_base.csv"), row.names = FALSE)
write.csv(broom.mixed::tidy(mod5_mech), file.path(tables_dir, "5_mcq_timing_mechanism.csv"), row.names = FALSE)

cat("\n=== Interpretation ===\n")
if (abs((timing_sync_mech - timing_sync_base) / abs(timing_sync_base)) > 0.20) {
  cat("The timing effect on MCQ is PARTIALLY EXPLAINED by summary accuracy.\n")
  cat("When summary accuracy is added, timing coefficients shrink by >20%.\n")
} else {
  cat("Summary accuracy does NOT substantially explain the timing effect on MCQ.\n")
  cat("Timing coefficients remain similar when summary accuracy is added.\n")
}

# =============================================================================
# SUMMARY
# =============================================================================
cat("\n\n############################################################\n")
cat("SUMMARY OF KEY FINDINGS\n")
cat("############################################################\n\n")

cat("1) Individual Differences → Outcomes:\n")
cat("   - See regression tables for trust/dependence/prior knowledge effects\n\n")

cat("2) Moderation of Timing:\n")
cat("   - Check interaction terms (timing × moderator) in tables\n\n")

cat("3) Group × Prior Knowledge:\n")
cat("   - Interaction plot saved\n\n")

cat("4) Time-on-Task:\n")
cat("   - Log-transformed reading/summary time (due to skew)\n")
cat("   - See scatter plots for relationships\n\n")

cat("5) Mechanism Test:\n")
cat("   - Summary accuracy as potential mechanism for timing → MCQ\n")
cat("   - Model comparison saved\n\n")

cat("=============================================================================\n")
cat("END OF INDIVIDUAL DIFFERENCES ANALYSIS\n")
cat("=============================================================================\n")

sink()

cat("\n\n=== ANALYSIS COMPLETE ===\n")
cat("Outputs saved to:", output_dir, "\n")
