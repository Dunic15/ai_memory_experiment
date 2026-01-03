#!/usr/bin/env Rscript

# =============================================================================
# ADDITIONAL FALSE LURES ANALYSIS
# =============================================================================
# 1) Summary time → false_lures_selected (Poisson/NB)
# 2) Summary time → false_lure_accuracy
# 3) False lures → learning outcomes
# 4) Trust/dependence/prior knowledge → false lures (trial-level)
# =============================================================================

# Load required packages
packages <- c("readxl", "tidyverse", "lme4", "lmerTest", "MASS", "glmmTMB",
              "MuMIn", "broom", "broom.mixed", "emmeans")

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
report_file <- file.path(output_dir, "false_lures_additional_report.txt")
sink(report_file)

cat("=============================================================================\n")
cat("ADDITIONAL FALSE LURES ANALYSIS\n")
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

# Convert factors and numerics
df$participant_id <- as.factor(df$participant_id)
df$experiment_group <- as.factor(df$experiment_group)
df$structure <- as.factor(df$structure)
df$timing <- as.factor(df$timing)
df$article <- as.factor(df$article)

df$mcq_accuracy <- as.numeric(df$mcq_accuracy)
df$ai_summary_accuracy <- as.numeric(as.character(df$ai_summary_accuracy))
df$false_lure_accuracy <- as.numeric(as.character(df$false_lure_accuracy))
df$false_lures_selected <- as.numeric(as.character(df$false_lures_selected))
df$recall_total_score <- as.numeric(df$recall_total_score)
df$reading_time_min <- as.numeric(df$reading_time_min)
df$summary_time_sec <- as.numeric(as.character(df$summary_time_sec))
df$prior_knowledge_familiarity <- as.numeric(df$prior_knowledge_familiarity)
df$ai_trust <- as.numeric(as.character(df$ai_trust))
df$ai_dependence <- as.numeric(as.character(df$ai_dependence))

# Create AI-only subset
df_ai <- df %>%
  filter(experiment_group == "AI" & structure != "control" & timing != "control") %>%
  droplevels()

df_ai$structure <- factor(df_ai$structure, levels = c("integrated", "segmented"))
df_ai$timing <- factor(df_ai$timing, levels = c("pre_reading", "synchronous", "post_reading"))

# Log-transform summary time
df_ai$log_summary_time <- log(df_ai$summary_time_sec + 1)

# Convert false_lures_selected to integer for count models
df_ai$false_lures_int <- as.integer(df_ai$false_lures_selected)

cat("AI-only subset:", nrow(df_ai), "observations,", length(unique(df_ai$participant_id)), "participants\n")
cat("False lures range:", min(df_ai$false_lures_int, na.rm=T), "-", max(df_ai$false_lures_int, na.rm=T), "\n")
cat("False lures distribution:\n")
print(table(df_ai$false_lures_int))
cat("\n")

# =============================================================================
# ANALYSIS 1: SUMMARY TIME → FALSE LURES SELECTED
# =============================================================================
cat("\n############################################################\n")
cat("ANALYSIS 1: SUMMARY TIME → FALSE LURES SELECTED\n")
cat("(Poisson mixed model, AI only)\n")
cat("############################################################\n\n")

cat("=== Poisson Mixed Model ===\n")
cat("Formula: false_lures ~ log(summary_time) + timing + structure + (1|participant) + (1|article)\n\n")

# Poisson model
model1_pois <- glmer(false_lures_int ~ log_summary_time + timing + structure + 
                      (1|participant_id) + (1|article),
                    data = df_ai, family = poisson)

cat("Fixed Effects:\n")
fe1 <- summary(model1_pois)$coefficients
print(round(fe1, 4))
cat("\n")

# Incidence Rate Ratios
cat("Incidence Rate Ratios (exp(β)):\n")
irr <- exp(fixef(model1_pois))
print(round(irr, 4))
cat("\n")

# Check overdispersion
resid_deviance <- sum(residuals(model1_pois, type = "deviance")^2)
df_resid <- nrow(df_ai) - length(fixef(model1_pois))
dispersion <- resid_deviance / df_resid
cat("Overdispersion check: residual deviance/df =", round(dispersion, 3), "\n")
if (dispersion > 1.5) {
  cat("  → Overdispersion detected, trying Negative Binomial...\n\n")
  
  # Negative Binomial model
  model1_nb <- glmer.nb(false_lures_int ~ log_summary_time + timing + structure + 
                         (1|participant_id) + (1|article),
                       data = df_ai)
  
  cat("=== Negative Binomial Mixed Model ===\n")
  cat("Fixed Effects:\n")
  fe1_nb <- summary(model1_nb)$coefficients
  print(round(fe1_nb, 4))
  cat("\n")
  
  cat("Incidence Rate Ratios (exp(β)):\n")
  irr_nb <- exp(fixef(model1_nb))
  print(round(irr_nb, 4))
  cat("\n")
  
  # Compare AIC
  cat("Model comparison:\n")
  cat("  Poisson AIC:", round(AIC(model1_pois), 2), "\n")
  cat("  NB AIC:", round(AIC(model1_nb), 2), "\n")
  cat("  → Use:", ifelse(AIC(model1_nb) < AIC(model1_pois), "Negative Binomial", "Poisson"), "\n\n")
  
  write.csv(broom.mixed::tidy(model1_nb), file.path(tables_dir, "ADD1_false_lures_summary_time_nb.csv"), row.names = FALSE)
} else {
  cat("  → No serious overdispersion, Poisson is adequate.\n\n")
  write.csv(broom.mixed::tidy(model1_pois), file.path(tables_dir, "ADD1_false_lures_summary_time_poisson.csv"), row.names = FALSE)
}

# =============================================================================
# ANALYSIS 2: SUMMARY TIME → FALSE LURE ACCURACY
# =============================================================================
cat("\n############################################################\n")
cat("ANALYSIS 2: SUMMARY TIME → FALSE LURE ACCURACY\n")
cat("(Linear mixed model, AI only)\n")
cat("############################################################\n\n")

cat("Formula: false_lure_accuracy ~ log(summary_time) + timing + structure + (1|participant) + (1|article)\n\n")

model2 <- lmer(false_lure_accuracy ~ log_summary_time + timing + structure + 
                (1|participant_id) + (1|article),
              data = df_ai)

cat("Fixed Effects:\n")
fe2 <- summary(model2)$coefficients
print(round(fe2, 4))
cat("\n")

# R-squared
r2_2 <- r.squaredGLMM(model2)
cat("R² (marginal / conditional):", round(r2_2[1], 4), "/", round(r2_2[2], 4), "\n\n")

write.csv(broom.mixed::tidy(model2), file.path(tables_dir, "ADD2_false_lure_accuracy_summary_time.csv"), row.names = FALSE)

# =============================================================================
# ANALYSIS 3: FALSE LURES → LEARNING OUTCOMES
# =============================================================================
cat("\n############################################################\n")
cat("ANALYSIS 3: DO FALSE LURES HARM LEARNING?\n")
cat("(Linear mixed models, AI only)\n")
cat("############################################################\n\n")

# 3A: MCQ
cat("=== 3A: MCQ ~ False Lures Selected ===\n")
cat("Formula: mcq_accuracy ~ false_lures_selected + timing + structure + (1|participant) + (1|article)\n\n")

model3a <- lmer(mcq_accuracy ~ false_lures_selected + timing + structure + 
                 (1|participant_id) + (1|article),
               data = df_ai)

cat("Fixed Effects:\n")
fe3a <- summary(model3a)$coefficients
print(round(fe3a, 4))
cat("\n")

r2_3a <- r.squaredGLMM(model3a)
cat("R² (marginal / conditional):", round(r2_3a[1], 4), "/", round(r2_3a[2], 4), "\n\n")

write.csv(broom.mixed::tidy(model3a), file.path(tables_dir, "ADD3A_mcq_false_lures.csv"), row.names = FALSE)

# 3B: Recall
cat("=== 3B: Recall ~ False Lures Selected ===\n")
cat("Formula: recall_total_score ~ false_lures_selected + timing + structure + (1|participant) + (1|article)\n\n")

model3b <- lmer(recall_total_score ~ false_lures_selected + timing + structure + 
                 (1|participant_id) + (1|article),
               data = df_ai)

cat("Fixed Effects:\n")
fe3b <- summary(model3b)$coefficients
print(round(fe3b, 4))
cat("\n")

r2_3b <- r.squaredGLMM(model3b)
cat("R² (marginal / conditional):", round(r2_3b[1], 4), "/", round(r2_3b[2], 4), "\n\n")

write.csv(broom.mixed::tidy(model3b), file.path(tables_dir, "ADD3B_recall_false_lures.csv"), row.names = FALSE)

# =============================================================================
# ANALYSIS 4: TRUST/DEPENDENCE/PRIOR KNOWLEDGE → FALSE LURES (TRIAL-LEVEL)
# =============================================================================
cat("\n############################################################\n")
cat("ANALYSIS 4: TRUST/DEPENDENCE/PRIOR KNOWLEDGE → FALSE LURES\n")
cat("(Poisson mixed model, trial-level, AI only)\n")
cat("############################################################\n\n")

cat("Formula: false_lures ~ structure + timing + ai_trust + ai_dependence + prior_knowledge + (1|participant) + (1|article)\n\n")

# Center predictors
df_ai$trust_c <- scale(df_ai$ai_trust, center = TRUE, scale = TRUE)[,1]
df_ai$dependence_c <- scale(df_ai$ai_dependence, center = TRUE, scale = TRUE)[,1]
df_ai$prior_knowledge_c <- scale(df_ai$prior_knowledge_familiarity, center = TRUE, scale = TRUE)[,1]

# Poisson model
model4_pois <- glmer(false_lures_int ~ structure + timing + trust_c + dependence_c + prior_knowledge_c + 
                      (1|participant_id) + (1|article),
                    data = df_ai, family = poisson)

cat("=== Poisson Mixed Model ===\n")
cat("Fixed Effects:\n")
fe4 <- summary(model4_pois)$coefficients
print(round(fe4, 4))
cat("\n")

cat("Incidence Rate Ratios (exp(β)):\n")
irr4 <- exp(fixef(model4_pois))
print(round(irr4, 4))
cat("\n")

# Check overdispersion
resid_deviance4 <- sum(residuals(model4_pois, type = "deviance")^2)
df_resid4 <- nrow(df_ai) - length(fixef(model4_pois))
dispersion4 <- resid_deviance4 / df_resid4
cat("Overdispersion check: residual deviance/df =", round(dispersion4, 3), "\n")

if (dispersion4 > 1.5) {
  cat("  → Overdispersion detected, trying Negative Binomial...\n\n")
  
  model4_nb <- glmer.nb(false_lures_int ~ structure + timing + trust_c + dependence_c + prior_knowledge_c + 
                         (1|participant_id) + (1|article),
                       data = df_ai)
  
  cat("=== Negative Binomial Mixed Model ===\n")
  cat("Fixed Effects:\n")
  fe4_nb <- summary(model4_nb)$coefficients
  print(round(fe4_nb, 4))
  cat("\n")
  
  cat("Incidence Rate Ratios (exp(β)):\n")
  irr4_nb <- exp(fixef(model4_nb))
  print(round(irr4_nb, 4))
  cat("\n")
  
  write.csv(broom.mixed::tidy(model4_nb), file.path(tables_dir, "ADD4_false_lures_individual_diff_nb.csv"), row.names = FALSE)
} else {
  cat("  → No serious overdispersion, Poisson is adequate.\n\n")
  write.csv(broom.mixed::tidy(model4_pois), file.path(tables_dir, "ADD4_false_lures_individual_diff_poisson.csv"), row.names = FALSE)
}

# =============================================================================
# SUMMARY
# =============================================================================
cat("\n############################################################\n")
cat("SUMMARY OF ADDITIONAL FALSE LURES ANALYSES\n")
cat("############################################################\n\n")

cat("1) Summary Time → False Lures Selected:\n")
cat("   log(summary_time) β =", round(fe1["log_summary_time", "Estimate"], 4), 
    ", p =", round(fe1["log_summary_time", "Pr(>|z|)"], 4), "\n")
cat("   IRR =", round(irr["log_summary_time"], 3), "\n\n")

cat("2) Summary Time → False Lure Accuracy:\n")
cat("   log(summary_time) β =", round(fe2["log_summary_time", "Estimate"], 4), 
    ", p =", round(fe2["log_summary_time", "Pr(>|t|)"], 4), "\n\n")

cat("3) False Lures → Learning:\n")
cat("   MCQ: false_lures β =", round(fe3a["false_lures_selected", "Estimate"], 4), 
    ", p =", round(fe3a["false_lures_selected", "Pr(>|t|)"], 4), "\n")
cat("   Recall: false_lures β =", round(fe3b["false_lures_selected", "Estimate"], 4), 
    ", p =", round(fe3b["false_lures_selected", "Pr(>|t|)"], 4), "\n\n")

cat("4) Trust/Dependence/Prior Knowledge → False Lures:\n")
cat("   Trust β =", round(fe4["trust_c", "Estimate"], 4), 
    ", p =", round(fe4["trust_c", "Pr(>|z|)"], 4), "\n")
cat("   Dependence β =", round(fe4["dependence_c", "Estimate"], 4), 
    ", p =", round(fe4["dependence_c", "Pr(>|z|)"], 4), "\n")
cat("   Prior Knowledge β =", round(fe4["prior_knowledge_c", "Estimate"], 4), 
    ", p =", round(fe4["prior_knowledge_c", "Pr(>|z|)"], 4), "\n\n")

cat("=============================================================================\n")
cat("END OF ADDITIONAL ANALYSES\n")
cat("=============================================================================\n")

sink()

cat("\n\n=== ANALYSIS COMPLETE ===\n")
cat("Outputs saved to:", output_dir, "\n")
