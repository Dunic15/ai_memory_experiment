# ============================================================================
# ORDERED ANALYSES - Complete Analysis Suite
# ============================================================================
# 0) Article differences
# 1) AI vs NoAI beyond MCQ
# 2) Efficiency (AI only)
# 3) False lures mechanism (binomial)
# 4) Decomposition
# 5) Recall null interpretability + TOST
# 6) Robustness checks (6A-6E)
# ============================================================================

library(tidyverse)
library(lme4)
library(lmerTest)
library(emmeans)
library(readxl)
library(broom.mixed)
library(effectsize)
library(MuMIn)

# Set working directory
setwd("/Users/duccioo/Desktop/ai_memory_experiment/final_analysis/opus")

# Create output directories
dir.create("all_tables", showWarnings = FALSE)
dir.create("all_plots", showWarnings = FALSE)

# Load data
dat <- read_excel("../Analysis long finals-.xlsx")

# Clean column names
names(dat) <- gsub(" ", "_", names(dat))
names(dat) <- tolower(names(dat))

# Ensure numeric columns
dat <- dat %>%
  mutate(
    summary_time_sec = as.numeric(summary_time_sec),
    ai_summary_accuracy = as.numeric(ai_summary_accuracy),
    reading_time_min = as.numeric(reading_time_min),
    mcq_accuracy = as.numeric(mcq_accuracy),
    recall_total_score = as.numeric(recall_total_score),
    article_accuracy = as.numeric(article_accuracy),
    false_lures_selected = as.numeric(false_lures_selected),
    ai_trust = as.numeric(ai_trust),
    ai_dependence = as.numeric(ai_dependence),
    mental_effort = as.numeric(mental_effort),
    prior_knowledge = as.numeric(prior_knowledge_familiarity)
  )

# Split data
ai_dat <- dat %>% filter(experiment_group == "AI")
noai_dat <- dat %>% filter(experiment_group == "NoAI")

# Create total_time_sec for AI group
ai_dat <- ai_dat %>%
  mutate(total_time_sec = reading_time_min * 60 + summary_time_sec)

# Set contrasts
dat$experiment_group <- factor(dat$experiment_group, levels = c("AI", "NoAI"))
dat$timing <- factor(dat$timing, levels = c("pre_reading", "synchronous", "post_reading"))
dat$structure <- factor(dat$structure, levels = c("integrated", "segmented"))
dat$article <- factor(dat$article)

ai_dat$timing <- factor(ai_dat$timing, levels = c("pre_reading", "synchronous", "post_reading"))
ai_dat$structure <- factor(ai_dat$structure, levels = c("integrated", "segmented"))
ai_dat$article <- factor(ai_dat$article)

cat("\n============================================================\n")
cat("0) ARTICLE DIFFERENCES\n")
cat("============================================================\n\n")

# --- Descriptives ---
cat("--- Descriptives by Article ---\n")
article_desc <- dat %>%
  group_by(article) %>%
  summarise(
    mcq_mean = mean(mcq_accuracy, na.rm = TRUE),
    mcq_sd = sd(mcq_accuracy, na.rm = TRUE),
    recall_mean = mean(recall_total_score, na.rm = TRUE),
    recall_sd = sd(recall_total_score, na.rm = TRUE),
    n = n()
  )
print(article_desc)
write_csv(article_desc, "all_tables/ORD_0_article_descriptives.csv")

# --- Model 0A: MCQ ~ article + group ---
cat("\n--- Model 0A: MCQ ~ article + group + (1|participant_id) ---\n")
m0a <- lmer(mcq_accuracy ~ article + experiment_group + (1|participant_id), data = dat)
print(summary(m0a))
m0a_tidy <- tidy(m0a, conf.int = TRUE)
write_csv(m0a_tidy, "all_tables/ORD_0A_mcq_article_group.csv")

# Article contrasts
emm_article <- emmeans(m0a, ~ article)
article_pairs <- pairs(emm_article, adjust = "holm")
cat("\nArticle pairwise contrasts:\n")
print(article_pairs)
write_csv(as.data.frame(article_pairs), "all_tables/ORD_0A_article_contrasts.csv")

# --- Model 0B: Group × Article interaction ---
cat("\n--- Model 0B: MCQ ~ group * article + (1|participant_id) ---\n")
m0b <- lmer(mcq_accuracy ~ experiment_group * article + (1|participant_id), data = dat)
print(summary(m0b))
m0b_tidy <- tidy(m0b, conf.int = TRUE)
write_csv(m0b_tidy, "all_tables/ORD_0B_mcq_group_x_article.csv")

# Interaction test
cat("\nGroup × Article interaction test:\n")
m0b_anova <- anova(m0b, type = 3)
print(m0b_anova)
write_csv(as.data.frame(m0b_anova), "all_tables/ORD_0B_interaction_anova.csv")

# --- Model 0C: AI-only Timing × Article (MCQ) ---
cat("\n--- Model 0C: AI-only MCQ ~ timing * article + structure + (1|participant_id) ---\n")
m0c <- lmer(mcq_accuracy ~ timing * article + structure + (1|participant_id), data = ai_dat)
print(summary(m0c))
m0c_tidy <- tidy(m0c, conf.int = TRUE)
write_csv(m0c_tidy, "all_tables/ORD_0C_ai_mcq_timing_x_article.csv")

# Timing×Article interaction test
cat("\nTiming × Article interaction test:\n")
m0c_anova <- anova(m0c, type = 3)
print(m0c_anova)
write_csv(as.data.frame(m0c_anova), "all_tables/ORD_0C_timing_x_article_anova.csv")

# --- Model 0D: AI-only Summary Accuracy ~ Timing × Article ---
cat("\n--- Model 0D: AI-only Summary Acc ~ timing * article + structure + (1|participant_id) ---\n")
m0d <- lmer(ai_summary_accuracy ~ timing * article + structure + (1|participant_id), data = ai_dat)
print(summary(m0d))
m0d_tidy <- tidy(m0d, conf.int = TRUE)
write_csv(m0d_tidy, "all_tables/ORD_0D_ai_summacc_timing_x_article.csv")

cat("\nTiming × Article interaction test (summary accuracy):\n")
m0d_anova <- anova(m0d, type = 3)
print(m0d_anova)
write_csv(as.data.frame(m0d_anova), "all_tables/ORD_0D_summacc_timing_x_article_anova.csv")


cat("\n============================================================\n")
cat("1) AI vs NoAI BEYOND MCQ\n")
cat("============================================================\n\n")

# --- Model 1A: Recall ~ group + article ---
cat("--- Model 1A: Recall ~ group + article + (1|participant_id) ---\n")
m1a <- lmer(recall_total_score ~ experiment_group + article + (1|participant_id), data = dat)
print(summary(m1a))
m1a_tidy <- tidy(m1a, conf.int = TRUE)
write_csv(m1a_tidy, "all_tables/ORD_1A_recall_group.csv")

# Group EMMs
emm_recall <- emmeans(m1a, ~ experiment_group)
recall_contrast <- pairs(emm_recall)
cat("\nGroup contrast on recall:\n")
print(emm_recall)
print(recall_contrast)
write_csv(as.data.frame(emm_recall), "all_tables/ORD_1A_recall_emms.csv")
write_csv(as.data.frame(recall_contrast), "all_tables/ORD_1A_recall_contrast.csv")

# --- Model 1B: Article Accuracy ~ group + article ---
cat("\n--- Model 1B: Article Accuracy ~ group + article + (1|participant_id) ---\n")
m1b <- lmer(article_accuracy ~ experiment_group + article + (1|participant_id), data = dat)
print(summary(m1b))
m1b_tidy <- tidy(m1b, conf.int = TRUE)
write_csv(m1b_tidy, "all_tables/ORD_1B_articleacc_group.csv")

# Group EMMs
emm_artacc <- emmeans(m1b, ~ experiment_group)
artacc_contrast <- pairs(emm_artacc)
cat("\nGroup contrast on article accuracy:\n")
print(emm_artacc)
print(artacc_contrast)
write_csv(as.data.frame(emm_artacc), "all_tables/ORD_1B_articleacc_emms.csv")
write_csv(as.data.frame(artacc_contrast), "all_tables/ORD_1B_articleacc_contrast.csv")


cat("\n============================================================\n")
cat("2) EFFICIENCY (AI ONLY) - Controlling for Total Time\n")
cat("============================================================\n\n")

# Descriptives for total time by timing
cat("--- Total Time by Timing Condition ---\n")
time_desc <- ai_dat %>%
  group_by(timing) %>%
  summarise(
    mean_total_time = mean(total_time_sec, na.rm = TRUE),
    sd_total_time = sd(total_time_sec, na.rm = TRUE),
    n = n()
  )
print(time_desc)
write_csv(time_desc, "all_tables/ORD_2_total_time_descriptives.csv")

# --- Model 2: MCQ ~ timing + structure + total_time + article ---
cat("\n--- Model 2: MCQ ~ timing + structure + total_time_sec + article + (1|participant_id) ---\n")
m2 <- lmer(mcq_accuracy ~ timing + structure + total_time_sec + article + (1|participant_id), 
           data = ai_dat)
print(summary(m2))
m2_tidy <- tidy(m2, conf.int = TRUE)
write_csv(m2_tidy, "all_tables/ORD_2_mcq_efficiency.csv")

# Timing contrasts (Holm corrected)
emm_timing <- emmeans(m2, ~ timing)
timing_pairs <- pairs(emm_timing, adjust = "holm")
cat("\nTiming contrasts (Holm-corrected):\n")
print(emm_timing)
print(timing_pairs)
write_csv(as.data.frame(emm_timing), "all_tables/ORD_2_timing_emms.csv")
write_csv(as.data.frame(timing_pairs), "all_tables/ORD_2_timing_contrasts.csv")

# Effect sizes for timing
sigma_res <- sigma(m2)
timing_df <- as.data.frame(timing_pairs)
timing_df$d <- timing_df$estimate / sigma_res
cat("\nEffect sizes (d):\n")
print(timing_df[, c("contrast", "estimate", "d", "p.value")])
write_csv(timing_df, "all_tables/ORD_2_timing_contrasts_with_d.csv")


cat("\n============================================================\n")
cat("3) FALSE LURES MECHANISM (AI ONLY) - Binomial Models\n")
cat("============================================================\n\n")

# Create success/failure columns for binomial
ai_dat <- ai_dat %>%
  mutate(
    lures = false_lures_selected,
    no_lures = 2 - false_lures_selected
  )

# --- Model 3A: Base binomial model ---
cat("--- Model 3A: Binomial Base Model ---\n")
cat("cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + (1|participant_id)\n\n")

m3a <- glmer(cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + 
               (1|participant_id), 
             data = ai_dat, family = binomial)
print(summary(m3a))
m3a_tidy <- tidy(m3a, conf.int = TRUE, exponentiate = TRUE)
names(m3a_tidy)[names(m3a_tidy) == "estimate"] <- "OR"
write_csv(m3a_tidy, "all_tables/ORD_3A_lures_binomial_base.csv")
cat("\nOdds Ratios:\n")
print(m3a_tidy[, c("term", "OR", "conf.low", "conf.high", "p.value")])

# --- Model 3B: Add trust + dependence ---
cat("\n--- Model 3B: Adding Trust + Dependence ---\n")
m3b <- glmer(cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + 
               ai_trust + ai_dependence + (1|participant_id), 
             data = ai_dat, family = binomial)
print(summary(m3b))
m3b_tidy <- tidy(m3b, conf.int = TRUE, exponentiate = TRUE)
names(m3b_tidy)[names(m3b_tidy) == "estimate"] <- "OR"
write_csv(m3b_tidy, "all_tables/ORD_3B_lures_binomial_trust_dep.csv")
cat("\nOdds Ratios with Trust/Dependence:\n")
print(m3b_tidy[, c("term", "OR", "conf.low", "conf.high", "p.value")])

# --- Model 3C: Summary Accuracy × Structure interaction ---
cat("\n--- Model 3C: Summary Accuracy × Structure Interaction ---\n")
m3c <- glmer(cbind(lures, no_lures) ~ ai_summary_accuracy * structure + timing + article + 
               (1|participant_id), 
             data = ai_dat, family = binomial)
print(summary(m3c))
m3c_tidy <- tidy(m3c, conf.int = TRUE, exponentiate = TRUE)
names(m3c_tidy)[names(m3c_tidy) == "estimate"] <- "OR"
write_csv(m3c_tidy, "all_tables/ORD_3C_lures_binomial_interaction.csv")
cat("\nInteraction model ORs:\n")
print(m3c_tidy[, c("term", "OR", "conf.low", "conf.high", "p.value")])

# Predicted probabilities by structure
emm_struct <- emmeans(m3a, ~ structure, type = "response")
cat("\nPredicted lure probability by structure:\n")
print(emm_struct)
write_csv(as.data.frame(emm_struct), "all_tables/ORD_3_predicted_lure_prob.csv")


cat("\n============================================================\n")
cat("4) DECOMPOSITION (AI ONLY)\n")
cat("============================================================\n\n")

# --- Model 4A: Timing only (baseline) ---
cat("--- Model 4A: Timing Only ---\n")
m4a <- lmer(mcq_accuracy ~ timing + structure + article + (1|participant_id), data = ai_dat)
print(summary(m4a))
m4a_tidy <- tidy(m4a, conf.int = TRUE)
write_csv(m4a_tidy, "all_tables/ORD_4A_timing_only.csv")

# --- Model 4B: Full decomposition ---
cat("\n--- Model 4B: Full Decomposition ---\n")
cat("mcq_accuracy ~ ai_summary_accuracy + article_accuracy + timing + structure + article + (1|participant_id)\n\n")
m4b <- lmer(mcq_accuracy ~ ai_summary_accuracy + article_accuracy + timing + structure + article + 
              (1|participant_id), data = ai_dat)
print(summary(m4b))
m4b_tidy <- tidy(m4b, conf.int = TRUE)
write_csv(m4b_tidy, "all_tables/ORD_4B_full_decomposition.csv")

# R-squared
r2_4b <- r.squaredGLMM(m4b)
cat("\nModel R-squared:\n")
cat("  Marginal R² =", round(r2_4b[1], 3), "\n")
cat("  Conditional R² =", round(r2_4b[2], 3), "\n")

# Coefficient change
# Note: We want the *intercept* difference between timing conditions, not the coefficient
# In the current parameterization, pre_reading is the reference level (coefficient = 0)
# So we look at synchronous and post_reading coefficients

# Base model: get timing coefficients
timing_sync_base <- m4a_tidy %>% filter(term == "timingsynchronous") %>% pull(estimate)
timing_post_base <- m4a_tidy %>% filter(term == "timingpost_reading") %>% pull(estimate)

# Full model: get timing coefficients
timing_sync_full <- m4b_tidy %>% filter(term == "timingsynchronous") %>% pull(estimate)
timing_post_full <- m4b_tidy %>% filter(term == "timingpost_reading") %>% pull(estimate)

# Calculate reduction
sync_change_pct <- (abs(timing_sync_base) - abs(timing_sync_full)) / abs(timing_sync_base) * 100
post_change_pct <- (abs(timing_post_base) - abs(timing_post_full)) / abs(timing_post_base) * 100

cat("\n--- Coefficient Change Summary ---\n")
cat("Synchronous β (timing only):", round(timing_sync_base, 3), "\n")
cat("Synchronous β (full model):", round(timing_sync_full, 3), "\n")
cat("Synchronous change:", round(sync_change_pct, 1), "% reduction\n\n")
cat("Post-reading β (timing only):", round(timing_post_base, 3), "\n")
cat("Post-reading β (full model):", round(timing_post_full, 3), "\n")
cat("Post-reading change:", round(post_change_pct, 1), "% reduction\n")

decomp_summary <- data.frame(
  Model = c("Timing only", "Full decomposition"),
  synchronous_beta = c(timing_sync_base, timing_sync_full),
  post_reading_beta = c(timing_post_base, timing_post_full),
  avg_change_pct = c(NA, mean(c(sync_change_pct, post_change_pct)))
)
write_csv(decomp_summary, "all_tables/ORD_4_decomposition_summary.csv")


cat("\n============================================================\n")
cat("5) RECALL NULL INTERPRETABILITY (AI ONLY) + TOST\n")
cat("============================================================\n\n")

# --- Final recall model ---
cat("--- Model 5: Recall ~ timing + structure + article + (1|participant_id) ---\n")
m5 <- lmer(recall_total_score ~ timing + structure + article + (1|participant_id), data = ai_dat)
print(summary(m5))
m5_tidy <- tidy(m5, conf.int = TRUE)
write_csv(m5_tidy, "all_tables/ORD_5_recall_final.csv")

# Timing EMMs
emm_recall_timing <- emmeans(m5, ~ timing)
recall_timing_pairs <- pairs(emm_recall_timing, adjust = "holm")
cat("\nTiming effects on recall:\n")
print(emm_recall_timing)
print(recall_timing_pairs)
write_csv(as.data.frame(emm_recall_timing), "all_tables/ORD_5_recall_timing_emms.csv")
write_csv(as.data.frame(recall_timing_pairs), "all_tables/ORD_5_recall_timing_contrasts.csv")

# --- TOST Equivalence Test ---
cat("\n--- TOST Equivalence Tests for Timing on Recall ---\n")
cat("SESOI: d = 0.30\n\n")

# Calculate SESOI in raw units
recall_sd <- sd(ai_dat$recall_total_score, na.rm = TRUE)
sesoi <- 0.30 * recall_sd
cat("Recall SD:", round(recall_sd, 2), "\n")
cat("SESOI (raw):", round(sesoi, 2), "\n\n")

# Get timing contrasts with 90% CI for TOST
recall_timing_90ci <- confint(recall_timing_pairs, level = 0.90)
recall_timing_df <- as.data.frame(recall_timing_90ci)

# TOST decisions using the 90% CI approach
# If the 90% CI is entirely within [-SESOI, +SESOI], then equivalent
tost_results <- recall_timing_df %>%
  mutate(
    lower_bound = -sesoi,
    upper_bound = sesoi,
    within_bounds = (lower.CL > -sesoi) & (upper.CL < sesoi),
    # Calculate TOST p-value as max of two one-sided tests
    t_lower = (estimate - (-sesoi)) / SE,
    t_upper = (sesoi - estimate) / SE,
    tost_p_lower = pt(t_lower, df = df, lower.tail = FALSE),
    tost_p_upper = pt(t_upper, df = df, lower.tail = FALSE),
    tost_p = pmax(tost_p_lower, tost_p_upper),
    equivalent = tost_p < 0.05
  )

cat("TOST Results:\n")
print(tost_results[, c("contrast", "estimate", "lower.CL", "upper.CL", "tost_p", "equivalent")])
write_csv(tost_results, "all_tables/ORD_5_recall_tost.csv")


cat("\n============================================================\n")
cat("6) ROBUSTNESS CHECKS\n")
cat("============================================================\n\n")

# -------------------------------------------------------------------------
# 6A) Leave-One-Article-Out
# -------------------------------------------------------------------------
cat("--- 6A: Leave-One-Article-Out Robustness ---\n\n")

articles <- c("semiconductors", "uhi", "crispr")
loao_results <- list()

for (art in articles) {
  cat("Dropping:", art, "\n")
  ai_sub <- ai_dat %>% filter(article != art)
  
  # Re-run Model 2 (Efficiency) - use emmeans for timing contrasts
  m2_sub <- lmer(mcq_accuracy ~ timing + structure + total_time_sec + article + (1|participant_id), 
                 data = ai_sub)
  emm_sub <- emmeans(m2_sub, ~ timing)
  pairs_sub <- as.data.frame(pairs(emm_sub))
  # Get pre-reading vs synchronous contrast
  pre_sync <- pairs_sub %>% filter(grepl("pre_reading - synchronous", contrast))
  
  loao_results[[art]] <- data.frame(
    dropped_article = art,
    pre_vs_sync_estimate = pre_sync$estimate[1],
    pre_vs_sync_se = pre_sync$SE[1],
    pre_vs_sync_p = pre_sync$p.value[1]
  )
  
  # Re-run Model 3A (Lures)
  m3_sub <- tryCatch({
    glmer(cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + 
            (1|participant_id), data = ai_sub, family = binomial)
  }, error = function(e) NULL)
  
  if (!is.null(m3_sub)) {
    struct_coef <- tidy(m3_sub, exponentiate = TRUE) %>% filter(term == "structuresegmented")
    if (nrow(struct_coef) > 0) {
      loao_results[[art]]$structure_OR <- struct_coef$estimate[1]
      loao_results[[art]]$structure_p <- struct_coef$p.value[1]
    }
  }
}

loao_df <- bind_rows(loao_results)
print(loao_df)
write_csv(loao_df, "all_tables/ORD_6A_leave_one_article_out.csv")

# -------------------------------------------------------------------------
# 6B) Random-Effects Sensitivity
# -------------------------------------------------------------------------
cat("\n--- 6B: Random-Effects Sensitivity ---\n\n")

# Helper function to get pre-sync contrast
get_pre_sync_contrast <- function(model) {
  emm <- emmeans(model, ~ timing)
  pairs_df <- as.data.frame(pairs(emm))
  pre_sync <- pairs_df %>% filter(grepl("pre_reading - synchronous", contrast))
  return(list(estimate = pre_sync$estimate[1], p = pre_sync$p.value[1]))
}

# Model with (1|participant_id) + (1|article)
cat("Model with (1|participant_id) + (1|article):\n")
m2_re2 <- tryCatch({
  lmer(mcq_accuracy ~ timing + structure + total_time_sec + (1|participant_id) + (1|article), 
       data = ai_dat)
}, error = function(e) {
  cat("  Error:", e$message, "\n")
  NULL
})
re2_result <- if (!is.null(m2_re2)) get_pre_sync_contrast(m2_re2) else list(estimate = NA, p = NA)
cat("  Pre-Sync Δ =", round(re2_result$estimate, 3), ", p =", round(re2_result$p, 4), "\n")

# Model with (1|participant_id) only
cat("\nModel with (1|participant_id) only:\n")
m2_re1 <- lmer(mcq_accuracy ~ timing + structure + total_time_sec + (1|participant_id), 
               data = ai_dat)
re1_result <- get_pre_sync_contrast(m2_re1)
cat("  Pre-Sync Δ =", round(re1_result$estimate, 3), ", p =", round(re1_result$p, 4), "\n")

# Model with article as fixed effect (this is model m2)
cat("\nModel with article as fixed effect:\n")
fixed_result <- get_pre_sync_contrast(m2)
cat("  Pre-Sync Δ =", round(fixed_result$estimate, 3), ", p =", round(fixed_result$p, 4), "\n")

re_sensitivity <- data.frame(
  model = c("(1|participant) + (1|article)", "(1|participant) only", "+ article fixed effect"),
  pre_sync_estimate = c(re2_result$estimate, re1_result$estimate, fixed_result$estimate),
  pre_sync_p = c(re2_result$p, re1_result$p, fixed_result$p)
)
print(re_sensitivity)
write_csv(re_sensitivity, "all_tables/ORD_6B_random_effects_sensitivity.csv")

# -------------------------------------------------------------------------
# 6C) False-Lure Overdispersion Check
# -------------------------------------------------------------------------
cat("\n--- 6C: False-Lure Overdispersion Check ---\n\n")

# Calculate overdispersion
resid_pearson <- residuals(m3a, type = "pearson")
n_obs <- nrow(ai_dat)
n_params <- length(fixef(m3a)) + 1  # fixed effects + 1 random effect variance
overdispersion <- sum(resid_pearson^2) / (n_obs - n_params)
cat("Overdispersion ratio:", round(overdispersion, 2), "\n")

if (overdispersion > 1.5) {
  cat("⚠️ Overdispersion detected! Fitting model with observation-level RE.\n\n")
  
  ai_dat$obs_id <- 1:nrow(ai_dat)
  m3a_olre <- tryCatch({
    glmer(cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + 
            (1|participant_id) + (1|obs_id), 
          data = ai_dat, family = binomial)
  }, error = function(e) NULL)
  
  if (!is.null(m3a_olre)) {
    cat("OLRE model fitted:\n")
    struct_olre <- tidy(m3a_olre, exponentiate = TRUE) %>% filter(term == "structuresegmented")
    cat("  Structure OR =", round(struct_olre$estimate, 2), 
        ", p =", round(struct_olre$p.value, 4), "\n")
    cat("  ✓ Structure effect remains", ifelse(struct_olre$p.value < 0.05, "significant", "non-significant"), "\n")
  }
} else {
  cat("✓ No substantial overdispersion (ratio < 1.5)\n")
}

overdispersion_result <- data.frame(
  overdispersion_ratio = overdispersion,
  threshold = 1.5,
  overdispersed = overdispersion > 1.5
)
write_csv(overdispersion_result, "all_tables/ORD_6C_overdispersion_check.csv")

# -------------------------------------------------------------------------
# 6D) Time-Cap Sensitivity
# -------------------------------------------------------------------------
cat("\n--- 6D: Time-Cap Sensitivity ---\n\n")

# Flag reading times near cap (≥ 14.9 if capped at 15)
time_cap <- 14.9
ai_dat <- ai_dat %>%
  mutate(near_cap = reading_time_min >= time_cap)

n_capped <- sum(ai_dat$near_cap, na.rm = TRUE)
cat("Trials with reading_time_min ≥", time_cap, ":", n_capped, "\n")

if (n_capped > 0) {
  cat("Participants with capped trials:\n")
  capped_info <- ai_dat %>% 
    filter(near_cap) %>% 
    select(participant_id, article, timing, reading_time_min)
  print(capped_info)
  
  # Re-run key model excluding capped
  ai_nocap <- ai_dat %>% filter(!near_cap)
  m2_nocap <- lmer(mcq_accuracy ~ timing + structure + total_time_sec + article + (1|participant_id), 
                   data = ai_nocap)
  nocap_result <- get_pre_sync_contrast(m2_nocap)
  cat("\nExcluding capped trials:\n")
  cat("  Pre-Sync Δ =", round(nocap_result$estimate, 3), ", p =", round(nocap_result$p, 4), "\n")
  
  time_cap_result <- data.frame(
    n_capped = n_capped,
    original_estimate = fixed_result$estimate,
    original_p = fixed_result$p,
    nocap_estimate = nocap_result$estimate,
    nocap_p = nocap_result$p
  )
} else {
  cat("✓ No trials at time cap.\n")
  time_cap_result <- data.frame(n_capped = 0, note = "No trials at cap")
}
print(time_cap_result)
write_csv(time_cap_result, "all_tables/ORD_6D_time_cap_sensitivity.csv")

# -------------------------------------------------------------------------
# 6E) Leave-One-Participant-Out Influence
# -------------------------------------------------------------------------
cat("\n--- 6E: Leave-One-Participant-Out Influence ---\n\n")

# For structure → false lures
cat("Structure effect on false lures (leave-one-participant-out):\n")
participants <- unique(ai_dat$participant_id)
lopo_struct <- data.frame(
  dropped_participant = character(),
  structure_OR = numeric(),
  structure_p = numeric()
)

for (pid in participants) {
  ai_sub <- ai_dat %>% filter(participant_id != pid)
  m_sub <- tryCatch({
    glmer(cbind(lures, no_lures) ~ ai_summary_accuracy + timing + structure + article + 
            (1|participant_id), data = ai_sub, family = binomial)
  }, error = function(e) NULL)
  
  if (!is.null(m_sub)) {
    struct_coef <- tidy(m_sub, exponentiate = TRUE) %>% filter(term == "structuresegmented")
    lopo_struct <- rbind(lopo_struct, data.frame(
      dropped_participant = pid,
      structure_OR = struct_coef$estimate,
      structure_p = struct_coef$p.value
    ))
  }
}

cat("  OR range:", round(min(lopo_struct$structure_OR), 2), "-", 
    round(max(lopo_struct$structure_OR), 2), "\n")
cat("  All p <", round(max(lopo_struct$structure_p), 3), "\n")
write_csv(lopo_struct, "all_tables/ORD_6E_lopo_structure_lures.csv")

# For AI vs NoAI MCQ
cat("\nAI vs NoAI MCQ effect (leave-one-participant-out):\n")
lopo_group <- data.frame(
  dropped_participant = character(),
  group_beta = numeric(),
  group_p = numeric()
)

all_participants <- unique(dat$participant_id)
for (pid in all_participants) {
  dat_sub <- dat %>% filter(participant_id != pid)
  m_sub <- tryCatch({
    lmer(mcq_accuracy ~ experiment_group + article + (1|participant_id), data = dat_sub)
  }, error = function(e) NULL)
  
  if (!is.null(m_sub)) {
    group_coef <- tidy(m_sub) %>% filter(term == "experiment_groupNoAI")
    lopo_group <- rbind(lopo_group, data.frame(
      dropped_participant = pid,
      group_beta = group_coef$estimate,
      group_p = group_coef$p.value
    ))
  }
}

cat("  β range:", round(min(lopo_group$group_beta), 3), "-", 
    round(max(lopo_group$group_beta), 3), "\n")
write_csv(lopo_group, "all_tables/ORD_6E_lopo_group_mcq.csv")


cat("\n============================================================\n")
cat("GENERATING PLOTS\n")
cat("============================================================\n\n")

# -------------------------------------------------------------------------
# Plot 1: MCQ by Timing (AI only), adjusted for total_time
# -------------------------------------------------------------------------
cat("--- Plot 1: MCQ by Timing (adjusted for total time) ---\n")

emm_plot1 <- emmeans(m2, ~ timing)
emm_plot1_df <- as.data.frame(emm_plot1)
names(emm_plot1_df)[names(emm_plot1_df) == "emmean"] <- "MCQ"

p1 <- ggplot(emm_plot1_df, aes(x = timing, y = MCQ)) +
  geom_point(size = 4) +
  geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL), width = 0.2) +
  scale_x_discrete(labels = c("Pre-reading", "Synchronous", "Post-reading")) +
  labs(
    title = "MCQ Accuracy by Timing Condition (AI only)",
    subtitle = "Adjusted for total time, structure, and article",
    x = "Timing Condition",
    y = "Estimated MCQ Accuracy"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  ) +
  ylim(0.4, 0.8)

ggsave("all_plots/ORD_plot1_mcq_by_timing.png", p1, width = 8, height = 6, dpi = 300)
cat("  Saved: all_plots/ORD_plot1_mcq_by_timing.png\n")

# -------------------------------------------------------------------------
# Plot 2: Predicted lure probability vs summary accuracy by structure
# -------------------------------------------------------------------------
cat("\n--- Plot 2: Lure probability vs summary accuracy by structure ---\n")

# Create prediction data
pred_grid <- expand.grid(
  ai_summary_accuracy = seq(0.3, 1, by = 0.05),
  structure = c("integrated", "segmented"),
  timing = "pre_reading",
  article = "crispr"
)
pred_grid$structure <- factor(pred_grid$structure, levels = c("integrated", "segmented"))
pred_grid$timing <- factor(pred_grid$timing, levels = levels(ai_dat$timing))
pred_grid$article <- factor(pred_grid$article, levels = levels(ai_dat$article))

# Predictions from base model (m3a)
pred_grid$pred_prob <- predict(m3a, newdata = pred_grid, type = "response", re.form = NA)

p2 <- ggplot(pred_grid, aes(x = ai_summary_accuracy, y = pred_prob, color = structure)) +
  geom_line(size = 1.2) +
  geom_point(data = ai_dat, aes(x = ai_summary_accuracy, y = lures/2, color = structure), 
             alpha = 0.4, size = 2, position = position_jitter(width = 0.02, height = 0.05)) +
  scale_color_manual(values = c("integrated" = "#2E86AB", "segmented" = "#E94F37"),
                     labels = c("Integrated", "Segmented")) +
  labs(
    title = "Predicted False Lure Probability by Summary Accuracy",
    subtitle = "Points show raw data (jittered); lines show model predictions",
    x = "AI Summary Accuracy",
    y = "Probability of Selecting a Lure",
    color = "Structure"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold"),
    legend.position = "bottom"
  ) +
  ylim(0, 1)

ggsave("all_plots/ORD_plot2_lure_prob_by_structure.png", p2, width = 8, height = 6, dpi = 300)
cat("  Saved: all_plots/ORD_plot2_lure_prob_by_structure.png\n")

# -------------------------------------------------------------------------
# Plot 3: Article means (MCQ) showing difficulty difference
# -------------------------------------------------------------------------
cat("\n--- Plot 3: Article difficulty (MCQ means) ---\n")

emm_article_plot <- emmeans(m0a, ~ article)
emm_article_df <- as.data.frame(emm_article_plot)
names(emm_article_df)[names(emm_article_df) == "emmean"] <- "MCQ"

# Reorder by difficulty
emm_article_df <- emm_article_df %>%
  mutate(article = fct_reorder(article, MCQ))

p3 <- ggplot(emm_article_df, aes(x = article, y = MCQ)) +
  geom_point(size = 5, color = "#2E86AB") +
  geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL), width = 0.15, size = 1) +
  geom_hline(yintercept = mean(emm_article_df$MCQ), linetype = "dashed", color = "gray50") +
  scale_x_discrete(labels = c("Semiconductors\n(Hardest)", "UHI\n(Moderate)", "CRISPR\n(Easiest)")) +
  labs(
    title = "Article Difficulty: MCQ Accuracy by Article",
    subtitle = "Dashed line = overall mean; error bars = 95% CI",
    x = "Article",
    y = "Estimated MCQ Accuracy"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  ) +
  ylim(0.4, 0.75)

ggsave("all_plots/ORD_plot3_article_difficulty.png", p3, width = 8, height = 6, dpi = 300)
cat("  Saved: all_plots/ORD_plot3_article_difficulty.png\n")


cat("\n============================================================\n")
cat("SUMMARY COMPLETE\n")
cat("============================================================\n\n")

# Count outputs
n_tables <- length(list.files("all_tables", pattern = "ORD_.*\\.csv"))
cat("Generated", n_tables, "new tables (ORD_*.csv)\n")
cat("Generated 3 new plots (ORD_plot*.png)\n")
cat("\nAll outputs saved to all_tables/ and all_plots/\n")
