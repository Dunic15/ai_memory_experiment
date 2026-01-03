# ============================================================================
# RECALL RELATIONSHIP ANALYSES
# Additional analyses focused on recall as outcome/predictor
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

# Create directories if needed
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
    # Convert character to numeric first
    summary_time_sec_num = as.numeric(summary_time_sec),
    reading_time_min_num = as.numeric(reading_time_min),
    log_summary_time = ifelse(!is.na(summary_time_sec_num) & summary_time_sec_num > 0, 
                               log(summary_time_sec_num), NA),
    log_reading_time = log(reading_time_min_num * 60 + 1)
  )

# AI-only subset
df_ai <- df %>% filter(experiment_group == "AI")

# Start output
sink(file.path(root_dir, "recall_analyses_report.txt"))

cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("RECALL RELATIONSHIP ANALYSES\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# ============================================================================
# A) DOES SUMMARY TIME PREDICT RECALL? (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("A) SUMMARY TIME → RECALL (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_a <- lmer(recall_total_score ~ log_summary_time + timing + structure + 
                  (1|participant_id) + (1|article), 
                data = df_ai)

cat("Model: recall_total_score ~ log(summary_time) + timing + structure + (1|participant) + (1|article)\n\n")
print(summary(model_a))

# Extract key result
coef_a <- tidy(model_a, effects = "fixed") %>% 
  filter(term == "log_summary_time")

cat("\n--- KEY RESULT ---\n")
cat(sprintf("log(summary_time) → recall: β = %.3f, SE = %.3f, t = %.2f, p = %.4f\n",
            coef_a$estimate, coef_a$std.error, coef_a$statistic, coef_a$p.value))

if (coef_a$p.value < .05) {
  cat("✓ Significant: Longer summary time associated with ")
  if (coef_a$estimate > 0) cat("HIGHER") else cat("LOWER")
  cat(" recall\n")
} else {
  cat("✗ Not significant: Summary time does NOT predict recall\n")
}

# Save
write.csv(tidy(model_a, effects = "fixed"), 
          file.path(tables_dir, "REC_A_summary_time_recall.csv"), row.names = FALSE)

# ============================================================================
# B) DOES MENTAL EFFORT PREDICT RECALL? (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("B) MENTAL EFFORT → RECALL (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_b <- lmer(recall_total_score ~ mental_effort + timing + structure + 
                  (1|participant_id) + (1|article), 
                data = df_ai)

cat("Model: recall_total_score ~ mental_effort + timing + structure + (1|participant) + (1|article)\n\n")
print(summary(model_b))

coef_b <- tidy(model_b, effects = "fixed") %>% 
  filter(term == "mental_effort")

cat("\n--- KEY RESULT ---\n")
cat(sprintf("mental_effort → recall: β = %.3f, SE = %.3f, t = %.2f, p = %.4f\n",
            coef_b$estimate, coef_b$std.error, coef_b$statistic, coef_b$p.value))

if (coef_b$p.value < .05) {
  cat("✓ Significant: Higher effort associated with ")
  if (coef_b$estimate > 0) cat("HIGHER") else cat("LOWER")
  cat(" recall\n")
} else {
  cat("✗ Not significant: Mental effort does NOT predict recall\n")
}

write.csv(tidy(model_b, effects = "fixed"), 
          file.path(tables_dir, "REC_B_mental_effort_recall.csv"), row.names = FALSE)

# ============================================================================
# C) TRUST / DEPENDENCE / PRIOR KNOWLEDGE → RECALL (AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("C) TRUST, DEPENDENCE, PRIOR KNOWLEDGE → RECALL (AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# C1: Trial-level mixed model
cat("--- C1: Trial-level mixed model ---\n\n")

model_c1 <- lmer(recall_total_score ~ ai_trust + ai_dependence + prior_knowledge + 
                   timing + structure + (1|participant_id) + (1|article), 
                 data = df_ai)

cat("Model: recall ~ ai_trust + ai_dependence + prior_knowledge + timing + structure + (1|participant) + (1|article)\n\n")
print(summary(model_c1))

coefs_c1 <- tidy(model_c1, effects = "fixed")

cat("\n--- KEY RESULTS ---\n")
for (pred in c("ai_trust", "ai_dependence", "prior_knowledge")) {
  c <- coefs_c1 %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s → recall: β = %.3f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  } else {
    cat(sprintf("%s: dropped from model (collinearity/rank deficiency)\n", pred))
  }
}

write.csv(coefs_c1, 
          file.path(tables_dir, "REC_C1_trust_dep_pk_recall_trial.csv"), row.names = FALSE)

# C2: Participant-level regression (aggregated)
cat("\n--- C2: Participant-level regression (aggregated) ---\n\n")

df_ai_agg <- df_ai %>%
  group_by(participant_id) %>%
  summarise(
    mean_recall = mean(recall_total_score, na.rm = TRUE),
    ai_trust = first(ai_trust),
    ai_dependence = first(ai_dependence),
    prior_knowledge = first(prior_knowledge),
    .groups = "drop"
  )

model_c2 <- lm(mean_recall ~ ai_trust + ai_dependence + prior_knowledge, data = df_ai_agg)

cat("Model: mean_recall ~ ai_trust + ai_dependence + prior_knowledge\n")
cat("N participants:", nrow(df_ai_agg), "\n\n")
print(summary(model_c2))

coefs_c2 <- tidy(model_c2)

cat("\n--- KEY RESULTS (participant-level) ---\n")
for (pred in c("ai_trust", "ai_dependence", "prior_knowledge")) {
  c <- coefs_c2 %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("%s → mean_recall: β = %.3f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  }
}

write.csv(coefs_c2, 
          file.path(tables_dir, "REC_C2_trust_dep_pk_recall_participant.csv"), row.names = FALSE)

# ============================================================================
# D) RECALL → MCQ (mechanism check, AI only)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("D) RECALL → MCQ ACCURACY (mechanism check, AI only)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

model_d <- lmer(mcq_accuracy ~ recall_total_score + timing + structure + 
                  (1|participant_id) + (1|article), 
                data = df_ai)

cat("Model: mcq_accuracy ~ recall_total_score + timing + structure + (1|participant) + (1|article)\n\n")
print(summary(model_d))

coef_d <- tidy(model_d, effects = "fixed") %>% 
  filter(term == "recall_total_score")

cat("\n--- KEY RESULT ---\n")
cat(sprintf("recall → MCQ: β = %.4f, SE = %.4f, t = %.2f, p = %.4f\n",
            coef_d$estimate, coef_d$std.error, coef_d$statistic, coef_d$p.value))

if (coef_d$p.value < .05) {
  cat("✓ Significant: Higher recall associated with HIGHER MCQ\n")
  cat("  → People who recall more also score higher on MCQ\n")
} else {
  cat("✗ Not significant: Recall does NOT predict MCQ accuracy\n")
}

write.csv(tidy(model_d, effects = "fixed"), 
          file.path(tables_dir, "REC_D_recall_mcq_mechanism.csv"), row.names = FALSE)

# Also test with all participants
cat("\n--- Also testing ALL participants ---\n\n")

model_d_all <- lmer(mcq_accuracy ~ recall_total_score + experiment_group + 
                      (1|participant_id) + (1|article), 
                    data = df)

print(summary(model_d_all))

coef_d_all <- tidy(model_d_all, effects = "fixed") %>% 
  filter(term == "recall_total_score")

cat("\n--- KEY RESULT (all participants) ---\n")
cat(sprintf("recall → MCQ: β = %.4f, p = %.4f\n", coef_d_all$estimate, coef_d_all$p.value))

write.csv(tidy(model_d_all, effects = "fixed"), 
          file.path(tables_dir, "REC_D_recall_mcq_all_participants.csv"), row.names = FALSE)

# ============================================================================
# E) ARTICLE DIFFICULTY ON RECALL (design check)
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("E) ARTICLE DIFFICULTY → RECALL (design check)\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

# E1: All participants
cat("--- E1: All participants ---\n\n")

model_e1 <- lmer(recall_total_score ~ article + experiment_group + 
                   (1|participant_id), 
                 data = df)

cat("Model: recall ~ article + experiment_group + (1|participant)\n\n")
print(summary(model_e1))

# Means by article
recall_by_article <- df %>%
  group_by(article) %>%
  summarise(
    mean_recall = mean(recall_total_score, na.rm = TRUE),
    sd_recall = sd(recall_total_score, na.rm = TRUE),
    n = n(),
    .groups = "drop"
  ) %>%
  arrange(desc(mean_recall))

cat("\n--- RECALL BY ARTICLE ---\n\n")
print(recall_by_article)

# Test article effect formally
cat("\n--- ANOVA for article effect ---\n")
anova_e <- anova(model_e1)
print(anova_e)

article_p <- anova_e["article", "Pr(>F)"]
cat(sprintf("\nArticle effect: F = %.2f, p = %.4f\n", 
            anova_e["article", "F value"], article_p))

if (article_p < .05) {
  cat("✓ Significant: Recall differs by article\n")
} else {
  cat("✗ Not significant: Recall does NOT differ by article\n")
}

write.csv(recall_by_article, 
          file.path(tables_dir, "REC_E_recall_by_article.csv"), row.names = FALSE)

# E2: AI only
cat("\n--- E2: AI only ---\n\n")

model_e2 <- lmer(recall_total_score ~ article + timing + structure + 
                   (1|participant_id), 
                 data = df_ai)

print(summary(model_e2))

anova_e2 <- anova(model_e2)
cat("\n--- ANOVA (AI only) ---\n")
print(anova_e2)

# ============================================================================
# SUMMARY
# ============================================================================

cat("\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n")
cat("SUMMARY OF RECALL ANALYSES\n")
cat("=" %>% rep(70) %>% paste(collapse = ""), "\n\n")

cat("A) Summary Time → Recall (AI only)\n")
cat(sprintf("   log(summary_time): β = %.3f, p = %.4f\n", coef_a$estimate, coef_a$p.value))
if (coef_a$p.value < .05) cat("   ✓ SIGNIFICANT\n\n") else cat("   ✗ Not significant\n\n")

cat("B) Mental Effort → Recall (AI only)\n")
cat(sprintf("   mental_effort: β = %.3f, p = %.4f\n", coef_b$estimate, coef_b$p.value))
if (coef_b$p.value < .05) cat("   ✓ SIGNIFICANT\n\n") else cat("   ✗ Not significant\n\n")

cat("C) Trust/Dependence/Prior Knowledge → Recall (AI only, trial-level)\n")
for (pred in c("ai_trust", "ai_dependence", "prior_knowledge")) {
  c <- coefs_c1 %>% filter(term == pred)
  if (nrow(c) > 0) {
    sig <- if(c$p.value < .05) "✓ SIG" else "ns"
    cat(sprintf("   %s: β = %.3f, p = %.4f [%s]\n", pred, c$estimate, c$p.value, sig))
  } else {
    cat(sprintf("   %s: dropped from model\n", pred))
  }
}

cat("\nD) Recall → MCQ (mechanism, AI only)\n")
cat(sprintf("   recall_total_score: β = %.4f, p = %.4f\n", coef_d$estimate, coef_d$p.value))
if (coef_d$p.value < .05) cat("   ✓ SIGNIFICANT: recall predicts MCQ\n\n") else cat("   ✗ Not significant\n\n")

cat("E) Article → Recall (design check)\n")
cat(sprintf("   Article effect: F = %.2f, p = %.4f\n", 
            anova_e["article", "F value"], article_p))
if (article_p < .05) cat("   ✓ SIGNIFICANT\n") else cat("   ✗ Not significant\n")
cat("   Best recall: ", as.character(recall_by_article$article[1]), 
    sprintf(" (M = %.2f)\n", recall_by_article$mean_recall[1]))
cat("   Worst recall: ", as.character(recall_by_article$article[3]), 
    sprintf(" (M = %.2f)\n", recall_by_article$mean_recall[3]))

sink()

cat("\n✅ Recall analyses complete!\n")
cat("Report saved to:", file.path(root_dir, "recall_analyses_report.txt"), "\n")
cat("Tables saved to:", tables_dir, "\n")
