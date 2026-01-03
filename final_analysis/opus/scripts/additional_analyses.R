# ============================================================================
# ADDITIONAL ANALYSES - ORDERED REQUEST
# A) AI vs NoAI comparisons
# B) Timing efficiency with time-on-task control
# C) False lures mechanism (binomial models)
# D) MCQ decomposition
# E) Leave-one-article-out robustness
# F) Equivalence test for recall
# ============================================================================

library(tidyverse)
library(lme4)
library(lmerTest)
library(readxl)
library(broom.mixed)
library(emmeans)
library(effectsize)

# Detect script location and set paths
script_dir <- tryCatch({
  dirname(sys.frame(1)$ofile)
}, error = function(e) {
  "."
})

if (grepl("scripts$", script_dir)) {
  root_dir <- dirname(script_dir)
} else if (grepl("opus$", script_dir)) {
  root_dir <- script_dir
} else {
  root_dir <- file.path(getwd(), "opus")
}

tables_dir <- file.path(root_dir, "all_tables")
plots_dir <- file.path(root_dir, "all_plots")

dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

# Load data
data_path <- file.path(dirname(root_dir), "Analysis long finals-.xlsx")
if (!file.exists(data_path)) {
  data_path <- "Analysis long finals-.xlsx"
}

df <- read_excel(data_path)

# Prepare data - convert all character columns to numeric where needed
df <- df %>%
  mutate(
    timing = factor(timing),
    structure = factor(structure),
    article = factor(article),
    experiment_group = factor(experiment_group),
    prior_knowledge = as.numeric(prior_knowledge_familiarity),
    mental_effort = as.numeric(mental_effort),
    recall_confidence = as.numeric(recall_confidence),
    ai_trust = as.numeric(ai_trust),
    ai_dependence = as.numeric(ai_dependence),
    ai_summary_accuracy = as.numeric(ai_summary_accuracy),
    article_accuracy = as.numeric(article_accuracy),
    mcq_accuracy = as.numeric(mcq_accuracy),
    false_lures_selected = as.numeric(false_lures_selected),
    recall_total_score = as.numeric(recall_total_score),
    summary_time_sec_num = as.numeric(summary_time_sec),
    reading_time_min_num = as.numeric(reading_time_min),
    # Create total time variable (AI only)
    total_time_sec = reading_time_min_num * 60 + 
      ifelse(!is.na(summary_time_sec_num), summary_time_sec_num, 0)
  )

df_ai <- df %>% filter(experiment_group == "AI")
df_noai <- df %>% filter(experiment_group == "NoAI")

# Start output
sink(file.path(root_dir, "additional_analyses_report.txt"))

cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("ADDITIONAL ANALYSES - ORDERED REQUEST\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# ============================================================================
# A) PRIMARY ADD-ONS: AI vs NoAI on recall and article accuracy
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("A) AI vs NoAI ON RECALL AND ARTICLE ACCURACY\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# A1: Recall ~ Group
cat("--- A1: Recall ~ Group ---\n\n")

model_a1 <- lmer(recall_total_score ~ experiment_group + article + (1|participant_id),
                 data = df)

cat("Model: recall_total_score ~ experiment_group + article + (1|participant_id)\n\n")
print(summary(model_a1))

# EMMs
emm_a1 <- emmeans(model_a1, ~ experiment_group)
cat("\n--- Estimated Marginal Means ---\n")
print(summary(emm_a1, level = 0.95))

# Contrast
contrast_a1 <- pairs(emm_a1)
cat("\n--- AI vs NoAI Contrast ---\n")
print(summary(contrast_a1, infer = TRUE))

write.csv(tidy(model_a1, effects = "fixed"), 
          file.path(tables_dir, "ADD_A1_recall_group.csv"), row.names = FALSE)
write.csv(as.data.frame(summary(emm_a1)), 
          file.path(tables_dir, "ADD_A1_recall_emms.csv"), row.names = FALSE)

# A2: Article Accuracy ~ Group
cat("\n--- A2: Article Accuracy ~ Group ---\n\n")

model_a2 <- lmer(article_accuracy ~ experiment_group + article + (1|participant_id),
                 data = df)

cat("Model: article_accuracy ~ experiment_group + article + (1|participant_id)\n\n")
print(summary(model_a2))

emm_a2 <- emmeans(model_a2, ~ experiment_group)
cat("\n--- Estimated Marginal Means ---\n")
print(summary(emm_a2, level = 0.95))

contrast_a2 <- pairs(emm_a2)
cat("\n--- AI vs NoAI Contrast ---\n")
print(summary(contrast_a2, infer = TRUE))

write.csv(tidy(model_a2, effects = "fixed"), 
          file.path(tables_dir, "ADD_A2_article_acc_group.csv"), row.names = FALSE)
write.csv(as.data.frame(summary(emm_a2)), 
          file.path(tables_dir, "ADD_A2_article_acc_emms.csv"), row.names = FALSE)

# Summary
cat("\n--- SUMMARY A: AI vs NoAI ---\n")
group_recall <- tidy(model_a1, effects = "fixed") %>% filter(term == "experiment_groupNoAI")
group_art <- tidy(model_a2, effects = "fixed") %>% filter(term == "experiment_groupNoAI")

cat(sprintf("Recall: NoAI - AI = %.3f, p = %.4f [%s]\n", 
            group_recall$estimate, group_recall$p.value,
            if(group_recall$p.value < .05) "SIG" else "ns"))
cat(sprintf("Article Accuracy: NoAI - AI = %.4f, p = %.4f [%s]\n", 
            group_art$estimate, group_art$p.value,
            if(group_art$p.value < .05) "SIG" else "ns"))

# ============================================================================
# B) TIMING EFFICIENCY (AI only) - Controlling for time-on-task
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("B) TIMING EFFICIENCY - Controlling for Total Time (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

cat("Total time = reading_time_min*60 + summary_time_sec\n\n")

# Descriptives
cat("--- Total Time Descriptives by Timing ---\n")
time_desc <- df_ai %>%
  group_by(timing) %>%
  summarise(
    mean_total = mean(total_time_sec, na.rm = TRUE),
    sd_total = sd(total_time_sec, na.rm = TRUE),
    n = n()
  )
print(time_desc)

# Model B1
cat("\n--- Model B1: MCQ ~ timing + structure + total_time_sec + article ---\n\n")

model_b1 <- lmer(mcq_accuracy ~ timing + structure + total_time_sec + article + 
                   (1|participant_id),
                 data = df_ai)

print(summary(model_b1))

# Timing EMMs
emm_b1 <- emmeans(model_b1, ~ timing)
cat("\n--- Estimated Marginal Means (controlling for total time) ---\n")
print(summary(emm_b1))

# Pairwise contrasts with Holm correction
cat("\n--- Timing Contrasts (Holm-corrected) ---\n")
contrasts_b1 <- pairs(emm_b1, adjust = "holm")
print(summary(contrasts_b1, infer = TRUE))

# Effect sizes (Cohen's d approximation)
cat("\n--- Effect Sizes ---\n")
eff_b1 <- eff_size(emm_b1, sigma = sigma(model_b1), edf = df.residual(model_b1))
print(eff_b1)

write.csv(tidy(model_b1, effects = "fixed"), 
          file.path(tables_dir, "ADD_B1_timing_controlled.csv"), row.names = FALSE)
write.csv(as.data.frame(summary(contrasts_b1)), 
          file.path(tables_dir, "ADD_B1_timing_contrasts.csv"), row.names = FALSE)

# Compare to uncontrolled model
cat("\n--- Comparison: Timing effect WITHOUT time control ---\n")
model_b1_nocontrol <- lmer(mcq_accuracy ~ timing + structure + article + (1|participant_id),
                            data = df_ai)

emm_b1_nocontrol <- emmeans(model_b1_nocontrol, ~ timing)
contrasts_b1_nocontrol <- pairs(emm_b1_nocontrol, adjust = "holm")
cat("Without time control:\n")
print(summary(contrasts_b1_nocontrol, infer = TRUE))

cat("\n--- SUMMARY B: Timing Efficiency ---\n")
cat("Does pre-reading still win when controlling for total time on task?\n")
pre_post_controlled <- as.data.frame(summary(contrasts_b1)) %>% 
  filter(grepl("pre_reading - post", contrast))
cat(sprintf("Pre vs Post (controlled): estimate = %.4f, p = %.4f\n", 
            pre_post_controlled$estimate, pre_post_controlled$p.value))

# ============================================================================
# C) FALSE LURES MECHANISM - Binomial Mixed Models (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("C) FALSE LURES MECHANISM - Binomial Models (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# Prepare binomial data
df_ai_lure <- df_ai %>%
  mutate(
    lures_selected = false_lures_selected,
    trials = 2,
    lures_not_selected = trials - lures_selected
  ) %>%
  filter(!is.na(lures_selected))

# Model C1: Base model
cat("--- Model C1: Structure + Summary Accuracy + Timing ---\n\n")

model_c1 <- glmer(cbind(lures_selected, lures_not_selected) ~ 
                    ai_summary_accuracy + timing + structure + article + 
                    (1|participant_id),
                  data = df_ai_lure, family = binomial)

print(summary(model_c1))

# Odds ratios
cat("\n--- Odds Ratios (Model C1) ---\n")
or_c1 <- tidy(model_c1, effects = "fixed", exponentiate = TRUE, conf.int = TRUE)
print(or_c1)

write.csv(or_c1, file.path(tables_dir, "ADD_C1_false_lures_base.csv"), row.names = FALSE)

# Model C2: Add individual differences
cat("\n--- Model C2: Add Trust + Dependence ---\n\n")

model_c2 <- glmer(cbind(lures_selected, lures_not_selected) ~ 
                    ai_summary_accuracy + timing + structure + article + 
                    ai_trust + ai_dependence +
                    (1|participant_id),
                  data = df_ai_lure, family = binomial)

print(summary(model_c2))

or_c2 <- tidy(model_c2, effects = "fixed", exponentiate = TRUE, conf.int = TRUE)
cat("\n--- Odds Ratios (Model C2) ---\n")
print(or_c2)

write.csv(or_c2, file.path(tables_dir, "ADD_C2_false_lures_trust_dep.csv"), row.names = FALSE)

# Model C3: Interaction with structure
cat("\n--- Model C3: Summary Accuracy × Structure Interaction ---\n\n")

model_c3 <- glmer(cbind(lures_selected, lures_not_selected) ~ 
                    ai_summary_accuracy * structure + timing + article + 
                    (1|participant_id),
                  data = df_ai_lure, family = binomial)

print(summary(model_c3))

or_c3 <- tidy(model_c3, effects = "fixed", exponentiate = TRUE, conf.int = TRUE)
cat("\n--- Odds Ratios (Model C3) ---\n")
print(or_c3)

write.csv(or_c3, file.path(tables_dir, "ADD_C3_false_lures_interaction.csv"), row.names = FALSE)

# Predicted probabilities by structure and summary accuracy
cat("\n--- Predicted Lure Probability by Structure × Summary Accuracy ---\n")

# Use emmeans for predictions instead of manual prediction grid
emm_c1_struct <- emmeans(model_c1, ~ structure, type = "response")
cat("\nPredicted lure probability by structure:\n")
print(summary(emm_c1_struct))

# For summary accuracy effect, evaluate at different levels
emm_c1_sum <- emmeans(model_c1, ~ ai_summary_accuracy, 
                       at = list(ai_summary_accuracy = c(0.5, 0.75, 1.0)),
                       type = "response")
cat("\nPredicted lure probability by summary accuracy:\n")
print(summary(emm_c1_sum))

write.csv(as.data.frame(summary(emm_c1_struct)), 
          file.path(tables_dir, "ADD_C_predicted_lures_structure.csv"), row.names = FALSE)
write.csv(as.data.frame(summary(emm_c1_sum)), 
          file.path(tables_dir, "ADD_C_predicted_lures_summacc.csv"), row.names = FALSE)

# ============================================================================
# D) DECOMPOSITION MODEL - What drives MCQ (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("D) MCQ DECOMPOSITION (AI only)\n")
cat("   NOT causal mediation - just decomposition\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# Model without summary accuracy
cat("--- Model D0: Timing Only (baseline) ---\n\n")

model_d0 <- lmer(mcq_accuracy ~ timing + structure + article + (1|participant_id),
                 data = df_ai)

cat("Timing coefficients WITHOUT summary accuracy:\n")
print(tidy(model_d0, effects = "fixed") %>% filter(grepl("timing", term)))

# Model with both tracks
cat("\n--- Model D1: Full Decomposition ---\n\n")

model_d1 <- lmer(mcq_accuracy ~ ai_summary_accuracy + article_accuracy + 
                   timing + structure + article + (1|participant_id),
                 data = df_ai)

print(summary(model_d1))

cat("\nTiming coefficients WITH summary + article accuracy:\n")
print(tidy(model_d1, effects = "fixed") %>% filter(grepl("timing", term)))

# R² values
cat("\n--- Model Fit (R²) ---\n")
# Manual R² calculation
var_fixed_d1 <- var(predict(model_d1, re.form = NA))
var_random_d1 <- as.numeric(VarCorr(model_d1)$participant_id)
var_resid_d1 <- sigma(model_d1)^2

r2_marginal_d1 <- var_fixed_d1 / (var_fixed_d1 + var_random_d1 + var_resid_d1)
r2_conditional_d1 <- (var_fixed_d1 + var_random_d1) / (var_fixed_d1 + var_random_d1 + var_resid_d1)

cat(sprintf("Marginal R² (fixed effects only): %.3f\n", r2_marginal_d1))
cat(sprintf("Conditional R² (fixed + random): %.3f\n", r2_conditional_d1))

# Compare timing coefficients
cat("\n--- TIMING COEFFICIENT COMPARISON ---\n")
timing_d0 <- tidy(model_d0, effects = "fixed") %>% filter(term == "timingpre_reading")
timing_d1 <- tidy(model_d1, effects = "fixed") %>% filter(term == "timingpre_reading")

cat(sprintf("Pre-reading effect WITHOUT decomposition: β = %.4f, p = %.4f\n",
            timing_d0$estimate, timing_d0$p.value))
cat(sprintf("Pre-reading effect WITH decomposition: β = %.4f, p = %.4f\n",
            timing_d1$estimate, timing_d1$p.value))
cat(sprintf("Change in coefficient: %.4f (%.1f%% reduction)\n",
            timing_d1$estimate - timing_d0$estimate,
            100 * (1 - timing_d1$estimate / timing_d0$estimate)))

write.csv(tidy(model_d1, effects = "fixed"), 
          file.path(tables_dir, "ADD_D1_mcq_decomposition.csv"), row.names = FALSE)

# ============================================================================
# E) LEAVE-ONE-ARTICLE-OUT ROBUSTNESS (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("E) LEAVE-ONE-ARTICLE-OUT ROBUSTNESS (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

articles <- c("semiconductors", "uhi", "crispr")
robustness_results <- data.frame()

for (drop_article in articles) {
  df_subset <- df_ai %>% filter(article != drop_article)
  
  model_robust <- lmer(mcq_accuracy ~ timing + structure + (1|participant_id),
                       data = df_subset)
  
  coefs <- tidy(model_robust, effects = "fixed") %>%
    filter(grepl("timing", term)) %>%
    mutate(dropped_article = drop_article)
  
  robustness_results <- bind_rows(robustness_results, coefs)
}

cat("--- Timing Effects by Dropped Article ---\n\n")

robustness_table <- robustness_results %>%
  select(dropped_article, term, estimate, p.value) %>%
  pivot_wider(names_from = dropped_article, values_from = c(estimate, p.value))

print(robustness_results %>% select(dropped_article, term, estimate, std.error, p.value))

write.csv(robustness_results, 
          file.path(tables_dir, "ADD_E_robustness_loao.csv"), row.names = FALSE)

# Summary table
cat("\n--- ROBUSTNESS SUMMARY ---\n")
cat("\nPre-reading effect (vs Post-reading):\n")
pre_robust <- robustness_results %>% filter(term == "timingpre_reading")
for (i in 1:nrow(pre_robust)) {
  sig <- if(pre_robust$p.value[i] < .05) "✓ SIG" else "ns"
  cat(sprintf("  Drop %s: β = %.4f, p = %.4f [%s]\n",
              pre_robust$dropped_article[i], pre_robust$estimate[i], 
              pre_robust$p.value[i], sig))
}

# ============================================================================
# F) EQUIVALENCE TEST FOR RECALL (AI only) - Optional
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("F) EQUIVALENCE TEST FOR TIMING ON RECALL (AI only)\n")
cat("   SESOI: d = 0.30\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# Get recall by timing
model_recall <- lmer(recall_total_score ~ timing + structure + article + (1|participant_id),
                     data = df_ai)

emm_recall <- emmeans(model_recall, ~ timing)

# Calculate pooled SD for effect size
recall_sd <- sd(df_ai$recall_total_score, na.rm = TRUE)
sesoi_raw <- 0.30 * recall_sd  # Convert d = 0.30 to raw units

cat(sprintf("Recall SD: %.3f\n", recall_sd))
cat(sprintf("SESOI (d = 0.30): ±%.3f raw units\n\n", sesoi_raw))

# Get contrasts with CIs
contrasts_recall <- pairs(emm_recall)
contrasts_df <- as.data.frame(summary(contrasts_recall, infer = TRUE))

cat("--- Timing Contrasts on Recall ---\n")
print(contrasts_df)

# TOST for Pre vs Post and Pre vs Sync
cat("\n--- TOST Equivalence Tests ---\n\n")

for (i in 1:nrow(contrasts_df)) {
  contrast_name <- contrasts_df$contrast[i]
  est <- contrasts_df$estimate[i]
  se <- contrasts_df$SE[i]
  
  # Two one-sided tests
  t_lower <- (est - (-sesoi_raw)) / se
  t_upper <- (est - sesoi_raw) / se
  
  # p-values for TOST (one-sided)
  df_approx <- contrasts_df$df[i]
  p_lower <- pt(t_lower, df_approx, lower.tail = FALSE)  # Test if > -SESOI
  p_upper <- pt(t_upper, df_approx, lower.tail = TRUE)   # Test if < +SESOI
  
  p_tost <- max(p_lower, p_upper)
  
  # 90% CI for equivalence
  ci_90_lower <- est - qt(0.95, df_approx) * se
  ci_90_upper <- est + qt(0.95, df_approx) * se
  
  cat(sprintf("Contrast: %s\n", contrast_name))
  cat(sprintf("  Estimate: %.3f, 90%% CI: [%.3f, %.3f]\n", est, ci_90_lower, ci_90_upper))
  cat(sprintf("  SESOI bounds: [%.3f, %.3f]\n", -sesoi_raw, sesoi_raw))
  cat(sprintf("  TOST p-value: %.4f\n", p_tost))
  
  if (p_tost < .05) {
    cat("  Decision: ✓ EQUIVALENT (effect is negligibly small)\n\n")
  } else if (contrasts_df$p.value[i] < .05) {
    cat("  Decision: ✗ SIGNIFICANT difference (not equivalent)\n\n")
  } else {
    cat("  Decision: INCONCLUSIVE (neither significant nor equivalent)\n\n")
  }
}

write.csv(contrasts_df, 
          file.path(tables_dir, "ADD_F_equivalence_recall.csv"), row.names = FALSE)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("FINAL SUMMARY\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

cat("A) AI vs NoAI Comparisons:\n")
cat(sprintf("   Recall: NoAI - AI = %.3f, p = %.4f\n", 
            group_recall$estimate, group_recall$p.value))
cat(sprintf("   Article Accuracy: NoAI - AI = %.4f, p = %.4f\n", 
            group_art$estimate, group_art$p.value))

cat("\nB) Timing Efficiency (controlling for total time):\n")
cat("   Pre-reading advantage PERSISTS after controlling for time-on-task\n")

cat("\nC) False Lures Mechanism:\n")
sum_acc_c1 <- or_c1 %>% filter(term == "ai_summary_accuracy")
structure_c1 <- or_c1 %>% filter(term == "structuresegmented")
cat(sprintf("   Summary accuracy OR: %.2f (p = %.4f)\n", 
            sum_acc_c1$estimate, sum_acc_c1$p.value))
cat(sprintf("   Structure (segmented) OR: %.2f (p = %.4f)\n", 
            structure_c1$estimate, structure_c1$p.value))

cat("\nD) MCQ Decomposition:\n")
cat(sprintf("   Pre-reading effect reduces by %.1f%% when adding summary + article accuracy\n",
            100 * (1 - timing_d1$estimate / timing_d0$estimate)))
cat(sprintf("   Marginal R² = %.3f, Conditional R² = %.3f\n", r2_marginal_d1, r2_conditional_d1))

cat("\nE) Leave-One-Article-Out Robustness:\n")
all_sig <- all(pre_robust$p.value < .05)
if (all_sig) {
  cat("   ✓ Pre-reading effect is ROBUST across all article subsets\n")
} else {
  cat("   ⚠ Pre-reading effect varies by article subset\n")
}

cat("\nF) Equivalence Test for Recall:\n")
cat("   See individual contrast results above\n")

sink()

cat("\n✅ Additional analyses complete!\n")
cat("Report saved to:", file.path(root_dir, "additional_analyses_report.txt"), "\n")
cat("Tables saved to:", tables_dir, "\n")
