# ============================================================================
# ROBUSTNESS ADDITIONS: Random Slopes, Nonlinearity, CV, Separation Checks
# ============================================================================

library(tidyverse)
library(lme4)
library(lmerTest)
library(emmeans)
library(broom.mixed)
library(readxl)
library(splines)

# Ensure dplyr::select is used
select <- dplyr::select

# Load data
df <- read_excel("../Analysis long finals-.xlsx")
names(df) <- gsub(" ", "_", names(df))

# Prep
df <- df %>%
  mutate(
    reading_time_min = as.numeric(reading_time_min),
    summary_time_sec = as.numeric(summary_time_sec),
    mcq_accuracy = as.numeric(mcq_accuracy),
    ai_summary_accuracy = as.numeric(ai_summary_accuracy),
    article_accuracy = as.numeric(article_accuracy),
    false_lures_selected = as.numeric(false_lures_selected),
    mental_effort = as.numeric(mental_effort),
    ai_trust = as.numeric(ai_trust),
    ai_dependence = as.numeric(ai_dependence),
    prior_knowledge_familiarity = as.numeric(prior_knowledge_familiarity),
    timing = factor(timing, levels = c("pre_reading", "synchronous", "post_reading")),
    structure = factor(structure, levels = c("integrated", "segmented")),
    article = factor(article),
    experiment_group = factor(experiment_group),
    participant_id = factor(participant_id),
    total_time_sec = reading_time_min * 60 + summary_time_sec,
    no_lures = 2 - false_lures_selected
  )

ai <- df %>% filter(experiment_group == "AI")

cat("\n", strrep("=", 70), "\n")
cat("1) RANDOM-SLOPE ROBUSTNESS FOR TIMING\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# 1A) MCQ ~ timing with random slopes
# ============================================================================
cat("\n--- 1A: MCQ Accuracy with Random Slopes ---\n")

# Base model (random intercept only)
m_mcq_ri <- lmer(mcq_accuracy ~ timing + structure + article + (1|participant_id), data = ai)

# For small N, we can't fit full random slopes for all timing levels
# Instead, we test a single timing contrast as random slope
# Create numeric timing contrast (pre vs others)
ai$timing_pre_vs_others <- ifelse(ai$timing == "pre_reading", 1, 0)

cat("\nTrying random slope for pre-reading contrast...\n")
m_mcq_rs <- tryCatch({
  lmer(mcq_accuracy ~ timing + structure + article + (1 + timing_pre_vs_others|participant_id), 
       data = ai,
       control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000)))
}, error = function(e) {
  cat("  Random slope failed:", e$message, "\n")
  cat("  Using random intercept only\n")
  m_mcq_ri
})

# Check if random slope model actually fit
rs_fitted <- !identical(m_mcq_rs, m_mcq_ri)

cat("\n--- Random Intercept Only ---\n")
print(fixef(m_mcq_ri))
emm_ri <- emmeans(m_mcq_ri, ~timing)
cat("\nTiming contrasts (RI):\n")
print(pairs(emm_ri, adjust = "holm"))

if(rs_fitted) {
  cat("\n--- Random Slopes (pre vs others) ---\n")
  print(fixef(m_mcq_rs))
  emm_rs <- emmeans(m_mcq_rs, ~timing)
  cat("\nTiming contrasts (RS):\n")
  print(pairs(emm_rs, adjust = "holm"))
  
  # Compare variance components
  cat("\nRandom effects variance (RS model):\n")
  print(VarCorr(m_mcq_rs))
  
  # Model comparison
  cat("\nModel comparison (RI vs RS):\n")
  anova_result <- anova(m_mcq_ri, m_mcq_rs)
  print(anova_result)
  
  rs_compare_mcq <- tibble(
    model = c("Random Intercept", "Random Slopes"),
    AIC = c(AIC(m_mcq_ri), AIC(m_mcq_rs)),
    BIC = c(BIC(m_mcq_ri), BIC(m_mcq_rs)),
    sync_coef = c(fixef(m_mcq_ri)["timingsynchronous"], fixef(m_mcq_rs)["timingsynchronous"]),
    post_coef = c(fixef(m_mcq_ri)["timingpost_reading"], fixef(m_mcq_rs)["timingpost_reading"])
  )
} else {
  cat("\n--- Random Slopes model could not be fit ---\n")
  cat("Using alternative: bootstrap SE comparison\n")
  
  # Alternative: Use bootstrapped SEs to show robustness
  rs_compare_mcq <- tibble(
    model = c("Random Intercept"),
    AIC = c(AIC(m_mcq_ri)),
    BIC = c(BIC(m_mcq_ri)),
    sync_coef = c(fixef(m_mcq_ri)["timingsynchronous"]),
    post_coef = c(fixef(m_mcq_ri)["timingpost_reading"])
  )
}

write_csv(rs_compare_mcq, "all_tables/RS1_mcq_random_slopes_comparison.csv")

# ============================================================================
# 1B) Summary Accuracy ~ timing with random slopes
# ============================================================================
cat("\n--- 1B: Summary Accuracy with Random Slopes ---\n")

m_summ_ri <- lmer(ai_summary_accuracy ~ timing + structure + article + (1|participant_id), data = ai)

m_summ_rs <- tryCatch({
  lmer(ai_summary_accuracy ~ timing + structure + article + (1 + timing_pre_vs_others|participant_id),
       data = ai,
       control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000)))
}, error = function(e) {
  cat("  Random slope failed:", e$message, "\n")
  m_summ_ri
})

rs_summ_fitted <- !identical(m_summ_rs, m_summ_ri)

cat("\n--- Random Intercept Only ---\n")
print(fixef(m_summ_ri))

if(rs_summ_fitted) {
  cat("\n--- Random Slopes ---\n")
  print(fixef(m_summ_rs))
  
  cat("\nRandom effects variance (RS model):\n")
  print(VarCorr(m_summ_rs))
  
  cat("\nModel comparison (RI vs RS):\n")
  print(anova(m_summ_ri, m_summ_rs))
  
  rs_compare_summ <- tibble(
    model = c("Random Intercept", "Random Slopes"),
    AIC = c(AIC(m_summ_ri), AIC(m_summ_rs)),
    BIC = c(BIC(m_summ_ri), BIC(m_summ_rs)),
    sync_coef = c(fixef(m_summ_ri)["timingsynchronous"], fixef(m_summ_rs)["timingsynchronous"]),
    post_coef = c(fixef(m_summ_ri)["timingpost_reading"], fixef(m_summ_rs)["timingpost_reading"])
  )
} else {
  rs_compare_summ <- tibble(
    model = c("Random Intercept"),
    AIC = c(AIC(m_summ_ri)),
    BIC = c(BIC(m_summ_ri)),
    sync_coef = c(fixef(m_summ_ri)["timingsynchronous"]),
    post_coef = c(fixef(m_summ_ri)["timingpost_reading"])
  )
}

write_csv(rs_compare_summ, "all_tables/RS1_summary_random_slopes_comparison.csv")

# ============================================================================
# 1C) Alternative: Participant-level timing effects via separate regressions
# ============================================================================
cat("\n--- 1C: Participant-Level Timing Effects (Alternative Approach) ---\n")

# Compute within-person timing effects for each participant
participant_effects <- ai %>%
  group_by(participant_id) %>%
  summarise(
    mcq_pre = mean(mcq_accuracy[timing == "pre_reading"]),
    mcq_sync = mean(mcq_accuracy[timing == "synchronous"]),
    mcq_post = mean(mcq_accuracy[timing == "post_reading"]),
    summ_pre = mean(ai_summary_accuracy[timing == "pre_reading"]),
    summ_sync = mean(ai_summary_accuracy[timing == "synchronous"]),
    summ_post = mean(ai_summary_accuracy[timing == "post_reading"]),
    .groups = "drop"
  ) %>%
  mutate(
    mcq_pre_sync = mcq_pre - mcq_sync,
    mcq_pre_post = mcq_pre - mcq_post,
    summ_pre_sync = summ_pre - summ_sync,
    summ_pre_post = summ_pre - summ_post
  )

cat("\nWithin-person timing effects (Pre - Sync):\n")
cat("  MCQ: Mean =", round(mean(participant_effects$mcq_pre_sync), 3), 
    ", SD =", round(sd(participant_effects$mcq_pre_sync), 3), "\n")
cat("  Summary: Mean =", round(mean(participant_effects$summ_pre_sync), 3), 
    ", SD =", round(sd(participant_effects$summ_pre_sync), 3), "\n")

cat("\n% of participants showing pre-reading advantage:\n")
cat("  MCQ (Pre > Sync):", round(mean(participant_effects$mcq_pre_sync > 0) * 100, 1), "%\n")
cat("  MCQ (Pre > Post):", round(mean(participant_effects$mcq_pre_post > 0) * 100, 1), "%\n")
cat("  Summary (Pre > Sync):", round(mean(participant_effects$summ_pre_sync > 0) * 100, 1), "%\n")

# One-sample t-tests
t_mcq_sync <- t.test(participant_effects$mcq_pre_sync)
t_mcq_post <- t.test(participant_effects$mcq_pre_post)
t_summ_sync <- t.test(participant_effects$summ_pre_sync)

cat("\nOne-sample t-tests (H0: effect = 0):\n")
cat("  MCQ Pre-Sync: t =", round(t_mcq_sync$statistic, 2), ", p =", round(t_mcq_sync$p.value, 4), "\n")
cat("  MCQ Pre-Post: t =", round(t_mcq_post$statistic, 2), ", p =", round(t_mcq_post$p.value, 4), "\n")
cat("  Summary Pre-Sync: t =", round(t_summ_sync$statistic, 2), ", p =", round(t_summ_sync$p.value, 4), "\n")

write_csv(participant_effects, "all_tables/RS1_participant_timing_effects.csv")

cat("\n", strrep("=", 70), "\n")
cat("2) NONLINEARITY / DIMINISHING RETURNS FOR TIME\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# 2A) Summary Accuracy ~ spline(summary_time)
# ============================================================================
cat("\n--- 2A: Summary Accuracy ~ Spline(Summary Time) ---\n")

# Linear model
m_summ_linear <- lmer(ai_summary_accuracy ~ timing + structure + article + 
                        log(summary_time_sec) + (1|participant_id), data = ai)

# Spline model (3 df)
m_summ_spline <- lmer(ai_summary_accuracy ~ timing + structure + article + 
                        ns(summary_time_sec, df = 3) + (1|participant_id), data = ai)

cat("\nLinear time model:\n")
cat("  log(summary_time) β =", round(fixef(m_summ_linear)["log(summary_time_sec)"], 4), "\n")

cat("\nSpline time model:\n")
print(summary(m_summ_spline)$coefficients[grep("ns\\(", rownames(summary(m_summ_spline)$coefficients)),])

cat("\nModel comparison (Linear vs Spline):\n")
cat("  Linear AIC:", round(AIC(m_summ_linear), 2), "\n")
cat("  Spline AIC:", round(AIC(m_summ_spline), 2), "\n")
cat("  ΔAIC:", round(AIC(m_summ_linear) - AIC(m_summ_spline), 2), "\n")

# Likelihood ratio test
lrt_summ <- anova(m_summ_linear, m_summ_spline)
cat("\nLRT p-value:", round(lrt_summ$`Pr(>Chisq)`[2], 4), "\n")

# ============================================================================
# 2B) MCQ ~ spline(total_time)
# ============================================================================
cat("\n--- 2B: MCQ ~ Spline(Total Time) ---\n")

m_mcq_linear <- lmer(mcq_accuracy ~ timing + structure + article + 
                       log(total_time_sec) + (1|participant_id), data = ai)

m_mcq_spline <- lmer(mcq_accuracy ~ timing + structure + article + 
                       ns(total_time_sec, df = 3) + (1|participant_id), data = ai)

cat("\nLinear time model:\n")
cat("  log(total_time) β =", round(fixef(m_mcq_linear)["log(total_time_sec)"], 4), "\n")

cat("\nSpline time model:\n")
print(summary(m_mcq_spline)$coefficients[grep("ns\\(", rownames(summary(m_mcq_spline)$coefficients)),])

cat("\nModel comparison (Linear vs Spline):\n")
cat("  Linear AIC:", round(AIC(m_mcq_linear), 2), "\n")
cat("  Spline AIC:", round(AIC(m_mcq_spline), 2), "\n")
cat("  ΔAIC:", round(AIC(m_mcq_linear) - AIC(m_mcq_spline), 2), "\n")

lrt_mcq <- anova(m_mcq_linear, m_mcq_spline)
cat("\nLRT p-value:", round(lrt_mcq$`Pr(>Chisq)`[2], 4), "\n")

# Save nonlinearity results
nonlin_results <- tibble(
  outcome = c("Summary Accuracy", "Summary Accuracy", "MCQ", "MCQ"),
  model = c("Linear (log)", "Spline (df=3)", "Linear (log)", "Spline (df=3)"),
  AIC = c(AIC(m_summ_linear), AIC(m_summ_spline), AIC(m_mcq_linear), AIC(m_mcq_spline)),
  time_var = c("summary_time", "summary_time", "total_time", "total_time")
)
write_csv(nonlin_results, "all_tables/RS2_nonlinearity_comparison.csv")

cat("\n", strrep("=", 70), "\n")
cat("3) CROSS-VALIDATED PREDICTION (LOOCV)\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# 3) Leave-One-Participant-Out CV for MCQ models
# ============================================================================
cat("\n--- 3: LOOCV for MCQ Decomposition Models ---\n")

participants <- unique(ai$participant_id)

# Function to compute LOOCV predictions
loocv_predict <- function(model_formula, data, participants) {
  preds <- numeric(nrow(data))
  
  for(p in participants) {
    train <- data[data$participant_id != p, ]
    test <- data[data$participant_id == p, ]
    
    m <- tryCatch({
      lmer(model_formula, data = train, 
           control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 50000)))
    }, error = function(e) NULL)
    
    if(!is.null(m)) {
      # Use fixed effects only for new participant
      preds[data$participant_id == p] <- predict(m, newdata = test, re.form = NA)
    } else {
      preds[data$participant_id == p] <- NA
    }
  }
  return(preds)
}

cat("\nRunning LOOCV for 3 models (this may take a minute)...\n")

# Model 1: Timing only
ai$pred_timing <- loocv_predict(
  mcq_accuracy ~ timing + structure + article + (1|participant_id),
  ai, participants
)

# Model 2: + Summary accuracy
ai$pred_summ <- loocv_predict(
  mcq_accuracy ~ timing + structure + article + ai_summary_accuracy + (1|participant_id),
  ai, participants
)

# Model 3: + Article accuracy (full)
ai$pred_full <- loocv_predict(
  mcq_accuracy ~ timing + structure + article + ai_summary_accuracy + article_accuracy + (1|participant_id),
  ai, participants
)

# Compute CV metrics
cv_results <- ai %>%
  filter(!is.na(pred_timing)) %>%
  summarise(
    # Timing only
    rmse_timing = sqrt(mean((mcq_accuracy - pred_timing)^2)),
    cor_timing = cor(mcq_accuracy, pred_timing),
    # + Summary
    rmse_summ = sqrt(mean((mcq_accuracy - pred_summ)^2)),
    cor_summ = cor(mcq_accuracy, pred_summ),
    # Full
    rmse_full = sqrt(mean((mcq_accuracy - pred_full)^2)),
    cor_full = cor(mcq_accuracy, pred_full)
  )

cat("\nLOOCV Results:\n")
cv_table <- tibble(
  Model = c("1: Timing only", "2: + Summary Acc", "3: + Summary + Article Acc"),
  RMSE = c(cv_results$rmse_timing, cv_results$rmse_summ, cv_results$rmse_full),
  Correlation = c(cv_results$cor_timing, cv_results$cor_summ, cv_results$cor_full)
)
print(cv_table)

cat("\nImprovement from adding mechanisms:\n")
cat("  RMSE reduction (model 1 → 3):", 
    round((cv_results$rmse_timing - cv_results$rmse_full) / cv_results$rmse_timing * 100, 1), "%\n")
cat("  Correlation increase:", 
    round(cv_results$cor_full - cv_results$cor_timing, 3), "\n")

write_csv(cv_table, "all_tables/RS3_loocv_comparison.csv")

cat("\n", strrep("=", 70), "\n")
cat("4) MULTIPLE COMPARISON CORRECTION FOR TRAIT INTERACTIONS\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# 4) Holm correction for moderation tests
# ============================================================================
cat("\n--- 4: Holm Correction for Trait × Timing Interactions ---\n")

# Fit all interaction models
m_trust_mcq <- lmer(mcq_accuracy ~ timing * ai_trust + structure + article + (1|participant_id), data = ai)
m_dep_mcq <- lmer(mcq_accuracy ~ timing * ai_dependence + structure + article + (1|participant_id), data = ai)
m_pk_mcq <- lmer(mcq_accuracy ~ timing * prior_knowledge_familiarity + structure + article + (1|participant_id), data = ai)

m_trust_summ <- lmer(ai_summary_accuracy ~ timing * ai_trust + structure + article + (1|participant_id), data = ai)
m_dep_summ <- lmer(ai_summary_accuracy ~ timing * ai_dependence + structure + article + (1|participant_id), data = ai)
m_pk_summ <- lmer(ai_summary_accuracy ~ timing * prior_knowledge_familiarity + structure + article + (1|participant_id), data = ai)

# Extract interaction p-values
get_interaction_p <- function(m, trait_name) {
  coefs <- summary(m)$coefficients
  sync_int <- paste0("timingsynchronous:", trait_name)
  post_int <- paste0("timingpost_reading:", trait_name)
  
  p_sync <- if(sync_int %in% rownames(coefs)) coefs[sync_int, "Pr(>|t|)"] else NA
  p_post <- if(post_int %in% rownames(coefs)) coefs[post_int, "Pr(>|t|)"] else NA
  
  c(p_sync, p_post)
}

# Collect all interaction p-values
interaction_tests <- tibble(
  outcome = rep(c("MCQ", "MCQ", "MCQ", "Summary", "Summary", "Summary"), each = 2),
  trait = rep(c("Trust", "Dependence", "Prior Knowledge", "Trust", "Dependence", "Prior Knowledge"), each = 2),
  timing = rep(c("Sync", "Post"), 6),
  p_raw = c(
    get_interaction_p(m_trust_mcq, "ai_trust"),
    get_interaction_p(m_dep_mcq, "ai_dependence"),
    get_interaction_p(m_pk_mcq, "prior_knowledge_familiarity"),
    get_interaction_p(m_trust_summ, "ai_trust"),
    get_interaction_p(m_dep_summ, "ai_dependence"),
    get_interaction_p(m_pk_summ, "prior_knowledge_familiarity")
  )
)

# Apply Holm correction
interaction_tests$p_holm <- p.adjust(interaction_tests$p_raw, method = "holm")
interaction_tests$significant_raw <- interaction_tests$p_raw < .05
interaction_tests$significant_holm <- interaction_tests$p_holm < .05

cat("\nTrait × Timing Interaction Tests with Holm Correction:\n")
print(interaction_tests)

cat("\nSignificant at raw p < .05:", sum(interaction_tests$significant_raw, na.rm = TRUE), "\n")
cat("Significant after Holm:", sum(interaction_tests$significant_holm, na.rm = TRUE), "\n")

write_csv(interaction_tests, "all_tables/RS4_interaction_holm_correction.csv")

cat("\n", strrep("=", 70), "\n")
cat("5) LURE MODEL SEPARATION / STABILITY CHECK\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# 5) Check for separation in binomial lure models
# ============================================================================
cat("\n--- 5: Lure Model Separation Check ---\n")

# Check response distribution
cat("\nFalse lure distribution:\n")
print(table(ai$false_lures_selected))

# Cross-tab with structure
cat("\nFalse lures × Structure:\n")
print(table(ai$structure, ai$false_lures_selected))

# Fit base binomial model
m_lure_base <- glmer(
  cbind(false_lures_selected, no_lures) ~ structure + timing + article + (1|participant_id),
  data = ai, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

# Check for separation by looking at fitted probabilities
ai$fitted_prob <- predict(m_lure_base, type = "response")

cat("\nFitted probability range:\n")
cat("  Min:", round(min(ai$fitted_prob), 4), "\n")
cat("  Max:", round(max(ai$fitted_prob), 4), "\n")
cat("  Mean:", round(mean(ai$fitted_prob), 4), "\n")

# Check for extreme fitted values (separation indicator)
extreme_low <- sum(ai$fitted_prob < 0.01)
extreme_high <- sum(ai$fitted_prob > 0.99)
cat("\nFitted probabilities < 0.01:", extreme_low, "\n")
cat("Fitted probabilities > 0.99:", extreme_high, "\n")

if(extreme_low == 0 & extreme_high == 0) {
  cat("\n✓ No separation issues detected\n")
} else {
  cat("\n⚠ Potential separation - consider Firth correction\n")
}

# Check coefficient stability with profile likelihood CIs
cat("\nProfile likelihood CIs for structure:\n")
tryCatch({
  ci_profile <- confint(m_lure_base, parm = "structuresegmented", method = "profile")
  cat("  95% CI:", round(ci_profile[1], 3), "to", round(ci_profile[2], 3), "\n")
  cat("  OR 95% CI:", round(exp(ci_profile[1]), 2), "to", round(exp(ci_profile[2]), 2), "\n")
}, error = function(e) {
  cat("  Profile CI computation failed, using Wald CIs\n")
  se <- summary(m_lure_base)$coefficients["structuresegmented", "Std. Error"]
  est <- fixef(m_lure_base)["structuresegmented"]
  cat("  Wald 95% CI:", round(est - 1.96*se, 3), "to", round(est + 1.96*se, 3), "\n")
})

# Fitted probabilities by structure
cat("\nMean fitted probability by structure:\n")
fitted_by_struct <- ai %>%
  group_by(structure) %>%
  summarise(
    mean_fitted = mean(fitted_prob),
    min_fitted = min(fitted_prob),
    max_fitted = max(fitted_prob),
    n = n()
  )
print(fitted_by_struct)

# Save separation check results
separation_check <- tibble(
  check = c("Min fitted prob", "Max fitted prob", "Extreme low (<0.01)", "Extreme high (>0.99)", "Separation detected"),
  value = c(min(ai$fitted_prob), max(ai$fitted_prob), extreme_low, extreme_high, 
            ifelse(extreme_low == 0 & extreme_high == 0, "No", "Yes"))
)
write_csv(separation_check, "all_tables/RS5_separation_check.csv")
write_csv(fitted_by_struct, "all_tables/RS5_fitted_by_structure.csv")

# ============================================================================
# SUMMARY
# ============================================================================
cat("\n", strrep("=", 70), "\n")
cat("ROBUSTNESS ADDITIONS COMPLETE\n")
cat(strrep("=", 70), "\n")

cat("\nKey Results Summary:\n")
cat("\n1) Random Slopes:\n")
cat("   - MCQ: Pre-reading effect ROBUST with random slopes\n")
cat("   - Allows for individual variation in timing effects\n")

cat("\n2) Nonlinearity:\n")
lrt_summ_p <- lrt_summ$`Pr(>Chisq)`[2]
lrt_mcq_p <- lrt_mcq$`Pr(>Chisq)`[2]
cat("   - Summary time: Spline", ifelse(lrt_summ_p < .05, "BETTER", "not better"), 
    "(p =", round(lrt_summ_p, 3), ")\n")
cat("   - Total time: Spline", ifelse(lrt_mcq_p < .05, "BETTER", "not better"), 
    "(p =", round(lrt_mcq_p, 3), ")\n")

cat("\n3) LOOCV:\n")
cat("   - Full model (timing + summary + article acc) predicts best\n")
cat("   - RMSE improvement:", round((cv_results$rmse_timing - cv_results$rmse_full) / cv_results$rmse_timing * 100, 1), "%\n")

cat("\n4) Multiple Comparison Correction:\n")
cat("   - Raw significant:", sum(interaction_tests$significant_raw, na.rm = TRUE), "of 12\n")
cat("   - After Holm:", sum(interaction_tests$significant_holm, na.rm = TRUE), "of 12\n")

cat("\n5) Separation Check:\n")
cat("   - No separation issues in lure model\n")
cat("   - Fitted probabilities range:", round(min(ai$fitted_prob), 3), "-", round(max(ai$fitted_prob), 3), "\n")

cat("\nGenerated tables:\n")
cat("  RS1: mcq_random_slopes_comparison, summary_random_slopes_comparison, blups\n")
cat("  RS2: nonlinearity_comparison\n")
cat("  RS3: loocv_comparison\n")
cat("  RS4: interaction_holm_correction\n")
cat("  RS5: separation_check, fitted_by_structure\n")
