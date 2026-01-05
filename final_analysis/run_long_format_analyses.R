#!/usr/bin/env Rscript

# Long-format analyses (A–G) for AI Memory Experiment
# - Uses long format: 1 row = participant × trial/article
# - Repeated-measures models include random intercepts for participant_id and article
# - AI-only where required (ai_summary_accuracy, ai_trust, ai_dependence, summary_time_sec)
# - Outputs saved to final_analysis/long_format_outputs/{tables,plots}/ + report.txt

options(stringsAsFactors = FALSE)
options(contrasts = c("contr.sum", "contr.poly")) # for Type-III tests

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(lme4)
  library(lmerTest)
  library(car)
  library(emmeans)
  library(performance)
})


# -----------------------------------------------------------------------------
# Paths + IO helpers
# -----------------------------------------------------------------------------

cwd <- normalizePath(getwd(), winslash = "/", mustWork = FALSE)
data_dir_candidates <- unique(c(
  cwd,
  file.path(cwd, "final_analysis")
))
data_dir <- NULL
for (cand in data_dir_candidates) {
  if (file.exists(file.path(cand, "Analysis long finals-.xlsx"))) {
    data_dir <- cand
    break
  }
}
if (is.null(data_dir)) {
  tried <- paste(file.path(data_dir_candidates, "Analysis long finals-.xlsx"), collapse = ", ")
  stop(paste0("Could not find long file. Tried: ", tried), call. = FALSE)
}

long_xlsx <- file.path(data_dir, "Analysis long finals-.xlsx")
out_root <- file.path(data_dir, "long_format_outputs")
tables_dir <- file.path(out_root, "tables")
plots_dir <- file.path(out_root, "plots")
dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

report_path <- file.path(out_root, "report.txt")
report_lines <- c()

log_line <- function(...) {
  msg <- paste0(...)
  report_lines <<- c(report_lines, msg)
}

write_table <- function(df, filename) {
  write.csv(df, file.path(tables_dir, filename), row.names = FALSE)
}

save_plot <- function(p, filename, width = 7.5, height = 4.5, dpi = 160) {
  ggsave(filename = file.path(plots_dir, filename), plot = p, width = width, height = height, dpi = dpi)
}

format_p <- function(p) {
  if (length(p) == 0) return("NA")
  p <- p[[1]]
  if (is.na(p)) return("NA")
  if (p < 0.001) return("< .001")
  sprintf("= %.3f", p)
}


# -----------------------------------------------------------------------------
# Read long Excel with possible embedded header row
# -----------------------------------------------------------------------------

find_sheet_with_embedded_header <- function(path, header_key = "participant_id") {
  sheets <- readxl::excel_sheets(path)
  for (sheet in sheets) {
    preview <- readxl::read_excel(path, sheet = sheet, col_names = FALSE, n_max = 25)
    preview_chr <- as.data.frame(lapply(preview, as.character))
    if (any(preview_chr == header_key, na.rm = TRUE)) {
      return(sheet)
    }
  }
  return(sheets[[1]])
}

read_sheet_with_embedded_header <- function(path, sheet = NULL, header_key = "participant_id") {
  if (is.null(sheet)) sheet <- find_sheet_with_embedded_header(path, header_key)
  raw <- readxl::read_excel(path, sheet = sheet, col_names = FALSE)
  raw_chr <- as.data.frame(lapply(raw, as.character))
  header_row <- NA_integer_
  for (i in seq_len(min(25, nrow(raw_chr)))) {
    if (any(trimws(raw_chr[i, ]) == header_key, na.rm = TRUE)) {
      header_row <- i
      break
    }
  }
  if (is.na(header_row)) {
    stop(sprintf("Could not find embedded header row containing '%s' in %s / %s", header_key, path, sheet), call. = FALSE)
  }
  header <- as.character(unlist(raw[header_row, ], use.names = FALSE))
  df <- raw[(header_row + 1):nrow(raw), , drop = FALSE]
  names(df) <- header
  as.data.frame(df, stringsAsFactors = FALSE)
}


# -----------------------------------------------------------------------------
# Stats helpers
# -----------------------------------------------------------------------------

anova_table_lmer <- function(model) {
  a <- tryCatch(
    car::Anova(model, type = 3, test.statistic = "F"),
    error = function(e) car::Anova(model, type = 3)
  )
  a_df <- as.data.frame(a)
  a_df$effect <- rownames(a_df)
  rownames(a_df) <- NULL

  # Normalize column names across lmer/glmer
  if ("F" %in% names(a_df)) {
    df1 <- a_df$Df
    df2 <- a_df$Df.res
    stat <- a_df$F
    p <- a_df$`Pr(>F)`
    eta_p2 <- (stat * df1) / (stat * df1 + df2)
    out <- data.frame(
      effect = a_df$effect,
      test = "F",
      df1 = df1,
      df2 = df2,
      stat = stat,
      p = p,
      partial_eta2 = eta_p2
    )
    return(out)
  }
  if ("F value" %in% names(a_df)) {
    stat_col <- "F value"
    df1 <- a_df$Df
    df2 <- a_df$`Den Df`
    p_col <- "Pr(>F)"
    stat <- a_df[[stat_col]]
    p <- a_df[[p_col]]
    eta_p2 <- (stat * df1) / (stat * df1 + df2)
    out <- data.frame(
      effect = a_df$effect,
      test = "F",
      df1 = df1,
      df2 = df2,
      stat = stat,
      p = p,
      partial_eta2 = eta_p2
    )
    return(out)
  }

  # glmer case (Chisq)
  if ("Chisq" %in% names(a_df)) {
    out <- data.frame(
      effect = a_df$effect,
      test = "Chisq",
      df1 = a_df$Df,
      df2 = NA_real_,
      stat = a_df$Chisq,
      p = a_df$`Pr(>Chisq)`,
      partial_eta2 = NA_real_
    )
    return(out)
  }

  stop("Unsupported Anova table format.")
}

fixed_effects_table <- function(model) {
  s <- summary(model)
  coefs <- as.data.frame(s$coefficients)
  coefs$term <- rownames(coefs)
  rownames(coefs) <- NULL
  # Normalize columns (robust exact matches)
  if ("Std. Error" %in% names(coefs)) names(coefs)[names(coefs) == "Std. Error"] <- "SE"
  if ("t value" %in% names(coefs)) names(coefs)[names(coefs) == "t value"] <- "t"
  if ("z value" %in% names(coefs)) names(coefs)[names(coefs) == "z value"] <- "z"
  if ("Pr(>|t|)" %in% names(coefs)) names(coefs)[names(coefs) == "Pr(>|t|)"] <- "p"
  if ("Pr(>|z|)" %in% names(coefs)) names(coefs)[names(coefs) == "Pr(>|z|)"] <- "p"
  coefs
}

means_plot <- function(df, dv, dv_label, filename) {
  desc <- df %>%
    group_by(structure, timing) %>%
    summarise(
      n = n(),
      mean = mean(.data[[dv]], na.rm = TRUE),
      sd = sd(.data[[dv]], na.rm = TRUE),
      se = sd / sqrt(n),
      .groups = "drop"
    )
  p <- ggplot(desc, aes(x = timing, y = mean, color = structure, group = structure)) +
    geom_line(linewidth = 1.1) +
    geom_point(size = 2.6) +
    geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.15) +
    labs(x = "Timing", y = dv_label, title = paste0(dv_label, " by Structure × Timing (AI only)")) +
    theme_minimal(base_size = 12) +
    theme(legend.title = element_text(size = 11), legend.position = "right")
  save_plot(p, filename)
  invisible(desc)
}


# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------

log_line("Long-format analyses (A–G)")
log_line(paste0("Long source: ", basename(long_xlsx)))
log_line(paste0("Generated: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S")))
log_line("")

df <- read_sheet_with_embedded_header(long_xlsx)

# Cast variables
df <- df %>%
  mutate(
    participant_id = factor(participant_id),
    experiment_group = factor(experiment_group),
    structure = factor(structure),
    timing = factor(timing),
    article = factor(article),
    mcq_accuracy = as.numeric(mcq_accuracy),
    recall_total_score = as.numeric(recall_total_score),
    recall_confidence = as.numeric(recall_confidence),
    article_accuracy = as.numeric(article_accuracy),
    ai_summary_accuracy = as.numeric(ai_summary_accuracy),
    false_lures_selected = as.numeric(false_lures_selected),
    false_lure_accuracy = as.numeric(false_lure_accuracy),
    mental_effort = as.numeric(mental_effort),
    summary_time_sec = as.numeric(summary_time_sec),
    reading_time_min = as.numeric(reading_time_min),
    ai_trust = as.numeric(ai_trust),
    ai_dependence = as.numeric(ai_dependence),
    prior_knowledge_familiarity = as.numeric(prior_knowledge_familiarity)
  )

# AI-only subset (for most mixed models here)
df_ai <- df %>%
  filter(experiment_group == "AI", structure %in% c("integrated", "segmented"), timing %in% c("pre_reading", "synchronous", "post_reading")) %>%
  mutate(
    structure = factor(structure, levels = c("integrated", "segmented")),
    timing = factor(timing, levels = c("pre_reading", "synchronous", "post_reading"))
  )

# Derived time-allocation measures (AI only)
df_ai <- df_ai %>%
  mutate(
    reading_time_sec = reading_time_min * 60,
    total_time_sec = reading_time_sec + summary_time_sec,
    summary_prop = summary_time_sec / total_time_sec,
    reading_prop = reading_time_sec / total_time_sec
  )


# -----------------------------------------------------------------------------
# A) Timing → learning outcomes (AI only)
# -----------------------------------------------------------------------------

log_line("A) Timing → learning outcomes (AI only)")

run_mixed_anova_lmer <- function(dv, label, prefix) {
  d <- df_ai %>% filter(!is.na(.data[[dv]]))
  model <- lmer(as.formula(paste0(dv, " ~ structure * timing + (1|participant_id) + (1|article)")), data = d, REML = TRUE)

  anova_tbl <- anova_table_lmer(model) %>% filter(effect %in% c("structure", "timing", "structure:timing"))
  desc <- d %>% group_by(structure, timing) %>% summarise(
    n = n(),
    mean = mean(.data[[dv]], na.rm = TRUE),
    sd = sd(.data[[dv]], na.rm = TRUE),
    se = sd / sqrt(n),
    .groups = "drop"
  )

  write_table(desc, paste0("A1_descriptives_", prefix, ".csv"))
  write_table(anova_tbl, paste0("A1_anova_", prefix, ".csv"))
  means_plot(d, dv, label, paste0("A1_plot_", prefix, ".png"))

  # Post-hoc for timing (Holm) when meaningful
  p_int <- anova_tbl$p[anova_tbl$effect == "structure:timing"]
  p_time <- anova_tbl$p[anova_tbl$effect == "timing"]
  if (!is.na(p_int) && p_int < 0.05) {
    emm <- emmeans(model, ~ timing | structure)
    ph <- pairs(emm, adjust = "holm") %>% as.data.frame()
    write_table(ph, paste0("A1_posthoc_timing_within_structure_", prefix, ".csv"))
  } else if (!is.na(p_time) && p_time < 0.05) {
    emm <- emmeans(model, ~ timing)
    ph <- pairs(emm, adjust = "holm") %>% as.data.frame()
    write_table(ph, paste0("A1_posthoc_timing_", prefix, ".csv"))
  }

  # Report summary line
  row_time <- anova_tbl %>% filter(effect == "timing")
  row_int <- anova_tbl %>% filter(effect == "structure:timing")
  log_line(paste0("- ", label, ": Timing p ", format_p(row_time$p), "; Interaction p ", format_p(row_int$p)))

  list(model = model, anova = anova_tbl, descriptives = desc)
}

res_A1_mcq <- run_mixed_anova_lmer("mcq_accuracy", "MCQ accuracy", "mcq_accuracy")
res_A1_recall <- run_mixed_anova_lmer("recall_total_score", "Recall total score", "recall_total_score")
res_A1_article <- run_mixed_anova_lmer("article_accuracy", "Article-only accuracy", "article_accuracy")

log_line("")


# -----------------------------------------------------------------------------
# B) Mechanism: does summary accuracy predict learning? (AI only)
# -----------------------------------------------------------------------------

log_line("B) Mechanism: ai_summary_accuracy → learning (AI only)")

run_bridge_models <- function(dv, label, prefix) {
  d <- df_ai %>% filter(!is.na(.data[[dv]]), !is.na(ai_summary_accuracy))
  base <- lmer(as.formula(paste0(dv, " ~ timing + structure + (1|participant_id) + (1|article)")), data = d, REML = FALSE)
  full <- lmer(as.formula(paste0(dv, " ~ ai_summary_accuracy + timing + structure + (1|participant_id) + (1|article)")), data = d, REML = FALSE)

  fe_full <- fixed_effects_table(full)
  write_table(fe_full, paste0("B1_fixed_effects_", prefix, ".csv"))

  r2_df <- tryCatch(as.data.frame(performance::r2_nakagawa(full)), error = function(e) NULL)
  if (!is.null(r2_df) && all(c("R2_marginal", "R2_conditional") %in% names(r2_df))) {
    write_table(
      data.frame(marginal_R2 = r2_df$R2_marginal, conditional_R2 = r2_df$R2_conditional),
      paste0("B1_r2_", prefix, ".csv")
    )
  }

  cmp <- anova(base, full)
  cmp_df <- as.data.frame(cmp)
  cmp_df$model <- rownames(cmp_df)
  rownames(cmp_df) <- NULL
  write_table(cmp_df, paste0("B1_model_comparison_", prefix, ".csv"))

  # Timing coefficients shrinkage (optional note)
  get_timing_terms <- function(m) {
    cf <- fixef(m)
    cf[grepl("^timing", names(cf))]
  }
  timing_base <- get_timing_terms(base)
  timing_full <- get_timing_terms(full)
  shrink_df <- data.frame(
    term = names(timing_base),
    beta_base = as.numeric(timing_base),
    beta_full = as.numeric(timing_full)
  )
  write_table(shrink_df, paste0("B1_timing_coefficients_base_vs_full_", prefix, ".csv"))

  # Report ai_summary_accuracy term
  coef_row <- fe_full %>% filter(term == "ai_summary_accuracy")
  if (nrow(coef_row) == 1) {
    log_line(
      paste0(
        "- ", label, ": ai_summary_accuracy beta = ", sprintf("%.3f", coef_row$Estimate),
        ", p ", format_p(coef_row$p)
      )
    )
  } else {
    log_line(paste0("- ", label, ": ai_summary_accuracy term not found"))
  }
  list(base = base, full = full)
}

res_B1_mcq <- run_bridge_models("mcq_accuracy", "MCQ accuracy", "mcq_accuracy")
res_B1_recall <- run_bridge_models("recall_total_score", "Recall total score", "recall_total_score")
res_B1_article <- run_bridge_models("article_accuracy", "Article-only accuracy", "article_accuracy")

# B2) Does ai_summary_accuracy explain Timing → MCQ? (timing shrink + model fit)
run_timing_shrink_summary <- function(base, full, prefix) {
  emm_base <- emmeans(base, ~ timing)
  emm_full <- emmeans(full, ~ timing)

  pb <- as.data.frame(pairs(emm_base, adjust = "holm"))
  pf <- as.data.frame(pairs(emm_full, adjust = "holm"))

  out <- pb %>%
    select(contrast, estimate_base = estimate, SE_base = SE, df_base = df, t_base = t.ratio, p_base_holm = p.value) %>%
    left_join(
      pf %>% select(contrast, estimate_full = estimate, SE_full = SE, df_full = df, t_full = t.ratio, p_full_holm = p.value),
      by = "contrast"
    ) %>%
    mutate(delta_estimate = estimate_full - estimate_base)

  write_table(out, paste0("B2_timing_pairwise_base_vs_full_", prefix, ".csv"))

  cmp <- anova(base, full)
  cmp_df <- as.data.frame(cmp)
  cmp_df$model <- rownames(cmp_df)
  rownames(cmp_df) <- NULL
  write_table(cmp_df, paste0("B2_model_comparison_", prefix, ".csv"))

  out
}

timing_shrink_mcq <- run_timing_shrink_summary(res_B1_mcq$base, res_B1_mcq$full, "mcq_accuracy")
log_line("- Timing→MCQ shrink summary: saved `B2_timing_pairwise_base_vs_full_mcq_accuracy.csv` and model comparison")

log_line("")


# -----------------------------------------------------------------------------
# C) Explain Structure → false lures (AI only)
# -----------------------------------------------------------------------------

log_line("C) Structure → false lures (AI only)")

# C1) false_lure_accuracy mixed model
res_C1_fla <- run_mixed_anova_lmer("false_lure_accuracy", "False-lure accuracy", "false_lure_accuracy")

# C2) false_lures_selected mixed models (Poisson GLMM, with fallback)
run_false_lures_models <- function() {
  d <- df_ai %>% filter(!is.na(false_lures_selected))

  fit_glmer <- function(formula_str) {
    glmer(as.formula(formula_str), data = d, family = poisson, control = glmerControl(optimizer = "bobyqa"))
  }

  base_formula <- "false_lures_selected ~ structure + timing + (1|participant_id) + (1|article)"
  mech_formula <- "false_lures_selected ~ structure + timing + mental_effort + reading_time_min + summary_time_sec + (1|participant_id) + (1|article)"

  base <- tryCatch(fit_glmer(base_formula), error = function(e) NULL)
  mech <- tryCatch(fit_glmer(mech_formula), error = function(e) NULL)

  if (is.null(base) || is.null(mech)) {
    # Fallback to Gaussian LMM
    base <- lmer(as.formula(base_formula), data = d, REML = FALSE)
    mech <- lmer(as.formula(mech_formula), data = d, REML = FALSE)
  }

  fe_base <- fixed_effects_table(base)
  fe_mech <- fixed_effects_table(mech)
  write_table(fe_base, "C2_false_lures_selected_base_fixed_effects.csv")
  write_table(fe_mech, "C2_false_lures_selected_mechanism_fixed_effects.csv")

  # Compare structure coefficient
  get_struct <- function(fe) fe %>% filter(grepl("^structure", term)) %>% select(term, Estimate, SE, p)
  struct_base <- get_struct(fe_base)
  struct_mech <- get_struct(fe_mech)
  comp <- full_join(
    struct_base %>% rename(Estimate_base = Estimate, SE_base = SE, p_base = p),
    struct_mech %>% rename(Estimate_mech = Estimate, SE_mech = SE, p_mech = p),
    by = "term"
  )
  write_table(comp, "C2_structure_coefficient_base_vs_mechanism.csv")

  # R2 (optional; may not exist for glmer in some setups)
  r2_mech <- tryCatch(performance::r2_nakagawa(mech), error = function(e) NULL)
  r2_mech_df <- tryCatch(as.data.frame(r2_mech), error = function(e) NULL)
  if (!is.null(r2_mech_df) && all(c("R2_marginal", "R2_conditional") %in% names(r2_mech_df))) {
    write_table(
      data.frame(marginal_R2 = r2_mech_df$R2_marginal, conditional_R2 = r2_mech_df$R2_conditional),
      "C2_false_lures_selected_mechanism_r2.csv"
    )
  }

  log_line("- false_lures_selected: saved base/mechanism mixed model fixed effects and structure-coefficient comparison")
}

run_false_lures_models()

log_line("")


# -----------------------------------------------------------------------------
# D) Effort/time process variables (AI only)
# -----------------------------------------------------------------------------

log_line("D) Effort/time as process variables (AI only)")

res_D1_effort <- run_mixed_anova_lmer("mental_effort", "Mental effort", "mental_effort")
res_D1_summary_time <- run_mixed_anova_lmer("summary_time_sec", "Summary time (sec)", "summary_time_sec")
res_D1_summary_prop <- run_mixed_anova_lmer("summary_prop", "Summary time proportion", "summary_prop")
res_D1_reading_time <- run_mixed_anova_lmer("reading_time_min", "Reading time (min)", "reading_time_min")
res_D1_total_time <- run_mixed_anova_lmer("total_time_sec", "Total time (sec)", "total_time_sec")

log_line("")


# -----------------------------------------------------------------------------
# E) AI trust/dependence predictors + moderation (AI only)
# -----------------------------------------------------------------------------

log_line("E) AI trust/dependence (AI only)")

# E1) Participant-level aggregation regressions
ai_participant <- df_ai %>%
  group_by(participant_id) %>%
  summarise(
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    mean_ai_summary_accuracy = mean(ai_summary_accuracy, na.rm = TRUE),
    mean_false_lures_selected = mean(false_lures_selected, na.rm = TRUE),
    mean_mental_effort = mean(mental_effort, na.rm = TRUE),
    mean_summary_time_sec = mean(summary_time_sec, na.rm = TRUE),
    ai_trust = first(ai_trust),
    ai_dependence = first(ai_dependence),
    prior_knowledge_familiarity = first(prior_knowledge_familiarity),
    structure = first(structure),
    .groups = "drop"
  )

run_lm <- function(formula_str, filename_prefix) {
  m <- lm(as.formula(formula_str), data = ai_participant)
  coefs <- summary(m)$coefficients
  coef_df <- data.frame(term = rownames(coefs), coefs, row.names = NULL)
  names(coef_df) <- c("term", "Estimate", "SE", "t", "p")
  write_table(coef_df, paste0("E1_", filename_prefix, "_coefficients.csv"))
  write_table(data.frame(R2 = summary(m)$r.squared, adj_R2 = summary(m)$adj.r.squared),
              paste0("E1_", filename_prefix, "_r2.csv"))
  m
}

run_lm("mean_mcq ~ ai_trust + ai_dependence + prior_knowledge_familiarity", "mean_mcq")
run_lm("mean_ai_summary_accuracy ~ ai_trust + ai_dependence + prior_knowledge_familiarity", "mean_ai_summary_accuracy")
run_lm("mean_false_lures_selected ~ ai_trust + ai_dependence + prior_knowledge_familiarity", "mean_false_lures_selected")

# E2) Moderation models (trial-level; random intercepts for participant + article)
run_moderation_model <- function(dv, dv_label, moderator, prefix) {
  d <- df_ai %>% filter(!is.na(.data[[dv]]), !is.na(.data[[moderator]]))
  m <- lmer(
    as.formula(paste0(dv, " ~ timing * ", moderator, " + structure + (1|participant_id) + (1|article)")),
    data = d,
    REML = TRUE
  )

  fe <- fixed_effects_table(m)
  write_table(fe, paste0("E2_", dv, "_moderation_", prefix, "_fixed_effects.csv"))

  a <- anova_table_lmer(m)
  write_table(a, paste0("E2_", dv, "_moderation_", prefix, "_anova.csv"))

  interaction_term <- paste0("timing:", moderator)
  p_int <- a$p[a$effect == interaction_term]

  # Follow-up: simple effects of timing at low/high moderator (±1 SD), Holm-corrected
  if (length(p_int) == 1 && !is.na(p_int) && p_int < 0.05) {
    mod_mean <- mean(d[[moderator]], na.rm = TRUE)
    mod_sd <- sd(d[[moderator]], na.rm = TRUE)
    at_vals <- c(mod_mean - mod_sd, mod_mean + mod_sd)

    emm <- emmeans(
      m,
      specs = as.formula(paste0("~ timing | ", moderator)),
      at = setNames(list(at_vals), moderator)
    )

    ph <- as.data.frame(pairs(emm, adjust = "holm"))
    write_table(ph, paste0("E2_", dv, "_moderation_", prefix, "_simple_slopes_timing.csv"))

    emm_df <- as.data.frame(emm) %>%
      mutate(
        moderator_value = .data[[moderator]],
        moderator_level = factor(
          moderator_value,
          levels = sort(unique(moderator_value)),
          labels = c("Low (-1 SD)", "High (+1 SD)")
        )
      )

    p_plot <- ggplot(emm_df, aes(x = timing, y = emmean, color = moderator_level, group = moderator_level)) +
      geom_line(linewidth = 1.1) +
      geom_point(size = 2.6) +
      geom_errorbar(aes(ymin = emmean - SE, ymax = emmean + SE), width = 0.15) +
      labs(
        x = "Timing",
        y = dv_label,
        title = paste0(dv_label, " by Timing × ", moderator, " (AI only; ±1 SD)"),
        color = moderator
      ) +
      theme_minimal(base_size = 12) +
      theme(legend.position = "right")

    save_plot(p_plot, paste0("E2_", dv, "_moderation_", prefix, "_interaction_plot.png"))
  }

  log_line(paste0("- ", dv_label, " moderation by ", moderator, ": interaction p ", format_p(p_int)))
}

# 2A) Moderation of Timing on AI summary accuracy
run_moderation_model("ai_summary_accuracy", "AI summary accuracy", "ai_trust", "timing_by_ai_trust")
run_moderation_model("ai_summary_accuracy", "AI summary accuracy", "ai_dependence", "timing_by_ai_dependence")
run_moderation_model("ai_summary_accuracy", "AI summary accuracy", "prior_knowledge_familiarity", "timing_by_prior_knowledge")

# 2B) Moderation of Timing on MCQ accuracy
run_moderation_model("mcq_accuracy", "MCQ accuracy", "ai_trust", "timing_by_ai_trust")
run_moderation_model("mcq_accuracy", "MCQ accuracy", "ai_dependence", "timing_by_ai_dependence")
run_moderation_model("mcq_accuracy", "MCQ accuracy", "prior_knowledge_familiarity", "timing_by_prior_knowledge")

# 3) Does prior knowledge moderate AI vs NoAI difference? (participant-level)
log_line("E3) Group × prior knowledge (participant mean MCQ)")

part_all <- df %>%
  filter(experiment_group %in% c("AI", "NoAI"), !is.na(mcq_accuracy), !is.na(prior_knowledge_familiarity)) %>%
  group_by(participant_id, experiment_group) %>%
  summarise(
    mean_mcq = mean(mcq_accuracy, na.rm = TRUE),
    prior_knowledge_familiarity = first(prior_knowledge_familiarity),
    .groups = "drop"
  ) %>%
  mutate(experiment_group = factor(experiment_group, levels = c("NoAI", "AI")))

m_pk <- lm(mean_mcq ~ experiment_group * prior_knowledge_familiarity, data = part_all)
coefs_pk <- summary(m_pk)$coefficients
coef_pk_df <- data.frame(term = rownames(coefs_pk), coefs_pk, row.names = NULL)
names(coef_pk_df) <- c("term", "Estimate", "SE", "t", "p")
write_table(coef_pk_df, "E3_group_by_prior_knowledge_coefficients.csv")
write_table(data.frame(R2 = summary(m_pk)$r.squared, adj_R2 = summary(m_pk)$adj.r.squared), "E3_group_by_prior_knowledge_r2.csv")

anova_pk <- as.data.frame(car::Anova(m_pk, type = 3))
anova_pk$effect <- rownames(anova_pk)
rownames(anova_pk) <- NULL
names(anova_pk) <- sub("^Pr\\(>F\\)$", "p", names(anova_pk))
write_table(anova_pk, "E3_group_by_prior_knowledge_anova.csv")

plot_pk <- ggplot(part_all, aes(x = prior_knowledge_familiarity, y = mean_mcq, color = experiment_group)) +
  geom_point(alpha = 0.75) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE) +
  labs(
    x = "Prior knowledge (familiarity mean)",
    y = "Mean MCQ accuracy",
    title = "Mean MCQ by Prior Knowledge × Group"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_pk, "E3_plot_group_by_prior_knowledge_mcq.png")

p_int_pk <- anova_pk$p[anova_pk$effect == "experiment_group:prior_knowledge_familiarity"]
if (length(p_int_pk) == 1 && !is.na(p_int_pk) && p_int_pk < 0.05) {
  pk_mean <- mean(part_all$prior_knowledge_familiarity, na.rm = TRUE)
  pk_sd <- sd(part_all$prior_knowledge_familiarity, na.rm = TRUE)
  at_vals <- c(pk_mean - pk_sd, pk_mean + pk_sd)
  emm_pk <- emmeans(m_pk, ~ experiment_group | prior_knowledge_familiarity, at = list(prior_knowledge_familiarity = at_vals))
  ph_pk <- as.data.frame(pairs(emm_pk, adjust = "holm"))
  write_table(ph_pk, "E3_group_simple_slopes_at_low_high_prior_knowledge.csv")
}
log_line(paste0("- Group×prior_knowledge interaction p ", format_p(p_int_pk)))

# 4) Time-on-task → outcomes (trial-level mixed models; log-transformed times)
log_line("E4) Time-on-task models (log-transformed due to skew)")

df_time_all <- df %>%
  filter(experiment_group %in% c("AI", "NoAI"), !is.na(mcq_accuracy), !is.na(reading_time_min)) %>%
  mutate(
    participant_id = factor(participant_id),
    article = factor(article),
    experiment_group = factor(experiment_group, levels = c("NoAI", "AI")),
    log_reading_time = log(reading_time_min + 1)
  )

m_read_base <- lmer(mcq_accuracy ~ log_reading_time + experiment_group + (1|participant_id) + (1|article),
                    data = df_time_all, REML = TRUE)
m_read_int <- lmer(mcq_accuracy ~ log_reading_time * experiment_group + (1|participant_id) + (1|article),
                   data = df_time_all, REML = TRUE)

write_table(fixed_effects_table(m_read_base), "E4A_mcq_log_reading_time_fixed_effects.csv")
write_table(anova_table_lmer(m_read_base), "E4A_mcq_log_reading_time_anova.csv")
write_table(fixed_effects_table(m_read_int), "E4A_mcq_log_reading_time_by_group_fixed_effects.csv")
write_table(anova_table_lmer(m_read_int), "E4A_mcq_log_reading_time_by_group_anova.csv")

grid_read <- expand.grid(
  log_reading_time = seq(min(df_time_all$log_reading_time, na.rm = TRUE), max(df_time_all$log_reading_time, na.rm = TRUE), length.out = 100),
  experiment_group = levels(df_time_all$experiment_group),
  participant_id = df_time_all$participant_id[1],
  article = df_time_all$article[1]
)
grid_read$pred <- predict(m_read_int, newdata = grid_read, re.form = NA, allow.new.levels = TRUE)

plot_read <- ggplot(df_time_all, aes(x = log_reading_time, y = mcq_accuracy, color = experiment_group)) +
  geom_point(alpha = 0.55) +
  geom_line(data = grid_read, aes(x = log_reading_time, y = pred, color = experiment_group), linewidth = 1.1) +
  labs(
    x = "log(reading_time_min + 1)",
    y = "MCQ accuracy",
    title = "MCQ accuracy vs reading time (trial-level)"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_read, "E4A_plot_mcq_by_log_reading_time.png")

df_time_ai <- df_ai %>%
  filter(!is.na(summary_time_sec), !is.na(ai_summary_accuracy)) %>%
  mutate(
    log_summary_time = log(summary_time_sec + 1),
    participant_id = factor(participant_id),
    article = factor(article)
  )

m_sumacc <- lmer(ai_summary_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article),
                data = df_time_ai, REML = TRUE)
write_table(fixed_effects_table(m_sumacc), "E4B_ai_summary_accuracy_log_summary_time_fixed_effects.csv")
write_table(anova_table_lmer(m_sumacc), "E4B_ai_summary_accuracy_log_summary_time_anova.csv")

df_time_ai_mcq <- df_ai %>%
  filter(!is.na(summary_time_sec), !is.na(mcq_accuracy)) %>%
  mutate(
    log_summary_time = log(summary_time_sec + 1),
    participant_id = factor(participant_id),
    article = factor(article)
  )
m_mcq_sumtime <- lmer(mcq_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article),
                      data = df_time_ai_mcq, REML = TRUE)
write_table(fixed_effects_table(m_mcq_sumtime), "E4B_mcq_accuracy_log_summary_time_fixed_effects.csv")
write_table(anova_table_lmer(m_mcq_sumtime), "E4B_mcq_accuracy_log_summary_time_anova.csv")

grid_sum <- expand.grid(
  log_summary_time = seq(min(df_time_ai$log_summary_time, na.rm = TRUE), max(df_time_ai$log_summary_time, na.rm = TRUE), length.out = 100),
  timing = levels(df_ai$timing),
  structure = levels(df_ai$structure),
  participant_id = df_ai$participant_id[1],
  article = df_ai$article[1]
)
grid_sum$pred <- predict(m_sumacc, newdata = grid_sum, re.form = NA, allow.new.levels = TRUE)
grid_sum_avg <- grid_sum %>% group_by(log_summary_time) %>% summarise(pred = mean(pred), .groups = "drop")

plot_sumacc <- ggplot(df_time_ai, aes(x = log_summary_time, y = ai_summary_accuracy)) +
  geom_point(alpha = 0.55) +
  geom_line(data = grid_sum_avg, aes(x = log_summary_time, y = pred), linewidth = 1.1, color = "#1f77b4") +
  labs(
    x = "log(summary_time_sec + 1)",
    y = "AI summary accuracy",
    title = "AI summary accuracy vs summary time (trial-level; marginal)"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_sumacc, "E4B_plot_ai_summary_accuracy_by_log_summary_time.png")

grid_sum_mcq <- grid_sum
grid_sum_mcq$pred <- predict(m_mcq_sumtime, newdata = grid_sum_mcq, re.form = NA, allow.new.levels = TRUE)
grid_sum_mcq_avg <- grid_sum_mcq %>% group_by(log_summary_time) %>% summarise(pred = mean(pred), .groups = "drop")

plot_mcq_sumtime <- ggplot(df_time_ai_mcq, aes(x = log_summary_time, y = mcq_accuracy)) +
  geom_point(alpha = 0.55) +
  geom_line(data = grid_sum_mcq_avg, aes(x = log_summary_time, y = pred), linewidth = 1.1, color = "#1f77b4") +
  labs(
    x = "log(summary_time_sec + 1)",
    y = "MCQ accuracy",
    title = "MCQ accuracy vs summary time (AI only; marginal)"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_mcq_sumtime, "E4B_plot_mcq_accuracy_by_log_summary_time.png")

# E4C) Does reading time predict article-only accuracy? (AI only)
df_time_ai_article <- df_ai %>%
  filter(!is.na(reading_time_min), !is.na(article_accuracy)) %>%
  mutate(
    log_reading_time = log(reading_time_min + 1),
    participant_id = factor(participant_id),
    article = factor(article)
  )
m_article_read <- lmer(article_accuracy ~ log_reading_time + timing + structure + (1|participant_id) + (1|article),
                       data = df_time_ai_article, REML = TRUE)
write_table(fixed_effects_table(m_article_read), "E4C_article_accuracy_log_reading_time_fixed_effects.csv")
anova_article_read <- anova_table_lmer(m_article_read)
write_table(anova_article_read, "E4C_article_accuracy_log_reading_time_anova.csv")
log_line(paste0("- AI only: article_accuracy ~ log_reading_time p ", format_p(anova_article_read$p[anova_article_read$effect == "log_reading_time"])))

log_line("")


# -----------------------------------------------------------------------------
# H) Recall-focused analyses (mixed models)
# -----------------------------------------------------------------------------

log_line("H) Recall-focused analyses (mixed models)")

# H1) Does recall relate to recognition performance?
# Note: NoAI rows have timing/structure == control, which are fully confounded with group.
# We therefore report (a) an all-participants model controlling for group + article, and
# (b) an AI-only model controlling for structure/timing + article.

log_line("H1) MCQ accuracy ~ recall_total_score")

df_h1_all <- df %>%
  filter(experiment_group %in% c("AI", "NoAI"), !is.na(mcq_accuracy), !is.na(recall_total_score), !is.na(article)) %>%
  mutate(
    participant_id = factor(participant_id),
    experiment_group = factor(experiment_group, levels = c("NoAI", "AI")),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors"))
  )

m_h1_all <- lmer(
  mcq_accuracy ~ recall_total_score + experiment_group + article + (1|participant_id),
  data = df_h1_all,
  REML = TRUE
)
write_table(fixed_effects_table(m_h1_all), "H1_mcq_by_recall_all_fixed_effects.csv")
write_table(anova_table_lmer(m_h1_all), "H1_mcq_by_recall_all_anova.csv")

coef_h1_all <- fixed_effects_table(m_h1_all)
p_h1_all <- coef_h1_all$p[coef_h1_all$term == "recall_total_score"]
beta_h1_all <- coef_h1_all$Estimate[coef_h1_all$term == "recall_total_score"]
log_line(paste0("- All participants: recall_total_score beta = ", sprintf("%.3f", beta_h1_all), ", p ", format_p(p_h1_all)))

plot_h1 <- ggplot(df_h1_all, aes(x = recall_total_score, y = mcq_accuracy, color = experiment_group)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE) +
  labs(
    x = "Recall total score",
    y = "MCQ accuracy",
    title = "MCQ accuracy vs recall (by group)"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_h1, "H1_plot_mcq_by_recall.png")

df_h1_ai <- df_ai %>%
  filter(!is.na(mcq_accuracy), !is.na(recall_total_score), !is.na(article)) %>%
  mutate(article = factor(article, levels = c("uhi", "crispr", "semiconductors")))

m_h1_ai <- lmer(
  mcq_accuracy ~ recall_total_score + timing + structure + article + (1|participant_id),
  data = df_h1_ai,
  REML = TRUE
)
write_table(fixed_effects_table(m_h1_ai), "H1_mcq_by_recall_ai_fixed_effects.csv")
write_table(anova_table_lmer(m_h1_ai), "H1_mcq_by_recall_ai_anova.csv")

coef_h1_ai <- fixed_effects_table(m_h1_ai)
p_h1_ai <- coef_h1_ai$p[coef_h1_ai$term == "recall_total_score"]
beta_h1_ai <- coef_h1_ai$Estimate[coef_h1_ai$term == "recall_total_score"]
log_line(paste0("- AI only (controls timing/structure): recall_total_score beta = ", sprintf("%.3f", beta_h1_ai), ", p ", format_p(p_h1_ai)))

log_line("")


# H2) What predicts recall? (process + individual differences)
log_line("H2) Recall total score predictors")

df_h2_all <- df %>%
  filter(experiment_group %in% c("AI", "NoAI"),
         !is.na(recall_total_score),
         !is.na(reading_time_min),
         !is.na(mental_effort),
         !is.na(prior_knowledge_familiarity),
         !is.na(article)) %>%
  mutate(
    participant_id = factor(participant_id),
    experiment_group = factor(experiment_group, levels = c("NoAI", "AI")),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors")),
    log_reading_time = log(reading_time_min + 1)
  )

m_h2_all <- lmer(
  recall_total_score ~ log_reading_time + mental_effort + prior_knowledge_familiarity + experiment_group + article + (1|participant_id),
  data = df_h2_all,
  REML = TRUE
)
write_table(fixed_effects_table(m_h2_all), "H2_recall_predictors_all_fixed_effects.csv")
write_table(anova_table_lmer(m_h2_all), "H2_recall_predictors_all_anova.csv")

anova_h2_all <- anova_table_lmer(m_h2_all)
log_line(paste0("- All participants: reading_time p ", format_p(anova_h2_all$p[anova_h2_all$effect == "log_reading_time"]),
                "; effort p ", format_p(anova_h2_all$p[anova_h2_all$effect == "mental_effort"]),
                "; prior knowledge p ", format_p(anova_h2_all$p[anova_h2_all$effect == "prior_knowledge_familiarity"])))

df_h2_ai <- df_ai %>%
  filter(!is.na(recall_total_score),
         !is.na(reading_time_min),
         !is.na(mental_effort),
         !is.na(summary_time_sec),
         !is.na(ai_summary_accuracy),
         !is.na(ai_trust),
         !is.na(ai_dependence),
         !is.na(prior_knowledge_familiarity),
         !is.na(article)) %>%
  mutate(
    participant_id = factor(participant_id),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors")),
    log_reading_time = log(reading_time_min + 1),
    log_summary_time = log(summary_time_sec + 1)
  )

m_h2_ai <- lmer(
  recall_total_score ~ log_reading_time + mental_effort + log_summary_time + ai_summary_accuracy +
    ai_trust + ai_dependence + prior_knowledge_familiarity + timing + structure + article + (1|participant_id),
  data = df_h2_ai,
  REML = TRUE
)
write_table(fixed_effects_table(m_h2_ai), "H2_recall_predictors_ai_fixed_effects.csv")
write_table(anova_table_lmer(m_h2_ai), "H2_recall_predictors_ai_anova.csv")

anova_h2_ai <- anova_table_lmer(m_h2_ai)
log_line(paste0("- AI only: ai_summary_accuracy p ", format_p(anova_h2_ai$p[anova_h2_ai$effect == "ai_summary_accuracy"]),
                "; summary_time p ", format_p(anova_h2_ai$p[anova_h2_ai$effect == "log_summary_time"]),
                "; trust p ", format_p(anova_h2_ai$p[anova_h2_ai$effect == "ai_trust"]),
                "; dependence p ", format_p(anova_h2_ai$p[anova_h2_ai$effect == "ai_dependence"])))

log_line("")


# H3) Recall confidence calibration (mixed-effects regression)
log_line("H3) Recall confidence calibration models")

df_h3_all <- df %>%
  filter(experiment_group %in% c("AI", "NoAI"),
         !is.na(recall_total_score),
         !is.na(recall_confidence),
         !is.na(article)) %>%
  mutate(
    participant_id = factor(participant_id),
    experiment_group = factor(experiment_group, levels = c("NoAI", "AI")),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors"))
  )

m_h3_all <- lmer(
  recall_total_score ~ recall_confidence * experiment_group + article + (1|participant_id),
  data = df_h3_all,
  REML = TRUE
)
write_table(fixed_effects_table(m_h3_all), "H3_recall_calibration_all_fixed_effects.csv")
write_table(anova_table_lmer(m_h3_all), "H3_recall_calibration_all_anova.csv")

anova_h3_all <- anova_table_lmer(m_h3_all)
log_line(paste0("- All participants: confidence p ", format_p(anova_h3_all$p[anova_h3_all$effect == "recall_confidence"]),
                "; confidence×group p ", format_p(anova_h3_all$p[anova_h3_all$effect == "recall_confidence:experiment_group"])))

grid_h3 <- expand.grid(
  recall_confidence = seq(min(df_h3_all$recall_confidence, na.rm = TRUE), max(df_h3_all$recall_confidence, na.rm = TRUE), length.out = 120),
  experiment_group = levels(df_h3_all$experiment_group),
  article = levels(df_h3_all$article),
  participant_id = df_h3_all$participant_id[1]
)
grid_h3$pred <- predict(m_h3_all, newdata = grid_h3, re.form = NA, allow.new.levels = TRUE)
grid_h3_avg <- grid_h3 %>%
  group_by(recall_confidence, experiment_group) %>%
  summarise(pred = mean(pred), .groups = "drop")

plot_h3 <- ggplot(df_h3_all, aes(x = recall_confidence, y = recall_total_score, color = experiment_group)) +
  geom_point(alpha = 0.55) +
  geom_line(data = grid_h3_avg, aes(x = recall_confidence, y = pred, color = experiment_group), linewidth = 1.1) +
  labs(
    x = "Recall confidence",
    y = "Recall total score",
    title = "Recall calibration: recall vs confidence (mixed model)"
  ) +
  theme_minimal(base_size = 12)
save_plot(plot_h3, "H3_plot_recall_calibration_by_group.png")

df_h3_ai <- df_ai %>%
  filter(!is.na(recall_total_score),
         !is.na(recall_confidence),
         !is.na(ai_trust),
         !is.na(ai_dependence),
         !is.na(article)) %>%
  mutate(
    participant_id = factor(participant_id),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors"))
  )

m_h3_ai_trust <- lmer(
  recall_total_score ~ recall_confidence * ai_trust + timing + structure + article + (1|participant_id),
  data = df_h3_ai,
  REML = TRUE
)
write_table(fixed_effects_table(m_h3_ai_trust), "H3_recall_calibration_ai_trust_fixed_effects.csv")
write_table(anova_table_lmer(m_h3_ai_trust), "H3_recall_calibration_ai_trust_anova.csv")

anova_h3_ai_trust <- anova_table_lmer(m_h3_ai_trust)
log_line(paste0("- AI only: confidence×trust p ", format_p(anova_h3_ai_trust$p[anova_h3_ai_trust$effect == "recall_confidence:ai_trust"])))

m_h3_ai_dep <- lmer(
  recall_total_score ~ recall_confidence * ai_dependence + timing + structure + article + (1|participant_id),
  data = df_h3_ai,
  REML = TRUE
)
write_table(fixed_effects_table(m_h3_ai_dep), "H3_recall_calibration_ai_dependence_fixed_effects.csv")
write_table(anova_table_lmer(m_h3_ai_dep), "H3_recall_calibration_ai_dependence_anova.csv")

anova_h3_ai_dep <- anova_table_lmer(m_h3_ai_dep)
log_line(paste0("- AI only: confidence×dependence p ", format_p(anova_h3_ai_dep$p[anova_h3_ai_dep$effect == "recall_confidence:ai_dependence"])))

log_line("")


# -----------------------------------------------------------------------------
# I) “AI buffer / cue” interpretation checks (AI only)
# -----------------------------------------------------------------------------

log_line("I) Buffer / cue interpretation checks (AI only)")

# I0) Does timing remain significant for AI-summary accuracy after controlling summary time?
log_line("I0) Timing contrasts on AI summary accuracy (base vs +log(summary_time))")

df_i0 <- df_ai %>%
  filter(!is.na(ai_summary_accuracy), !is.na(summary_time_sec)) %>%
  mutate(log_summary_time = log(summary_time_sec + 1))

m_i0_base <- lmer(
  ai_summary_accuracy ~ timing + structure + (1|participant_id) + (1|article),
  data = df_i0,
  REML = TRUE
)

m_i0_full <- lmer(
  ai_summary_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article),
  data = df_i0,
  REML = TRUE
)

write_table(fixed_effects_table(m_i0_base), "I0_ai_summary_accuracy_timing_only_fixed_effects.csv")
write_table(fixed_effects_table(m_i0_full), "I0_ai_summary_accuracy_timing_plus_log_summary_time_fixed_effects.csv")

emm_i0_base <- emmeans(m_i0_base, ~ timing)
pairs_i0_base <- pairs(emm_i0_base, adjust = "holm") %>% as.data.frame()
emm_i0_full <- emmeans(m_i0_full, ~ timing)
pairs_i0_full <- pairs(emm_i0_full, adjust = "holm") %>% as.data.frame()

write_table(pairs_i0_base, "I0_ai_summary_accuracy_timing_only_pairwise_holm.csv")
write_table(pairs_i0_full, "I0_ai_summary_accuracy_timing_plus_log_summary_time_pairwise_holm.csv")

extract_pre_contrasts <- function(pairs_df) {
  pairs_df %>%
    mutate(
      contrast = gsub("\\s+", " ", contrast),
      contrast = gsub("pre_reading", "Pre-reading", contrast),
      contrast = gsub("synchronous", "Synchronous", contrast),
      contrast = gsub("post_reading", "Post-reading", contrast)
    ) %>%
    filter(grepl("^Pre-reading - (Synchronous|Post-reading)$", contrast)) %>%
    select(contrast, estimate, SE, df, t.ratio, p.value) %>%
    arrange(contrast)
}

sig_stars <- function(p) {
  if (is.na(p)) return("")
  if (p < 0.001) return("***")
  if (p < 0.01) return("**")
  if (p < 0.05) return("*")
  ""
}

format_est_sig <- function(est, p) {
  paste0(sprintf("%.3f", est), sig_stars(p))
}

pre_base <- extract_pre_contrasts(pairs_i0_base)
pre_full <- extract_pre_contrasts(pairs_i0_full)

get_est <- function(d, contrast_label) {
  v <- d$estimate[d$contrast == contrast_label]
  if (length(v) == 0) return(NA_real_)
  v[[1]]
}
get_p <- function(d, contrast_label) {
  v <- d$p.value[d$contrast == contrast_label]
  if (length(v) == 0) return(NA_real_)
  v[[1]]
}

pre_sync_label <- "Pre-reading - Synchronous"
pre_post_label <- "Pre-reading - Post-reading"

base_pre_sync <- get_est(pre_base, pre_sync_label)
base_pre_post <- get_est(pre_base, pre_post_label)
full_pre_sync <- get_est(pre_full, pre_sync_label)
full_pre_post <- get_est(pre_full, pre_post_label)

reduction_pre_sync <- if (!is.na(base_pre_sync) && base_pre_sync != 0) (base_pre_sync - full_pre_sync) / base_pre_sync else NA_real_
reduction_pre_post <- if (!is.na(base_pre_post) && base_pre_post != 0) (base_pre_post - full_pre_post) / base_pre_post else NA_real_

summary_i0 <- data.frame(
  model = c("Base (timing only)", "+ log(summary_time)", "Reduction"),
  pre_sync = c(
    format_est_sig(base_pre_sync, get_p(pre_base, pre_sync_label)),
    format_est_sig(full_pre_sync, get_p(pre_full, pre_sync_label)),
    if (is.na(reduction_pre_sync)) "NA" else paste0(round(100 * reduction_pre_sync), "%")
  ),
  pre_post = c(
    format_est_sig(base_pre_post, get_p(pre_base, pre_post_label)),
    format_est_sig(full_pre_post, get_p(pre_full, pre_post_label)),
    if (is.na(reduction_pre_post)) "NA" else paste0(round(100 * reduction_pre_post), "%")
  )
)
write_table(summary_i0, "I0_timing_contrasts_summary_ai_summary_accuracy.csv")

log_summary_row <- fixed_effects_table(m_i0_full) %>% filter(term == "log_summary_time")
if (nrow(log_summary_row) == 1) {
  log_line(paste0(
    "- log(summary_time) effect: beta = ",
    sprintf("%.3f", log_summary_row$Estimate[[1]]),
    ", p ",
    format_p(log_summary_row$p)
  ))
}

m_i0_base_ml <- lmer(
  ai_summary_accuracy ~ timing + structure + (1|participant_id) + (1|article),
  data = df_i0,
  REML = FALSE
)
m_i0_full_ml <- lmer(
  ai_summary_accuracy ~ log_summary_time + timing + structure + (1|participant_id) + (1|article),
  data = df_i0,
  REML = FALSE
)
lrt_i0 <- anova(m_i0_base_ml, m_i0_full_ml)
lrt_i0_df <- as.data.frame(lrt_i0)
lrt_i0_df$model <- rownames(lrt_i0_df)
rownames(lrt_i0_df) <- NULL
write_table(lrt_i0_df, "I0_model_comparison_base_vs_log_summary_time_ml.csv")

write_table(fixed_effects_table(m_i0_full_ml), "I0_ai_summary_accuracy_timing_plus_log_summary_time_fixed_effects_ml.csv")

# I1) Summary time -> AI summary accuracy controlling for timing/structure/article
df_i1 <- df_ai %>%
  filter(!is.na(ai_summary_accuracy), !is.na(summary_time_sec), !is.na(article)) %>%
  mutate(
    log_summary_time = log(summary_time_sec + 1),
    article = factor(article, levels = c("uhi", "crispr", "semiconductors"))
  )

m_i1 <- lmer(
  ai_summary_accuracy ~ log_summary_time + timing + structure + article + (1|participant_id) + (1|article),
  data = df_i1,
  REML = TRUE
)
write_table(fixed_effects_table(m_i1), "I1_ai_summary_accuracy_log_summary_time_fixed_effects.csv")
write_table(anova_table_lmer(m_i1), "I1_ai_summary_accuracy_log_summary_time_anova.csv")

anova_i1 <- anova_table_lmer(m_i1)
log_line(paste0("- Summary time -> summary accuracy: p ", format_p(anova_i1$p[anova_i1$effect == "log_summary_time"])))

# I2) Summary time -> MCQ controlling for summary accuracy + article accuracy
df_i2 <- df_ai %>%
  filter(!is.na(mcq_accuracy),
         !is.na(summary_time_sec),
         !is.na(ai_summary_accuracy),
         !is.na(article_accuracy)) %>%
  mutate(log_summary_time = log(summary_time_sec + 1))

m_i2 <- lmer(
  mcq_accuracy ~ log_summary_time + ai_summary_accuracy + article_accuracy + timing + structure + (1|participant_id) + (1|article),
  data = df_i2,
  REML = TRUE
)
write_table(fixed_effects_table(m_i2), "I2_mcq_accuracy_log_summary_time_plus_summary_and_article_accuracy_fixed_effects.csv")
write_table(anova_table_lmer(m_i2), "I2_mcq_accuracy_log_summary_time_plus_summary_and_article_accuracy_anova.csv")

anova_i2 <- anova_table_lmer(m_i2)
log_line(paste0("- MCQ model: summary_time p ", format_p(anova_i2$p[anova_i2$effect == "log_summary_time"]),
                "; ai_summary_accuracy p ", format_p(anova_i2$p[anova_i2$effect == "ai_summary_accuracy"]),
                "; article_accuracy p ", format_p(anova_i2$p[anova_i2$effect == "article_accuracy"])))

log_line("")


# -----------------------------------------------------------------------------
# F) Confidence calibration (AI vs NoAI; and AI-only)
# -----------------------------------------------------------------------------

log_line("F) Confidence calibration")

# F1) Correlation: recall_confidence vs recall_total_score
run_corr <- function(d, label, filename) {
  d2 <- d %>% filter(!is.na(recall_confidence), !is.na(recall_total_score))
  ct <- cor.test(d2$recall_confidence, d2$recall_total_score)
  out <- data.frame(
    scope = label,
    n = nrow(d2),
    r = unname(ct$estimate),
    p = unname(ct$p.value),
    ci_low = ct$conf.int[1],
    ci_high = ct$conf.int[2]
  )
  write_table(out, filename)
  out
}

corr_all <- run_corr(df, "All (trial-level)", "F1_corr_all.csv")
corr_ai <- run_corr(df %>% filter(experiment_group == "AI"), "AI (trial-level)", "F1_corr_ai.csv")
corr_noai <- run_corr(df %>% filter(experiment_group == "NoAI"), "NoAI (trial-level)", "F1_corr_noai.csv")

log_line(paste0("- Correlation (all): r = ", sprintf("%.3f", corr_all$r), ", p ", format_p(corr_all$p)))

# F2) Overconfidence index + group comparison + AI-only structure×timing
df_over <- df %>%
  filter(!is.na(recall_confidence), !is.na(recall_total_score)) %>%
  mutate(
    z_conf = as.numeric(scale(recall_confidence)),
    z_score = as.numeric(scale(recall_total_score)),
    overconfidence = z_conf - z_score
  )

over_by_participant <- df_over %>%
  group_by(participant_id, experiment_group) %>%
  summarise(mean_overconfidence = mean(overconfidence, na.rm = TRUE), .groups = "drop")

t_over <- t.test(mean_overconfidence ~ experiment_group, data = over_by_participant, var.equal = TRUE)
over_desc <- over_by_participant %>%
  group_by(experiment_group) %>%
  summarise(n = n(), mean = mean(mean_overconfidence), sd = sd(mean_overconfidence), se = sd / sqrt(n), .groups = "drop")

write_table(over_desc, "F2_overconfidence_descriptives.csv")
write_table(
  data.frame(
    statistic = unname(t_over$statistic),
    df = unname(t_over$parameter),
    p = unname(t_over$p.value),
    mean_AI = over_desc$mean[over_desc$experiment_group == "AI"],
    mean_NoAI = over_desc$mean[over_desc$experiment_group == "NoAI"]
  ),
  "F2_overconfidence_group_ttest.csv"
)

df_over_ai <- df_over %>%
  filter(experiment_group == "AI", structure %in% c("integrated", "segmented"), timing %in% c("pre_reading", "synchronous", "post_reading")) %>%
  mutate(
    structure = factor(structure, levels = c("integrated", "segmented")),
    timing = factor(timing, levels = c("pre_reading", "synchronous", "post_reading"))
  )

m_over <- lmer(overconfidence ~ structure * timing + (1|participant_id) + (1|article), data = df_over_ai, REML = TRUE)
anova_over <- anova_table_lmer(m_over) %>% filter(effect %in% c("structure", "timing", "structure:timing"))
write_table(anova_over, "F2_overconfidence_ai_anova.csv")
means_plot(df_over_ai, "overconfidence", "Overconfidence (z(conf) − z(score))", "F2_plot_overconfidence.png")

log_line(paste0("- Overconfidence group t-test: p ", format_p(t_over$p.value)))
log_line("")


# -----------------------------------------------------------------------------
# G) Article effects (robustness)
# -----------------------------------------------------------------------------

log_line("G) Article effects (robustness)")

# G1) All participants: mcq_accuracy ~ experiment_group * article + (1|participant_id)
df_g1 <- df %>% filter(!is.na(mcq_accuracy))
df_g1$experiment_group <- factor(df_g1$experiment_group, levels = c("NoAI", "AI"))
df_g1$article <- factor(df_g1$article, levels = c("uhi", "crispr", "semiconductors"))

m_g1 <- lmer(mcq_accuracy ~ experiment_group * article + (1|participant_id), data = df_g1, REML = TRUE)
anova_g1 <- anova_table_lmer(m_g1)
write_table(anova_g1, "G1_mcq_group_by_article_anova.csv")
write_table(fixed_effects_table(m_g1), "G1_mcq_group_by_article_fixed_effects.csv")

log_line(paste0("- MCQ: group×article interaction p ", format_p(anova_g1$p[anova_g1$effect == "experiment_group:article"])))

# G2) AI only: ai_summary_accuracy ~ structure * timing + article + (1|participant_id)
m_g2 <- lmer(ai_summary_accuracy ~ structure * timing + article + (1|participant_id),
             data = df_ai %>% filter(!is.na(ai_summary_accuracy)),
            REML = TRUE)
anova_g2 <- anova_table_lmer(m_g2)
write_table(anova_g2, "G2_ai_summary_with_article_fixed_anova.csv")
write_table(fixed_effects_table(m_g2), "G2_ai_summary_with_article_fixed_effects.csv")

log_line("")


# -----------------------------------------------------------------------------
# Write report
# -----------------------------------------------------------------------------

writeLines(report_lines, con = report_path)
message("Done. Outputs written to: ", out_root)
