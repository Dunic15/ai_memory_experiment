# ============================================================================
# TIMING PROCESS CHAIN + FALSE LURES FINAL ANALYSES
# ============================================================================

library(tidyverse)
library(lme4)
library(lmerTest)
library(emmeans)
library(broom.mixed)
library(readxl)
library(MASS)  # for ordinal - load before dplyr to avoid select conflict

# Ensure dplyr::select is used
select <- dplyr::select

# Load data
df <- read_excel("../Analysis long finals-.xlsx")
names(df) <- gsub(" ", "_", names(df))

# Prep
df <- df %>%
  mutate(
    # Ensure numeric
    reading_time_min = as.numeric(reading_time_min),
    summary_time_sec = as.numeric(summary_time_sec),
    mcq_accuracy = as.numeric(mcq_accuracy),
    ai_summary_accuracy = as.numeric(ai_summary_accuracy),
    article_accuracy = as.numeric(article_accuracy),
    false_lures_selected = as.numeric(false_lures_selected),
    recall_total_score = as.numeric(recall_total_score),
    mental_effort = as.numeric(mental_effort),
    ai_trust = as.numeric(ai_trust),
    ai_dependence = as.numeric(ai_dependence),
    prior_knowledge_familiarity = as.numeric(prior_knowledge_familiarity),
    # Factors
    timing = factor(timing, levels = c("pre_reading", "synchronous", "post_reading")),
    structure = factor(structure, levels = c("integrated", "segmented")),
    article = factor(article),
    experiment_group = factor(experiment_group),
    participant_id = factor(participant_id),
    # Derived
    total_time_sec = reading_time_min * 60 + summary_time_sec,
    no_lures = 2 - false_lures_selected
  )

ai <- df %>% filter(experiment_group == "AI")

cat("\n", strrep("=", 70), "\n")
cat("TIMING PROCESS CHAIN ANALYSES\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# T1) SANITY CHECK: Trust/Dependence ~ Timing (should be ns)
# ============================================================================
cat("\n--- T1: SANITY CHECK - Trust/Dependence Balance ---\n")

# Trust ~ timing + structure
m_trust <- lmer(ai_trust ~ timing + structure + (1|participant_id), data = ai)
cat("\nai_trust ~ timing + structure:\n")
print(summary(m_trust)$coefficients)

# ANOVA for timing effect
cat("\nTiming effect on Trust (ANOVA):\n")
print(anova(m_trust))

# Dependence ~ timing + structure  
m_dep <- lmer(ai_dependence ~ timing + structure + (1|participant_id), data = ai)
cat("\nai_dependence ~ timing + structure:\n")
print(summary(m_dep)$coefficients)

cat("\nTiming effect on Dependence (ANOVA):\n")
print(anova(m_dep))

# Save
write_csv(tidy(m_trust), "all_tables/T1_trust_by_timing.csv")
write_csv(tidy(m_dep), "all_tables/T1_dependence_by_timing.csv")

# Descriptives by timing
trust_desc <- ai %>%
  group_by(timing) %>%
  summarise(
    trust_mean = mean(ai_trust, na.rm = TRUE),
    trust_sd = sd(ai_trust, na.rm = TRUE),
    dep_mean = mean(ai_dependence, na.rm = TRUE),
    dep_sd = sd(ai_dependence, na.rm = TRUE),
    n = n()
  )
cat("\nTrust/Dependence descriptives by timing:\n")
print(trust_desc)
write_csv(trust_desc, "all_tables/T1_trust_dep_descriptives.csv")

# ============================================================================
# T2) TIMING → SUMMARY ACCURACY via TIME ("Buffer" Mechanism)
# ============================================================================
cat("\n--- T2: Summary Accuracy Decomposition ---\n")

# Base model: just timing
m_summ_base <- lmer(ai_summary_accuracy ~ timing + structure + article + (1|participant_id), data = ai)
cat("\nBase model (timing only):\n")
print(fixef(m_summ_base))

# With summary time
m_summ_time <- lmer(ai_summary_accuracy ~ timing + structure + log(summary_time_sec) + article + (1|participant_id), data = ai)
cat("\n+ log(summary_time_sec):\n")
print(summary(m_summ_time)$coefficients)

# Compare timing coefficients
base_coefs <- fixef(m_summ_base)
time_coefs <- fixef(m_summ_time)

cat("\nTiming coefficient change:\n")
cat("Pre-reading (base):     reference\n")
cat("Synchronous (base):    ", round(base_coefs["timingsynchronous"], 4), "\n")
cat("Synchronous (+time):   ", round(time_coefs["timingsynchronous"], 4), "\n")
cat("Post-reading (base):   ", round(base_coefs["timingpost_reading"], 4), "\n")
cat("Post-reading (+time):  ", round(time_coefs["timingpost_reading"], 4), "\n")

# Timing contrasts with emmeans
emm_base <- emmeans(m_summ_base, ~timing)
emm_time <- emmeans(m_summ_time, ~timing)

cat("\nTiming EMMs (base model):\n")
print(pairs(emm_base, adjust = "holm"))

cat("\nTiming EMMs (+ summary time):\n")
print(pairs(emm_time, adjust = "holm"))

# Does timing remain significant after controlling summary time?
cat("\nANOVA - Timing effect after controlling summary time:\n")
print(anova(m_summ_time))

write_csv(tidy(m_summ_time), "all_tables/T2_summary_acc_with_time.csv")
write_csv(as.data.frame(pairs(emm_time, adjust = "holm")), "all_tables/T2_summary_acc_timing_contrasts.csv")

# ============================================================================
# T3) FINAL MCQ DECOMPOSITION (Timing + Time + Quality)
# ============================================================================
cat("\n--- T3: Final MCQ Decomposition ---\n")

# Progressive models
m_mcq_1 <- lmer(mcq_accuracy ~ timing + structure + article + (1|participant_id), data = ai)
m_mcq_2 <- lmer(mcq_accuracy ~ timing + structure + log(total_time_sec) + article + (1|participant_id), data = ai)
m_mcq_3 <- lmer(mcq_accuracy ~ timing + structure + ai_summary_accuracy + article + (1|participant_id), data = ai)
m_mcq_4 <- lmer(mcq_accuracy ~ timing + structure + ai_summary_accuracy + article_accuracy + article + (1|participant_id), data = ai)
m_mcq_5 <- lmer(mcq_accuracy ~ timing + structure + ai_summary_accuracy + article_accuracy + log(total_time_sec) + article + (1|participant_id), data = ai)

# Extract timing coefficients
get_timing_coefs <- function(m) {
  coefs <- fixef(m)
  sync_val <- if("timingsynchronous" %in% names(coefs)) coefs["timingsynchronous"] else NA
  post_val <- if("timingpost_reading" %in% names(coefs)) coefs["timingpost_reading"] else NA
  c(sync = sync_val, post = post_val)
}

decomp <- tibble(
  model = c("1: timing only", "2: + total_time", "3: + summary_acc", "4: + article_acc", "5: full"),
  sync_beta = c(
    get_timing_coefs(m_mcq_1)[1],
    get_timing_coefs(m_mcq_2)[1],
    get_timing_coefs(m_mcq_3)[1],
    get_timing_coefs(m_mcq_4)[1],
    get_timing_coefs(m_mcq_5)[1]
  ),
  post_beta = c(
    get_timing_coefs(m_mcq_1)[2],
    get_timing_coefs(m_mcq_2)[2],
    get_timing_coefs(m_mcq_3)[2],
    get_timing_coefs(m_mcq_4)[2],
    get_timing_coefs(m_mcq_5)[2]
  )
)
decomp$sync_beta <- round(unname(decomp$sync_beta), 4)
decomp$post_beta <- round(unname(decomp$post_beta), 4)

cat("\nProgressive MCQ Decomposition:\n")
print(decomp)

# Percentage reduction
base_sync <- decomp$sync_beta[1]
base_post <- decomp$post_beta[1]
decomp$sync_reduction <- round((1 - decomp$sync_beta / base_sync) * 100, 1)
decomp$post_reduction <- round((1 - decomp$post_beta / base_post) * 100, 1)

cat("\nWith reduction percentages:\n")
print(decomp)
write_csv(decomp, "all_tables/T3_mcq_decomposition_progressive.csv")

# Full model details
cat("\nFull model (Model 5) coefficients:\n")
print(summary(m_mcq_5)$coefficients)
write_csv(tidy(m_mcq_5), "all_tables/T3_mcq_full_decomposition.csv")

# ============================================================================
# T4) EFFORT AS MARKER (Not a Cause)
# ============================================================================
cat("\n--- T4: Mental Effort as Marker ---\n")

m_effort <- lmer(mcq_accuracy ~ timing + structure + mental_effort + article + (1|participant_id), data = ai)
cat("\nmcq ~ timing + structure + mental_effort + article:\n")
print(summary(m_effort)$coefficients)

# Compare to base
cat("\nTiming coefficient comparison:\n")
cat("Base sync:    ", round(get_timing_coefs(m_mcq_1)["sync"], 4), "\n")
cat("+ effort sync:", round(fixef(m_effort)["timingsynchronous"], 4), "\n")
cat("Base post:    ", round(get_timing_coefs(m_mcq_1)["post"], 4), "\n")
cat("+ effort post:", round(fixef(m_effort)["timingpost_reading"], 4), "\n")

write_csv(tidy(m_effort), "all_tables/T4_mcq_with_effort.csv")

# ============================================================================
# T5) WHO BENEFITS? (Within-Person Contrasts)
# ============================================================================
cat("\n--- T5: Who Benefits Profiles ---\n")

# Compute within-person deltas
wide <- ai %>%
  select(participant_id, timing, mcq_accuracy, ai_summary_accuracy, ai_trust, ai_dependence, prior_knowledge_familiarity) %>%
  pivot_wider(
    id_cols = c(participant_id, ai_trust, ai_dependence, prior_knowledge_familiarity),
    names_from = timing,
    values_from = c(mcq_accuracy, ai_summary_accuracy),
    values_fn = mean
  )

wide <- wide %>%
  mutate(
    delta_mcq_pre_sync = mcq_accuracy_pre_reading - mcq_accuracy_synchronous,
    delta_mcq_pre_post = mcq_accuracy_pre_reading - mcq_accuracy_post_reading,
    delta_summ_pre_sync = ai_summary_accuracy_pre_reading - ai_summary_accuracy_synchronous,
    delta_summ_pre_post = ai_summary_accuracy_pre_reading - ai_summary_accuracy_post_reading
  )

cat("\nDelta descriptives:\n")
delta_desc <- wide %>%
  summarise(
    across(starts_with("delta_"), list(mean = ~mean(., na.rm = TRUE), sd = ~sd(., na.rm = TRUE)))
  )
print(t(delta_desc))

# Regress deltas on traits
cat("\n--- MCQ Delta (Pre-Sync) ~ Traits ---\n")
m_delta1 <- lm(delta_mcq_pre_sync ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = wide)
print(summary(m_delta1))

cat("\n--- MCQ Delta (Pre-Post) ~ Traits ---\n")
m_delta2 <- lm(delta_mcq_pre_post ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = wide)
print(summary(m_delta2))

cat("\n--- Summary Acc Delta (Pre-Sync) ~ Traits ---\n")
m_delta3 <- lm(delta_summ_pre_sync ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = wide)
print(summary(m_delta3))

cat("\n--- Summary Acc Delta (Pre-Post) ~ Traits ---\n")
m_delta4 <- lm(delta_summ_pre_post ~ ai_trust + ai_dependence + prior_knowledge_familiarity, data = wide)
print(summary(m_delta4))

# Combine results
delta_results <- bind_rows(
  tidy(m_delta1) %>% mutate(outcome = "MCQ_pre_sync"),
  tidy(m_delta2) %>% mutate(outcome = "MCQ_pre_post"),
  tidy(m_delta3) %>% mutate(outcome = "SummAcc_pre_sync"),
  tidy(m_delta4) %>% mutate(outcome = "SummAcc_pre_post")
)
write_csv(delta_results, "all_tables/T5_who_benefits_deltas.csv")

# ============================================================================
cat("\n", strrep("=", 70), "\n")
cat("FALSE LURES FINAL ANALYSES\n")
cat(strrep("=", 70), "\n")

# ============================================================================
# L1) FULL DEFINITIVE LURE MODEL
# ============================================================================
cat("\n--- L1: Full Definitive Binomial Model ---\n")

# Check for zeros in time
ai <- ai %>%
  mutate(
    log_summary_time = log(summary_time_sec + 1),
    log_reading_time = log(reading_time_min + 0.1)
  )

m_lure_full <- glmer(
  cbind(false_lures_selected, no_lures) ~ 
    structure + timing + ai_summary_accuracy + article_accuracy + 
    ai_trust + ai_dependence + log_summary_time + log_reading_time + 
    mental_effort + article + (1|participant_id),
  data = ai, family = binomial, 
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

cat("\nFull model coefficients:\n")
full_coefs <- tidy(m_lure_full)
full_coefs$OR <- exp(full_coefs$estimate)
full_coefs$OR_lower <- exp(full_coefs$estimate - 1.96 * full_coefs$std.error)
full_coefs$OR_upper <- exp(full_coefs$estimate + 1.96 * full_coefs$std.error)
print(full_coefs %>% select(term, estimate, std.error, p.value, OR, OR_lower, OR_upper))
write_csv(full_coefs, "all_tables/L1_lure_full_model.csv")

# Key result: structure after controlling everything
cat("\nKey: Structure effect (controlling all):\n")
struct_row <- full_coefs %>% filter(grepl("structure", term))
cat("  OR =", round(struct_row$OR, 2), 
    ", 95% CI [", round(struct_row$OR_lower, 2), ",", round(struct_row$OR_upper, 2), "]",
    ", p =", round(struct_row$p.value, 4), "\n")

# Reduced model (drop always-null predictors)
m_lure_reduced <- glmer(
  cbind(false_lures_selected, no_lures) ~ 
    structure + timing + ai_summary_accuracy + article + (1|participant_id),
  data = ai, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

cat("\nReduced model (structure + timing + summary_acc + article):\n")
reduced_coefs <- tidy(m_lure_reduced)
reduced_coefs$OR <- exp(reduced_coefs$estimate)
print(reduced_coefs %>% select(term, estimate, p.value, OR))
write_csv(reduced_coefs, "all_tables/L1_lure_reduced_model.csv")

# ============================================================================
# L2) ARTICLE EFFECTS FOR LURES
# ============================================================================
cat("\n--- L2: Article Effects on False Lures ---\n")

m_lure_article <- glmer(
  cbind(false_lures_selected, no_lures) ~ structure + timing + article + (1|participant_id),
  data = ai, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

cat("\nLures by article:\n")
art_coefs <- tidy(m_lure_article)
art_coefs$OR <- exp(art_coefs$estimate)
print(art_coefs %>% select(term, estimate, p.value, OR))

# Article EMMs
emm_art <- emmeans(m_lure_article, ~article, type = "response")
cat("\nPredicted lure probability by article:\n")
print(emm_art)

art_contrasts <- as.data.frame(pairs(emm_art, adjust = "holm"))
cat("\nArticle contrasts:\n")
print(art_contrasts)

write_csv(art_coefs, "all_tables/L2_lure_by_article.csv")
write_csv(as.data.frame(emm_art), "all_tables/L2_lure_article_emms.csv")

# ============================================================================
# L3) SIMPLE EFFECTS BY STRUCTURE
# ============================================================================
cat("\n--- L3: Simple Effects of Timing Within Each Structure ---\n")

# Integrated only
ai_int <- ai %>% filter(structure == "integrated")
m_lure_int <- glmer(
  cbind(false_lures_selected, no_lures) ~ timing + article + (1|participant_id),
  data = ai_int, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)
cat("\n--- INTEGRATED structure ---\n")
print(tidy(m_lure_int) %>% select(term, estimate, p.value))

emm_int <- emmeans(m_lure_int, ~timing, type = "response")
cat("\nPredicted lure prob by timing (integrated):\n")
print(emm_int)

# Segmented only
ai_seg <- ai %>% filter(structure == "segmented")
m_lure_seg <- glmer(
  cbind(false_lures_selected, no_lures) ~ timing + article + (1|participant_id),
  data = ai_seg, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)
cat("\n--- SEGMENTED structure ---\n")
print(tidy(m_lure_seg) %>% select(term, estimate, p.value))

emm_seg <- emmeans(m_lure_seg, ~timing, type = "response")
cat("\nPredicted lure prob by timing (segmented):\n")
print(emm_seg)

# Combine
simple_effects <- bind_rows(
  as.data.frame(emm_int) %>% mutate(structure = "integrated"),
  as.data.frame(emm_seg) %>% mutate(structure = "segmented")
)
write_csv(simple_effects, "all_tables/L3_lure_simple_effects.csv")

# ============================================================================
# L4) MODEL FAMILY COMPARISON (Sensitivity)
# ============================================================================
cat("\n--- L4: Model Family Comparison ---\n")

# Binomial
m_binom <- glmer(
  cbind(false_lures_selected, no_lures) ~ structure + timing + article + (1|participant_id),
  data = ai, family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

# Poisson
m_pois <- glmer(
  false_lures_selected ~ structure + timing + article + (1|participant_id),
  data = ai, family = poisson,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

# Compare AICs
cat("\nAIC comparison:\n")
cat("  Binomial: ", round(AIC(m_binom), 1), "\n")
cat("  Poisson:  ", round(AIC(m_pois), 1), "\n")

# Compare structure coefficients
cat("\nStructure coefficient comparison:\n")
cat("  Binomial (log-OR): ", round(fixef(m_binom)["structuresegmented"], 3), "\n")
cat("  Poisson (log-IRR): ", round(fixef(m_pois)["structuresegmented"], 3), "\n")

# Structure p-values
binom_p <- tidy(m_binom) %>% filter(term == "structuresegmented") %>% pull(p.value)
pois_p <- tidy(m_pois) %>% filter(term == "structuresegmented") %>% pull(p.value)

cat("\nStructure p-values:\n")
cat("  Binomial: ", round(binom_p, 4), "\n")
cat("  Poisson:  ", round(pois_p, 4), "\n")

model_comparison <- tibble(
  model = c("Binomial", "Poisson"),
  AIC = c(AIC(m_binom), AIC(m_pois)),
  structure_coef = c(
    fixef(m_binom)["structuresegmented"],
    fixef(m_pois)["structuresegmented"]
  ),
  structure_OR_IRR = c(
    exp(fixef(m_binom)["structuresegmented"]),
    exp(fixef(m_pois)["structuresegmented"])
  ),
  structure_p = c(binom_p, pois_p)
)
write_csv(model_comparison, "all_tables/L4_model_family_comparison.csv")

cat("\nModel family comparison:\n")
print(model_comparison)

# Preferred model conclusion
cat("\nConclusion: ", 
    ifelse(AIC(m_binom) < AIC(m_pois), "Binomial", "Poisson"), 
    " is preferred (lower AIC)\n")

# Predicted probabilities from binomial
pred_probs <- emmeans(m_binom, ~structure, type = "response")
cat("\nPredicted lure probability (binomial model):\n")
print(pred_probs)

# ============================================================================
# SUMMARY PLOT: Timing Effect Decomposition
# ============================================================================
cat("\n--- Creating decomposition plot ---\n")

decomp_plot <- decomp %>%
  pivot_longer(cols = c(sync_beta, post_beta), names_to = "contrast", values_to = "beta") %>%
  mutate(contrast = ifelse(contrast == "sync_beta", "Pre vs Sync", "Pre vs Post"))

p_decomp <- ggplot(decomp_plot, aes(x = model, y = abs(beta), fill = contrast)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title = "MCQ: Timing Effect Decomposition",
    subtitle = "How timing coefficients shrink as mechanisms are added",
    x = "Model", y = "|Timing Coefficient|",
    fill = "Contrast"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("all_plots/timing_decomposition.png", p_decomp, width = 10, height = 6, dpi = 150)

# ============================================================================
cat("\n", strrep("=", 70), "\n")
cat("ANALYSES COMPLETE\n")
cat(strrep("=", 70), "\n")

cat("\nGenerated tables:\n")
cat("  T1: trust_by_timing, dependence_by_timing, trust_dep_descriptives\n")
cat("  T2: summary_acc_with_time, summary_acc_timing_contrasts\n")
cat("  T3: mcq_decomposition_progressive, mcq_full_decomposition\n")
cat("  T4: mcq_with_effort\n")
cat("  T5: who_benefits_deltas\n")
cat("  L1: lure_full_model, lure_reduced_model\n")
cat("  L2: lure_by_article, lure_article_emms\n")
cat("  L3: lure_simple_effects\n")
cat("  L4: model_family_comparison\n")
cat("\nGenerated plots:\n")
cat("  timing_decomposition.png\n")
