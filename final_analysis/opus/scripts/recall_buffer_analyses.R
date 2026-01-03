# ============================================================================
# RECALL & AI BUFFER ANALYSES
# Additional analyses connecting to literature review themes
# ============================================================================

library(tidyverse)
library(lme4)
library(lmerTest)
library(readxl)
library(broom.mixed)

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

# Prepare data
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
    summary_time_sec_num = as.numeric(summary_time_sec),
    reading_time_min_num = as.numeric(reading_time_min),
    log_summary_time = ifelse(!is.na(summary_time_sec_num) & summary_time_sec_num > 0, 
                               log(summary_time_sec_num), NA),
    log_reading_time = log(reading_time_min_num + 0.01)
  )

df_ai <- df %>% filter(experiment_group == "AI")
df_noai <- df %>% filter(experiment_group == "NoAI")

# Start output
sink(file.path(root_dir, "recall_buffer_analyses_report.txt"))

cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("RECALL & AI BUFFER ANALYSES\n")
cat("Connecting to Literature Review Themes\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# ============================================================================
# A1) DOES RECALL RELATE TO RECOGNITION (MCQ)?
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("A1) RECALL → MCQ (All Participants)\n")
cat("    Does free recall predict recognition performance?\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_a1 <- lmer(mcq_accuracy ~ recall_total_score + experiment_group + timing + 
                   structure + article + (1|participant_id), 
                 data = df)

cat("Model: mcq_accuracy ~ recall + group + timing + structure + article + (1|participant)\n\n")
print(summary(model_a1))

coef_a1 <- tidy(model_a1, effects = "fixed") %>% filter(term == "recall_total_score")

cat("\n--- KEY RESULT ---\n")
cat(sprintf("recall → MCQ: β = %.4f, SE = %.4f, t = %.2f, p = %.4f\n",
            coef_a1$estimate, coef_a1$std.error, coef_a1$statistic, coef_a1$p.value))

if (coef_a1$p.value < .05) {
  cat("✓ Significant: Recall and MCQ track SAME underlying learning\n")
} else {
  cat("✗ Not significant: Recall and MCQ are INDEPENDENT measures\n")
  cat("  → Free recall (self-generated) and recognition (cued) tap different processes\n")
}

write.csv(tidy(model_a1, effects = "fixed"), 
          file.path(tables_dir, "REC2_A1_recall_mcq_relationship.csv"), row.names = FALSE)

# Also test within AI only
cat("\n--- A1b: AI-only ---\n")
model_a1b <- lmer(mcq_accuracy ~ recall_total_score + timing + structure + article + 
                    (1|participant_id), 
                  data = df_ai)
print(summary(model_a1b))

coef_a1b <- tidy(model_a1b, effects = "fixed") %>% filter(term == "recall_total_score")
cat(sprintf("\nAI-only: recall → MCQ: β = %.4f, p = %.4f\n", coef_a1b$estimate, coef_a1b$p.value))

write.csv(tidy(model_a1b, effects = "fixed"), 
          file.path(tables_dir, "REC2_A1b_recall_mcq_AI_only.csv"), row.names = FALSE)

# ============================================================================
# A2) WHAT PREDICTS RECALL? (Process + Individual Differences)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("A2) WHAT PREDICTS RECALL?\n")
cat("    Testing process variables and individual differences\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# A2a: All participants - basic model
cat("--- A2a: All Participants (basic predictors) ---\n\n")

model_a2a <- lmer(recall_total_score ~ log_reading_time + mental_effort + 
                    prior_knowledge + experiment_group + article + 
                    (1|participant_id), 
                  data = df)

cat("Model: recall ~ log(reading_time) + mental_effort + prior_knowledge + group + article + (1|participant)\n\n")
print(summary(model_a2a))

coefs_a2a <- tidy(model_a2a, effects = "fixed")
cat("\n--- KEY RESULTS (All participants) ---\n")
for (pred in c("log_reading_time", "mental_effort", "prior_knowledge")) {
  c <- coefs_a2a %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s → recall: β = %.3f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  }
}

write.csv(coefs_a2a, 
          file.path(tables_dir, "REC2_A2a_predictors_recall_all.csv"), row.names = FALSE)

# A2b: AI only - full model with AI-specific predictors
cat("\n--- A2b: AI Only (full model with AI-specific predictors) ---\n\n")

model_a2b <- lmer(recall_total_score ~ log_reading_time + log_summary_time + 
                    mental_effort + ai_summary_accuracy + 
                    ai_trust + ai_dependence + prior_knowledge + 
                    timing + structure + article + 
                    (1|participant_id), 
                  data = df_ai)

cat("Model: recall ~ log(reading) + log(summary) + effort + summary_acc + trust + dependence + PK + timing + structure + article + (1|participant)\n\n")
print(summary(model_a2b))

coefs_a2b <- tidy(model_a2b, effects = "fixed")
cat("\n--- KEY RESULTS (AI only) ---\n")
predictors <- c("log_reading_time", "log_summary_time", "mental_effort", 
                "ai_summary_accuracy", "ai_trust", "ai_dependence", "prior_knowledge")
for (pred in predictors) {
  c <- coefs_a2b %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s → recall: β = %.3f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  }
}

write.csv(coefs_a2b, 
          file.path(tables_dir, "REC2_A2b_predictors_recall_AI.csv"), row.names = FALSE)

# Interpretation
cat("\n--- INTERPRETATION ---\n")
cat("Levels of Processing: Deeper processing (more effort/time) may support recall\n")
cat("Offloading Theory: Heavy reliance on AI may REDUCE internally generated recall\n")

# ============================================================================
# A3) RECALL CONFIDENCE CALIBRATION
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("A3) RECALL CONFIDENCE CALIBRATION\n")
cat("    Does confidence predict actual recall? (Metacognitive monitoring)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# A3a: All participants
cat("--- A3a: All Participants ---\n\n")

model_a3a <- lmer(recall_total_score ~ recall_confidence * experiment_group + 
                    (1|participant_id) + (1|article), 
                  data = df)

cat("Model: recall ~ confidence * group + (1|participant) + (1|article)\n\n")
print(summary(model_a3a))

coefs_a3a <- tidy(model_a3a, effects = "fixed")
conf_coef <- coefs_a3a %>% filter(term == "recall_confidence")
int_coef <- coefs_a3a %>% filter(grepl(":", term))

cat("\n--- KEY RESULTS ---\n")
cat(sprintf("Confidence main effect: β = %.3f, p = %.4f\n", conf_coef$estimate, conf_coef$p.value))
if (nrow(int_coef) > 0) {
  cat(sprintf("Confidence × Group interaction: β = %.3f, p = %.4f\n", 
              int_coef$estimate, int_coef$p.value))
}

if (conf_coef$p.value < .05) {
  cat("✓ Confidence IS calibrated with actual recall\n")
} else {
  cat("✗ Confidence is NOT well calibrated with recall (metacognitive failure)\n")
}

write.csv(coefs_a3a, 
          file.path(tables_dir, "REC2_A3a_confidence_calibration_all.csv"), row.names = FALSE)

# A3b: AI only with trust/dependence as moderators
cat("\n--- A3b: AI Only (with Trust/Dependence moderators) ---\n\n")

model_a3b <- lmer(recall_total_score ~ recall_confidence + ai_trust + ai_dependence + 
                    recall_confidence:ai_trust + recall_confidence:ai_dependence +
                    (1|participant_id) + (1|article), 
                  data = df_ai)

cat("Model: recall ~ confidence + trust + dependence + conf:trust + conf:dep + (1|participant) + (1|article)\n\n")
print(summary(model_a3b))

coefs_a3b <- tidy(model_a3b, effects = "fixed")
cat("\n--- KEY RESULTS (AI only with moderators) ---\n")
for (term_name in c("recall_confidence", "ai_trust", "ai_dependence", 
                    "recall_confidence:ai_trust", "recall_confidence:ai_dependence")) {
  c <- coefs_a3b %>% filter(term == term_name)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s: β = %.3f, p = %.4f [%s]\n", term_name, c$estimate, c$p.value, sig))
  }
}

write.csv(coefs_a3b, 
          file.path(tables_dir, "REC2_A3b_confidence_calibration_AI_moderated.csv"), row.names = FALSE)

# ============================================================================
# B1) SUMMARY TIME → SUMMARY ACCURACY (AI Buffer/Rehearsal)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("B1) SUMMARY TIME → SUMMARY ACCURACY (AI Buffer Effect)\n")
cat("    Does time with summary serve as rehearsal/cue window?\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_b1 <- lmer(ai_summary_accuracy ~ log_summary_time + timing + structure + article + 
                   (1|participant_id) + (1|article), 
                 data = df_ai)

cat("Model: summary_accuracy ~ log(summary_time) + timing + structure + article + (1|participant) + (1|article)\n\n")
print(summary(model_b1))

coef_b1 <- tidy(model_b1, effects = "fixed") %>% filter(term == "log_summary_time")

cat("\n--- KEY RESULT ---\n")
cat(sprintf("log(summary_time) → summary_accuracy: β = %.4f, SE = %.4f, t = %.2f, p = %.4f\n",
            coef_b1$estimate, coef_b1$std.error, coef_b1$statistic, coef_b1$p.value))

if (coef_b1$p.value < .05) {
  cat("✓ SIGNIFICANT: Longer summary time → Better summary-based performance\n")
  cat("  → Supports 'AI Buffer as rehearsal/reactivation window' framing\n")
} else {
  cat("✗ Not significant after controlling for timing/structure/article\n")
}

# Show timing effects too
cat("\n--- TIMING EFFECTS ---\n")
timing_coefs <- tidy(model_b1, effects = "fixed") %>% 
  filter(grepl("timing", term))
print(timing_coefs)

write.csv(tidy(model_b1, effects = "fixed"), 
          file.path(tables_dir, "REC2_B1_summary_time_summary_acc.csv"), row.names = FALSE)

# ============================================================================
# B2) SUMMARY TIME → MCQ (With Both Tracks)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("B2) SUMMARY TIME → MCQ (With Summary + Article Tracks)\n")
cat("    Does summary time help MCQ through summary track only?\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_b2 <- lmer(mcq_accuracy ~ log_summary_time + ai_summary_accuracy + article_accuracy + 
                   timing + structure + 
                   (1|participant_id) + (1|article), 
                 data = df_ai)

cat("Model: mcq ~ log(summary_time) + summary_acc + article_acc + timing + structure + (1|participant) + (1|article)\n\n")
print(summary(model_b2))

coefs_b2 <- tidy(model_b2, effects = "fixed")

cat("\n--- KEY RESULTS ---\n")
for (pred in c("log_summary_time", "ai_summary_accuracy", "article_accuracy")) {
  c <- coefs_b2 %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s → MCQ: β = %.4f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  }
}

# Check if summary time becomes ns when controlling for mechanisms
sum_time_p <- coefs_b2 %>% filter(term == "log_summary_time") %>% pull(p.value)
sum_acc_p <- coefs_b2 %>% filter(term == "ai_summary_accuracy") %>% pull(p.value)
art_acc_p <- coefs_b2 %>% filter(term == "article_accuracy") %>% pull(p.value)

cat("\n--- INTERPRETATION ---\n")
if (sum_time_p > .05 && sum_acc_p < .05) {
  cat("✓ Summary time effect is MEDIATED by summary accuracy\n")
  cat("  → Time helps because it improves summary quality, which then helps MCQ\n")
}
if (sum_acc_p < .05 && art_acc_p < .05) {
  cat("✓ MCQ is driven by BOTH summary track AND article track\n")
  cat("  → Consistent with dual-mechanism model\n")
}

write.csv(coefs_b2, 
          file.path(tables_dir, "REC2_B2_summary_time_mcq_mechanisms.csv"), row.names = FALSE)

# ============================================================================
# BONUS: OFFLOADING INTERPRETATION - Does AI dependence hurt recall?
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("BONUS: OFFLOADING TEST - Does AI Dependence Hurt Recall?\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_off <- lmer(recall_total_score ~ ai_dependence + ai_trust + 
                    timing + structure + article +
                    (1|participant_id), 
                  data = df_ai)

cat("Model: recall ~ ai_dependence + ai_trust + timing + structure + article + (1|participant)\n\n")
print(summary(model_off))

coef_dep <- tidy(model_off, effects = "fixed") %>% filter(term == "ai_dependence")
coef_trust <- tidy(model_off, effects = "fixed") %>% filter(term == "ai_trust")

cat("\n--- OFFLOADING INTERPRETATION ---\n")
cat(sprintf("ai_dependence → recall: β = %.3f, p = %.4f\n", coef_dep$estimate, coef_dep$p.value))
cat(sprintf("ai_trust → recall: β = %.3f, p = %.4f\n", coef_trust$estimate, coef_trust$p.value))

if (coef_dep$p.value < .05 && coef_dep$estimate < 0) {
  cat("✓ OFFLOADING EFFECT: Higher dependence on AI → LOWER recall\n")
  cat("  → Supports cognitive offloading reducing internal encoding\n")
} else if (coef_dep$p.value > .05) {
  cat("✗ No offloading effect detected: Dependence doesn't harm recall\n")
}

write.csv(tidy(model_off, effects = "fixed"), 
          file.path(tables_dir, "REC2_BONUS_offloading_test.csv"), row.names = FALSE)

# ============================================================================
# SUMMARY
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("SUMMARY OF RECALL & AI BUFFER ANALYSES\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

cat("A1) Recall → MCQ Relationship\n")
cat(sprintf("    All participants: β = %.4f, p = %.4f\n", coef_a1$estimate, coef_a1$p.value))
if (coef_a1$p.value < .05) cat("    ✓ Recall & MCQ track same learning\n") else cat("    ✗ Recall & MCQ are independent\n")

cat("\nA2) What Predicts Recall? (AI only)\n")
for (pred in predictors) {
  c <- coefs_a2b %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓" else "✗"
    cat(sprintf("    %s %s: β = %.3f, p = %.4f\n", sig, pred, c$estimate, c$p.value))
  }
}

cat("\nA3) Recall Confidence Calibration\n")
cat(sprintf("    Confidence → Recall: β = %.3f, p = %.4f\n", conf_coef$estimate, conf_coef$p.value))
if (conf_coef$p.value < .05) cat("    ✓ Good calibration\n") else cat("    ✗ Poor calibration\n")

cat("\nB1) Summary Time → Summary Accuracy (AI Buffer)\n")
cat(sprintf("    log(summary_time): β = %.4f, p = %.4f\n", coef_b1$estimate, coef_b1$p.value))
if (coef_b1$p.value < .05) cat("    ✓ Supports rehearsal/buffer effect\n") else cat("    ✗ Effect not robust\n")

cat("\nB2) MCQ Mechanism (with both tracks)\n")
for (pred in c("log_summary_time", "ai_summary_accuracy", "article_accuracy")) {
  c <- coefs_b2 %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓" else "✗"
    cat(sprintf("    %s %s: β = %.4f, p = %.4f\n", sig, pred, c$estimate, c$p.value))
  }
}

cat("\nBONUS: Offloading Effect\n")
cat(sprintf("    ai_dependence → recall: β = %.3f, p = %.4f\n", coef_dep$estimate, coef_dep$p.value))
if (coef_dep$p.value < .05 && coef_dep$estimate < 0) {
  cat("    ✓ OFFLOADING CONFIRMED: Dependence hurts recall\n")
} else {
  cat("    ✗ No offloading effect\n")
}

sink()

cat("\n✅ Recall & AI Buffer analyses complete!\n")
cat("Report saved to:", file.path(root_dir, "recall_buffer_analyses_report.txt"), "\n")
cat("Tables saved to:", tables_dir, "\n")
