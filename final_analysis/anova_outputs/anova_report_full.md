# ANOVA full results (generated)
- Wide source: `analysis_wide_format.xlsx` / `Foglio 1 - analysis_wide_format`
- Long source: `Analysis long finals-corrected.xlsx` / `1`

## MCQ accuracy (AI vs NoAI)
### From wide: total_mcq_accuracy
#### Descriptives
```csv
experiment_group,n,mean,sd
AI,24,0.598208,0.0846422
NoAI,12,0.509925,0.0976008
```
#### ANOVA
```csv
dv,F,df1,df2,p,partial_eta2
total_mcq_accuracy,7.86438,1,34,0.00827446,0.187854
```

### From long: mean(mcq_accuracy) across 3 trials
#### Descriptives
```csv
experiment_group,n,mean,sd
AI,24,0.598204,0.084646
NoAI,12,0.509928,0.097613
```
#### ANOVA
```csv
dv,F,df1,df2,p,partial_eta2
mcq_accuracy_mean,7.86195,1,34,0.00828349,0.187807
```

## AI summary accuracy (AI only; 2×3 mixed ANOVA)
### Sphericity (Timing)
- Mauchly: W = 0.887, chi2(2) = 2.650, p = 0.266
- Greenhouse–Geisser epsilon: 0.898

### Descriptives (Structure × Timing)
```csv
structure,timing,n,mean,sd
integrated,post_reading,12,0.6666666666666666,0.21541
integrated,pre_reading,12,0.8541666666666666,0.149177
integrated,synchronous,12,0.5416666666666666,0.257464
segmented,post_reading,12,0.6145833333333334,0.180422
segmented,pre_reading,12,0.8125,0.135889
segmented,synchronous,12,0.59375,0.226917
```
### ANOVA table
```csv
effect,SS,df1,df2,F,p,partial_eta2,df1_GG,df2_GG,p_GG
Structure,0.00347222,1,22,0.0641399,0.80242,0.00290698,,,
Timing,0.90408,2,44,13.9969,1.97449e-05,0.388837,1.7962,39.5163,4.47756e-05
Structure×Timing,0.0394965,2,44,0.611484,0.547091,0.0270431,1.7962,39.5163,0.530659
```
### Post hoc tests
```csv
contrast,mean_diff,t,p,cohen_dz,p_holm
pre_reading vs synchronous,0.265625,4.47225,0.000173473,0.912894,0.000520418
pre_reading vs post_reading,0.192708,4.26992,0.000287338,0.871593,0.000574677
synchronous vs post_reading,-0.0729167,-1.49685,0.148031,-0.305543,0.148031
```
### Figure of means
- `plot_ai_summary_accuracy.png` (error bars: ±SE)

## False lures selected (AI only; 2×3 mixed ANOVA)
### Sphericity (Timing)
- Mauchly: W = 0.981, chi2(2) = 0.433, p = 0.805
- Greenhouse–Geisser epsilon: 0.981

### Descriptives (Structure × Timing)
```csv
structure,timing,n,mean,sd
integrated,post_reading,12,0.5,0.6742
integrated,pre_reading,12,0.8333333333333334,0.717741
integrated,synchronous,12,0.4166666666666667,0.668558
segmented,post_reading,12,1.1666666666666667,0.717741
segmented,pre_reading,12,0.9166666666666666,0.792961
segmented,synchronous,12,1.0833333333333333,0.900337
```
### ANOVA table
```csv
effect,SS,df1,df2,F,p,partial_eta2,df1_GG,df2_GG,p_GG
Structure,4.01389,1,22,4.7377,0.0405216,0.177192,,,
Timing,0.194444,2,44,0.231928,0.793967,0.0104322,1.96175,43.1586,0.789822
Structure×Timing,1.36111,2,44,1.62349,0.208799,0.0687237,1.96175,43.1586,0.209358
```
### Post hoc tests
```csv
contrast,mean_integrated,mean_segmented,t,df,p,cohen_d
integrated vs segmented (subject mean across timing),0.583333,1.05556,-2.17663,22,0.0405216,-0.888604
```
### Figure of means
- `plot_false_lures_selected.png` (error bars: ±SE)

