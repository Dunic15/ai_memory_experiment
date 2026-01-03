#!/usr/bin/env python3
"""
Mixed Design ANOVA Analysis for AI Memory Experiment
=====================================================
Analysis 1: MCQ Accuracy - AI (all conditions) vs Non-AI
Analysis 2: AI Summary Accuracy - 2x3 Mixed Design (Structure x Timing)
Analysis 3: False Lures Selected - 2x3 Mixed Design (Structure x Timing)

Factors:
- Structure (between-subjects, 2 levels): Integrated, Segmented
- Timing (within-subjects, 3 levels): Pre, Sync, After
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Try to import required packages
try:
    import pingouin as pg
except ImportError:
    print("Installing pingouin...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pingouin', '-q'])
    import pingouin as pg

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Installing matplotlib...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'matplotlib', '-q'])
    import matplotlib.pyplot as plt

try:
    import seaborn as sns
except ImportError:
    print("Installing seaborn...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'seaborn', '-q'])
    import seaborn as sns

import os

# Set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create output directory
output_dir = os.path.join(script_dir, "anova_outputs")
os.makedirs(output_dir, exist_ok=True)

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

# Read data
df = pd.read_excel("Analysis long finals-.xlsx")
print(f"\nData loaded: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Columns: {df.columns.tolist()}")
print(f"\nExperiment groups: {df['experiment_group'].unique()}")
print(f"Structure levels: {df['structure'].unique()}")
print(f"Timing levels: {df['timing'].unique()}")

# ============================================================================
# ANALYSIS 1: MCQ Accuracy - AI vs Non-AI
# ============================================================================
print("\n")
print("#" * 70)
print("ANALYSIS 1: MCQ ACCURACY - AI vs NON-AI")
print("#" * 70)

# Calculate mean MCQ accuracy per participant
mcq_by_participant = df.groupby(['participant_id', 'experiment_group']).agg({
    'mcq_accuracy': 'mean'
}).reset_index()

# Descriptive statistics
print("\nDescriptive Statistics:")
mcq_desc = mcq_by_participant.groupby('experiment_group').agg({
    'mcq_accuracy': ['count', 'mean', 'std']
}).round(4)
mcq_desc.columns = ['n', 'mean', 'sd']
mcq_desc['se'] = mcq_desc['sd'] / np.sqrt(mcq_desc['n'])
print(mcq_desc)

# Separate groups
ai_mcq = mcq_by_participant[mcq_by_participant['experiment_group'] == 'AI']['mcq_accuracy']
noai_mcq = mcq_by_participant[mcq_by_participant['experiment_group'] == 'NoAI']['mcq_accuracy']

# Independent samples t-test
t_stat, p_value = stats.ttest_ind(ai_mcq, noai_mcq)
print(f"\nIndependent Samples t-test:")
print(f"  t = {t_stat:.4f}")
print(f"  p = {p_value:.4f}")
print(f"  df = {len(ai_mcq) + len(noai_mcq) - 2}")

# Cohen's d
pooled_std = np.sqrt(((len(ai_mcq)-1)*ai_mcq.std()**2 + (len(noai_mcq)-1)*noai_mcq.std()**2) / 
                     (len(ai_mcq) + len(noai_mcq) - 2))
cohens_d = (ai_mcq.mean() - noai_mcq.mean()) / pooled_std
print(f"\nEffect Size:")
print(f"  Cohen's d = {cohens_d:.4f}")

# Interpretation
if p_value < 0.05:
    print(f"\n✓ SIGNIFICANT: AI and Non-AI groups differ in MCQ accuracy")
else:
    print(f"\n✗ NOT SIGNIFICANT: No difference between AI and Non-AI groups in MCQ accuracy")

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
mcq_plot_data = mcq_desc.reset_index()
bars = ax.bar(mcq_plot_data['experiment_group'], mcq_plot_data['mean'], 
              yerr=mcq_plot_data['se'], capsize=5, color=['#66c2a5', '#fc8d62'])
ax.set_xlabel('Experiment Group')
ax.set_ylabel('MCQ Accuracy (Mean ± SE)')
ax.set_title('MCQ Accuracy: AI vs Non-AI')
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'mcq_accuracy_ai_vs_noai.png'), dpi=150)
plt.close()

# ============================================================================
# ANALYSIS 2: AI Summary Accuracy - 2x3 Mixed Design ANOVA
# ============================================================================
print("\n")
print("#" * 70)
print("ANALYSIS 2: AI SUMMARY ACCURACY - 2x3 MIXED DESIGN ANOVA")
print("(Structure: between-subjects, Timing: within-subjects)")
print("#" * 70)

# Filter to AI group only
df_ai = df[(df['experiment_group'] == 'AI') & 
           (df['structure'] != 'control') & 
           (df['timing'] != 'control')].copy()

# Convert numeric columns to proper numeric type
df_ai['ai_summary_accuracy'] = pd.to_numeric(df_ai['ai_summary_accuracy'], errors='coerce')
df_ai['false_lures_selected'] = pd.to_numeric(df_ai['false_lures_selected'], errors='coerce')
df_ai['mcq_accuracy'] = pd.to_numeric(df_ai['mcq_accuracy'], errors='coerce')

print(f"\nData subset for AI conditions:")
print(f"  Structure levels: {df_ai['structure'].unique()}")
print(f"  Timing levels: {df_ai['timing'].unique()}")
print(f"  N observations: {len(df_ai)}")

# Descriptive Statistics
print("\n" + "-" * 50)
print("DESCRIPTIVE STATISTICS - AI Summary Accuracy")
print("-" * 50)

summary_desc = df_ai.groupby(['structure', 'timing']).agg({
    'ai_summary_accuracy': ['count', 'mean', 'std']
}).round(4)
summary_desc.columns = ['n', 'mean', 'sd']
summary_desc['se'] = summary_desc['sd'] / np.sqrt(summary_desc['n'])
print("\nCell Means (Structure × Timing):")
print(summary_desc)

# Marginal means
print("\nMarginal Means - Structure:")
struct_means = df_ai.groupby('structure')['ai_summary_accuracy'].agg(['mean', 'std', 'count']).round(4)
print(struct_means)

print("\nMarginal Means - Timing:")
timing_means = df_ai.groupby('timing')['ai_summary_accuracy'].agg(['mean', 'std', 'count']).round(4)
print(timing_means)

# Run Mixed ANOVA
print("\n" + "-" * 50)
print("MIXED ANOVA RESULTS - AI Summary Accuracy")
print("-" * 50)

# Using pingouin mixed_anova
anova_summary = pg.mixed_anova(
    data=df_ai,
    dv='ai_summary_accuracy',
    within='timing',
    between='structure',
    subject='participant_id'
)

print("\nANOVA Table:")
print(anova_summary.to_string())

# Check sphericity
print("\n" + "-" * 50)
print("SPHERICITY TEST (Mauchly's)")
print("-" * 50)
spher = pg.sphericity(df_ai, dv='ai_summary_accuracy', within='timing', subject='participant_id')
print(f"Mauchly's W = {spher[0]:.4f}")
print(f"Chi-square = {spher[1]:.4f}")
print(f"p-value = {spher[2]:.4f}")
if spher[2] < 0.05:
    print("⚠ Sphericity violated - use Greenhouse-Geisser corrected p-values")
else:
    print("✓ Sphericity assumption met")

# Post-hoc analyses
print("\n" + "-" * 50)
print("POST-HOC ANALYSES - AI Summary Accuracy")
print("-" * 50)

# Check which effects are significant
structure_sig = anova_summary[anova_summary['Source'] == 'structure']['p-unc'].values[0] < 0.05
timing_sig = anova_summary[anova_summary['Source'] == 'timing']['p-unc'].values[0] < 0.05
interaction_sig = anova_summary[anova_summary['Source'] == 'Interaction']['p-unc'].values[0] < 0.05

print(f"\nSignificance Summary:")
print(f"  Main Effect of Structure: p = {anova_summary[anova_summary['Source'] == 'structure']['p-unc'].values[0]:.4f} {'✓ SIG' if structure_sig else '✗ NS'}")
print(f"  Main Effect of Timing: p = {anova_summary[anova_summary['Source'] == 'timing']['p-unc'].values[0]:.4f} {'✓ SIG' if timing_sig else '✗ NS'}")
print(f"  Interaction (Structure × Timing): p = {anova_summary[anova_summary['Source'] == 'Interaction']['p-unc'].values[0]:.4f} {'✓ SIG' if interaction_sig else '✗ NS'}")

if interaction_sig:
    print("\n>>> INTERACTION SIGNIFICANT - Performing Simple Effects Analysis <<<")
    
    # Simple effects of timing within each structure level
    print("\nSimple Effects of Timing WITHIN Integrated:")
    df_integrated = df_ai[df_ai['structure'] == 'integrated']
    timing_integrated = pg.rm_anova(data=df_integrated, dv='ai_summary_accuracy', 
                                      within='timing', subject='participant_id')
    print(timing_integrated.to_string())
    
    # Pairwise comparisons within integrated
    print("\nPairwise Comparisons (Timing within Integrated):")
    pw_integrated = pg.pairwise_tests(data=df_integrated, dv='ai_summary_accuracy',
                                       within='timing', subject='participant_id',
                                       padjust='holm')
    print(pw_integrated[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    print("\nSimple Effects of Timing WITHIN Segmented:")
    df_segmented = df_ai[df_ai['structure'] == 'segmented']
    timing_segmented = pg.rm_anova(data=df_segmented, dv='ai_summary_accuracy',
                                    within='timing', subject='participant_id')
    print(timing_segmented.to_string())
    
    # Pairwise comparisons within segmented
    print("\nPairwise Comparisons (Timing within Segmented):")
    pw_segmented = pg.pairwise_tests(data=df_segmented, dv='ai_summary_accuracy',
                                      within='timing', subject='participant_id',
                                      padjust='holm')
    print(pw_segmented[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    # Simple effects of structure at each timing level
    print("\nSimple Effects of Structure AT Each Timing Level:")
    for timing_level in df_ai['timing'].unique():
        df_timing = df_ai[df_ai['timing'] == timing_level]
        t_result = pg.ttest(df_timing[df_timing['structure'] == 'integrated']['ai_summary_accuracy'],
                           df_timing[df_timing['structure'] == 'segmented']['ai_summary_accuracy'])
        print(f"\n  {timing_level}: t = {t_result['T'].values[0]:.3f}, p = {t_result['p-val'].values[0]:.4f}, Cohen's d = {t_result['cohen-d'].values[0]:.3f}")

else:
    # Main effects post-hoc
    if timing_sig:
        print("\n>>> MAIN EFFECT OF TIMING SIGNIFICANT - Performing Pairwise Comparisons <<<")
        # Need to average over structure for main effect comparison
        timing_posthoc = pg.pairwise_tests(data=df_ai, dv='ai_summary_accuracy',
                                            within='timing', subject='participant_id',
                                            padjust='holm')
        print("\nPairwise Comparisons for Timing (Holm-corrected):")
        print(timing_posthoc[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    if structure_sig:
        print("\n>>> MAIN EFFECT OF STRUCTURE SIGNIFICANT <<<")
        print("(Only 2 levels - no post-hoc needed, effect already tested in ANOVA)")
        print(f"  Integrated: M = {df_ai[df_ai['structure'] == 'integrated']['ai_summary_accuracy'].mean():.4f}")
        print(f"  Segmented: M = {df_ai[df_ai['structure'] == 'segmented']['ai_summary_accuracy'].mean():.4f}")

# Interaction plot
fig, ax = plt.subplots(figsize=(10, 7))
summary_plot_data = summary_desc.reset_index()

for structure in ['integrated', 'segmented']:
    data = summary_plot_data[summary_plot_data['structure'] == structure]
    ax.errorbar(data['timing'], data['mean'], yerr=data['se'], 
                marker='o', markersize=8, linewidth=2, capsize=5, label=structure)

ax.set_xlabel('Timing', fontsize=12)
ax.set_ylabel('AI Summary Accuracy (Mean ± SE)', fontsize=12)
ax.set_title('AI Summary Accuracy: Structure × Timing Interaction', fontsize=14)
ax.legend(title='Structure')
ax.set_ylim(0, 1)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'ai_summary_accuracy_interaction.png'), dpi=150)
plt.close()

# ============================================================================
# ANALYSIS 3: False Lures Selected - 2x3 Mixed Design ANOVA
# ============================================================================
print("\n")
print("#" * 70)
print("ANALYSIS 3: FALSE LURES SELECTED - 2x3 MIXED DESIGN ANOVA")
print("(Structure: between-subjects, Timing: within-subjects)")
print("#" * 70)

# Descriptive Statistics
print("\n" + "-" * 50)
print("DESCRIPTIVE STATISTICS - False Lures Selected")
print("-" * 50)

lures_desc = df_ai.groupby(['structure', 'timing']).agg({
    'false_lures_selected': ['count', 'mean', 'std']
}).round(4)
lures_desc.columns = ['n', 'mean', 'sd']
lures_desc['se'] = lures_desc['sd'] / np.sqrt(lures_desc['n'])
print("\nCell Means (Structure × Timing):")
print(lures_desc)

# Marginal means
print("\nMarginal Means - Structure:")
struct_means_lures = df_ai.groupby('structure')['false_lures_selected'].agg(['mean', 'std', 'count']).round(4)
print(struct_means_lures)

print("\nMarginal Means - Timing:")
timing_means_lures = df_ai.groupby('timing')['false_lures_selected'].agg(['mean', 'std', 'count']).round(4)
print(timing_means_lures)

# Run Mixed ANOVA
print("\n" + "-" * 50)
print("MIXED ANOVA RESULTS - False Lures Selected")
print("-" * 50)

anova_lures = pg.mixed_anova(
    data=df_ai,
    dv='false_lures_selected',
    within='timing',
    between='structure',
    subject='participant_id'
)

print("\nANOVA Table:")
print(anova_lures.to_string())

# Check sphericity
print("\n" + "-" * 50)
print("SPHERICITY TEST (Mauchly's)")
print("-" * 50)
spher_lures = pg.sphericity(df_ai, dv='false_lures_selected', within='timing', subject='participant_id')
print(f"Mauchly's W = {spher_lures[0]:.4f}")
print(f"Chi-square = {spher_lures[1]:.4f}")
print(f"p-value = {spher_lures[2]:.4f}")
if spher_lures[2] < 0.05:
    print("⚠ Sphericity violated - use Greenhouse-Geisser corrected p-values")
else:
    print("✓ Sphericity assumption met")

# Post-hoc analyses
print("\n" + "-" * 50)
print("POST-HOC ANALYSES - False Lures Selected")
print("-" * 50)

# Check which effects are significant
structure_sig_l = anova_lures[anova_lures['Source'] == 'structure']['p-unc'].values[0] < 0.05
timing_sig_l = anova_lures[anova_lures['Source'] == 'timing']['p-unc'].values[0] < 0.05
interaction_sig_l = anova_lures[anova_lures['Source'] == 'Interaction']['p-unc'].values[0] < 0.05

print(f"\nSignificance Summary:")
print(f"  Main Effect of Structure: p = {anova_lures[anova_lures['Source'] == 'structure']['p-unc'].values[0]:.4f} {'✓ SIG' if structure_sig_l else '✗ NS'}")
print(f"  Main Effect of Timing: p = {anova_lures[anova_lures['Source'] == 'timing']['p-unc'].values[0]:.4f} {'✓ SIG' if timing_sig_l else '✗ NS'}")
print(f"  Interaction (Structure × Timing): p = {anova_lures[anova_lures['Source'] == 'Interaction']['p-unc'].values[0]:.4f} {'✓ SIG' if interaction_sig_l else '✗ NS'}")

if interaction_sig_l:
    print("\n>>> INTERACTION SIGNIFICANT - Performing Simple Effects Analysis <<<")
    
    # Simple effects of timing within each structure level
    print("\nSimple Effects of Timing WITHIN Integrated:")
    df_integrated = df_ai[df_ai['structure'] == 'integrated']
    timing_integrated_l = pg.rm_anova(data=df_integrated, dv='false_lures_selected', 
                                       within='timing', subject='participant_id')
    print(timing_integrated_l.to_string())
    
    print("\nPairwise Comparisons (Timing within Integrated):")
    pw_integrated_l = pg.pairwise_tests(data=df_integrated, dv='false_lures_selected',
                                         within='timing', subject='participant_id',
                                         padjust='holm')
    print(pw_integrated_l[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    print("\nSimple Effects of Timing WITHIN Segmented:")
    df_segmented = df_ai[df_ai['structure'] == 'segmented']
    timing_segmented_l = pg.rm_anova(data=df_segmented, dv='false_lures_selected',
                                      within='timing', subject='participant_id')
    print(timing_segmented_l.to_string())
    
    print("\nPairwise Comparisons (Timing within Segmented):")
    pw_segmented_l = pg.pairwise_tests(data=df_segmented, dv='false_lures_selected',
                                        within='timing', subject='participant_id',
                                        padjust='holm')
    print(pw_segmented_l[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    # Simple effects of structure at each timing level
    print("\nSimple Effects of Structure AT Each Timing Level:")
    for timing_level in df_ai['timing'].unique():
        df_timing = df_ai[df_ai['timing'] == timing_level]
        t_result = pg.ttest(df_timing[df_timing['structure'] == 'integrated']['false_lures_selected'],
                           df_timing[df_timing['structure'] == 'segmented']['false_lures_selected'])
        print(f"\n  {timing_level}: t = {t_result['T'].values[0]:.3f}, p = {t_result['p-val'].values[0]:.4f}, Cohen's d = {t_result['cohen-d'].values[0]:.3f}")

else:
    if timing_sig_l:
        print("\n>>> MAIN EFFECT OF TIMING SIGNIFICANT - Performing Pairwise Comparisons <<<")
        timing_posthoc_l = pg.pairwise_tests(data=df_ai, dv='false_lures_selected',
                                              within='timing', subject='participant_id',
                                              padjust='holm')
        print("\nPairwise Comparisons for Timing (Holm-corrected):")
        print(timing_posthoc_l[['Contrast', 'A', 'B', 'T', 'p-unc', 'p-corr', 'hedges']].to_string())
    
    if structure_sig_l:
        print("\n>>> MAIN EFFECT OF STRUCTURE SIGNIFICANT <<<")
        print(f"  Integrated: M = {df_ai[df_ai['structure'] == 'integrated']['false_lures_selected'].mean():.4f}")
        print(f"  Segmented: M = {df_ai[df_ai['structure'] == 'segmented']['false_lures_selected'].mean():.4f}")

# Interaction plot
fig, ax = plt.subplots(figsize=(10, 7))
lures_plot_data = lures_desc.reset_index()

for structure in ['integrated', 'segmented']:
    data = lures_plot_data[lures_plot_data['structure'] == structure]
    ax.errorbar(data['timing'], data['mean'], yerr=data['se'], 
                marker='o', markersize=8, linewidth=2, capsize=5, label=structure)

ax.set_xlabel('Timing', fontsize=12)
ax.set_ylabel('False Lures Selected (Mean ± SE)', fontsize=12)
ax.set_title('False Lures Selected: Structure × Timing Interaction', fontsize=14)
ax.legend(title='Structure')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'false_lures_interaction.png'), dpi=150)
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n")
print("#" * 70)
print("SUMMARY OF ALL ANALYSES")
print("#" * 70)

print("\n" + "=" * 70)
print("ANALYSIS 1: MCQ Accuracy (AI vs Non-AI)")
print("=" * 70)
print(f"  t({len(ai_mcq) + len(noai_mcq) - 2}) = {t_stat:.3f}, p = {p_value:.4f}")
print(f"  AI: M = {ai_mcq.mean():.3f}, SD = {ai_mcq.std():.3f} (n = {len(ai_mcq)})")
print(f"  NoAI: M = {noai_mcq.mean():.3f}, SD = {noai_mcq.std():.3f} (n = {len(noai_mcq)})")
print(f"  Cohen's d = {cohens_d:.3f}")
if p_value < 0.05:
    print("  RESULT: SIGNIFICANT difference between AI and Non-AI groups")
else:
    print("  RESULT: No significant difference between groups")

print("\n" + "=" * 70)
print("ANALYSIS 2: AI Summary Accuracy (2×3 Mixed ANOVA)")
print("=" * 70)
print(anova_summary[['Source', 'DF1', 'DF2', 'F', 'p-unc', 'np2']].to_string())

print("\n" + "=" * 70)
print("ANALYSIS 3: False Lures Selected (2×3 Mixed ANOVA)")
print("=" * 70)
print(anova_lures[['Source', 'DF1', 'DF2', 'F', 'p-unc', 'np2']].to_string())

print(f"\n\nPlots saved to: {output_dir}")
print("\nAnalysis complete!")

# Save summary to file
with open(os.path.join(output_dir, 'anova_summary_results.txt'), 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("MIXED DESIGN ANOVA ANALYSIS - SUMMARY RESULTS\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("ANALYSIS 1: MCQ Accuracy (AI vs Non-AI)\n")
    f.write("-" * 50 + "\n")
    f.write(f"t({len(ai_mcq) + len(noai_mcq) - 2}) = {t_stat:.3f}, p = {p_value:.4f}\n")
    f.write(f"AI: M = {ai_mcq.mean():.3f}, SD = {ai_mcq.std():.3f} (n = {len(ai_mcq)})\n")
    f.write(f"NoAI: M = {noai_mcq.mean():.3f}, SD = {noai_mcq.std():.3f} (n = {len(noai_mcq)})\n")
    f.write(f"Cohen's d = {cohens_d:.3f}\n\n")
    
    f.write("\nANALYSIS 2: AI Summary Accuracy (2×3 Mixed ANOVA)\n")
    f.write("-" * 50 + "\n")
    f.write(anova_summary.to_string() + "\n\n")
    
    f.write("\nANALYSIS 3: False Lures Selected (2×3 Mixed ANOVA)\n")
    f.write("-" * 50 + "\n")
    f.write(anova_lures.to_string() + "\n")

print("\nResults also saved to: anova_outputs/anova_summary_results.txt")
