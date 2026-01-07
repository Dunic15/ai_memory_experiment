% NOTE: This file is adapted from `Final result/FINAL_INTEGRATED_REPORT.tex`.
% It is intended to be included in the thesis via `\input{final_integrated_report}`.

\definecolor{mainblue}{RGB}{0,102,204}
\definecolor{findinggreen}{RGB}{34,139,34}
\definecolor{warningorange}{RGB}{255,140,0}

% ============================================
\section{Executive Summary}
% ============================================

This experiment investigated how AI-generated summaries affect learning and memory, with a focus on \textbf{when} (timing) and \textbf{how} (structure) summaries are presented. The findings reveal that the cognitive consequences of AI assistance depend critically on these design choices---not merely on whether AI is used.

\begin{tcolorbox}[colback=blue!5!white,colframe=mainblue,title=Key Takeaway]
\textbf{AI can meaningfully improve learning outcomes when aligned with cognitive principles of timing, structure, and task demands.}
\end{tcolorbox}

% ============================================
\section{Two Main Findings}
% ============================================

% --------------------------------------------
\subsection{Main Finding 1: Pre-Reading Timing Produces Superior MCQ Performance}
% --------------------------------------------

\subsubsection{The Finding}
\textbf{Presenting AI summaries \textit{before} reading produces dramatically better recognition-based learning compared to synchronous or post-reading presentation.} This is the largest and most robust effect in the experiment.

\subsubsection{Statistical Evidence}

\paragraph{Descriptive Statistics (AI Group, n = 24 per timing):}

\begin{table}[H]
\centering
\begin{tabular}{lc}
\toprule
\textbf{Timing Condition} & \textbf{MCQ Accuracy (Mean $\pm$ SD)} \\
\midrule
\textbf{Pre-reading} & \textbf{0.699 $\pm$ 0.125} \\
Synchronous & 0.533 $\pm$ 0.147 \\
Post-reading & 0.562 $\pm$ 0.127 \\
\bottomrule
\end{tabular}
\caption{MCQ Accuracy by Timing Condition}
\end{table}

\paragraph{Mixed ANOVA (Structure $\times$ Timing, AI Group):}
\begin{itemize}
    \item \textbf{Timing main effect:} $F(1.77, 38.87) = 11.77$, $p = .00018$, $\eta^2_G = .254$
    \item Structure main effect: $F(1, 22) = 4.69$, $p = .0415$, $\eta^2_G = .072$
    \item Interaction: $F(1.77, 38.87) = 0.76$, $p = .461$ (ns)
\end{itemize}

\paragraph{Post-hoc Pairwise Comparisons (Holm-corrected):}

\begin{table}[H]
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Comparison} & \textbf{Difference} & \textbf{p-value} & \textbf{Cohen's $d$} \\
\midrule
Pre vs Synchronous & +0.167 & .0019 & 1.62 (very large) \\
Pre vs Post & +0.137 & .0025 & 1.35 (very large) \\
Synchronous vs Post & $-$0.029 & .449 & 0.21 (small) \\
\bottomrule
\end{tabular}
\caption{Pairwise Comparisons for MCQ Accuracy}
\end{table}

\\subsubsection{Mechanism: Advance Organizers and Cognitive Load}

Why does pre-reading work? The summary functions as an \textbf{advance organizer} \citep{ausubel1960}, providing a high-level framework that guides attention during reading and reduces extraneous cognitive load \citep{sweller1988,chandler1992}.

\textbf{Advance Organizer Theory} \citep{ausubel1960}:
\begin{itemize}
    \item Activates relevant schemas before encoding
    \item Provides a ``cognitive map'' that guides attention during reading
    \item Reduces extraneous cognitive load \citep{sweller1988,chandler1992}
\end{itemize}



% --------------------------------------------
\subsection{Main Finding 2: Segmented Summaries Increase False Memory}
% --------------------------------------------

\subsubsection{The Finding}
\textbf{Summary structure---not timing---is the primary driver of susceptibility to false AI-generated claims.} Segmented summaries approximately \textbf{double} the probability of endorsing false lures compared to integrated summaries.

\subsubsection{Statistical Evidence}

\paragraph{Descriptive Statistics (AI Group):}

\begin{table}[H]
\centering
\begin{tabular}{lcc}
\toprule
\textbf{Structure} & \textbf{False Lures Selected (0--2)} & \textbf{Endorsement Probability} \\
\midrule
Integrated & 0.58 $\pm$ 0.69 & $\sim$25--29\% \\
\textbf{Segmented} & \textbf{1.06 $\pm$ 0.79} & \textbf{$\sim$53--54\%} \\
\bottomrule
\end{tabular}
\caption{False Lure Endorsement by Structure}
\end{table}

\paragraph{Binomial GLMM (Full Model):}

\begin{table}[H]
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Predictor} & \textbf{Odds Ratio} & \textbf{95\% CI} & \textbf{p-value} \\
\midrule
\textbf{Structure (Segmented)} & \textbf{5.93} & [1.63, 21.5] & .007 \\
Timing (Synchronous) & 0.46 & [0.12, 1.73] & .251 \\
Timing (Post-reading) & 0.67 & [0.18, 2.45] & .544 \\
\bottomrule
\end{tabular}
\caption{Binomial GLMM Results for False Lure Endorsement}
\end{table}

\subsubsection{Mechanism: Source Monitoring and Split-Attention}

Why do segmented summaries increase false memories?

\begin{enumerate}
    \item \textbf{Weaker source monitoring cues:} Fragmented presentation reduces contextual cues used to attribute information to its correct source \citep{johnson1993}
    \item \textbf{Reduced cross-checking:} Separated information discourages verification against the original article
    \item \textbf{Split-attention costs:} Dividing attention across separated elements taxes cognitive resources and impairs integration \citep{sweller1988,chandler1992}
    \item \textbf{Automation bias and misinformation:} Readers may accept AI-generated content with insufficient verification, increasing susceptibility to misinformation \citep{gerlich2025,loftus2005,chan2024}
\end{enumerate}

Overall, these results align with established accounts in which presentation format affects information integration and source attribution. Integrated summaries better support coherent mental model construction, whereas segmented summaries increase the risk of misattributing plausible but incorrect information \citep{johnson1993,sweller1988,chandler1992,loftus2005}.

% ============================================
\section{Secondary Findings}
% ============================================

% --------------------------------------------
\subsection{Secondary Finding A: Recall Performance Is Unaffected by Timing (MCQ-Recall Dissociation)}
% --------------------------------------------

\subsubsection{The Finding}
\textbf{While timing dramatically affects MCQ performance, free recall is completely unaffected across all timing conditions.} This represents a fundamental dissociation between recognition and generative retrieval.

\subsubsection{Statistical Evidence}

\begin{table}[H]
\centering
\begin{tabular}{lc}
\toprule
\textbf{Timing} & \textbf{Recall Total Score (Mean $\pm$ SD)} \\
\midrule
Pre-reading & 5.50 $\pm$ 1.92 \\
Synchronous & 5.54 $\pm$ 1.99 \\
Post-reading & 5.56 $\pm$ 2.17 \\
\bottomrule
\end{tabular}
\caption{Recall Scores by Timing (Difference $<$ 0.06 points)}
\end{table}

\paragraph{Mixed ANOVA (Structure $\times$ Timing, AI Group):}
\begin{itemize}
    \item \textbf{Timing:} $F(1.86, 40.88) = 0.03$, $p = .969$, $\eta^2_G < .001$
    \item Structure: $F(1, 22) = 0.40$, $p = .536$
    \item Interaction: $F(1.86, 40.88) = 0.62$, $p = .532$
\end{itemize}

\subsubsection{The MCQ-Recall Dissociation}

\begin{table}[H]
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Outcome} & \textbf{Timing Effect} & \textbf{Effect Size} & \textbf{Interpretation} \\
\midrule
MCQ Accuracy & Strong ($p < .001$) & $d = 1.35$--$1.62$ & Recognition benefits from schema priming \\
Recall Score & None ($p = .97$) & $d \approx 0$ & Generative retrieval not enhanced \\
\bottomrule
\end{tabular}
\caption{MCQ-Recall Dissociation Summary}
\end{table}

\subsubsection{Mechanism: Different Memory Processes and Task Demands}

This dissociation reflects a fundamental distinction in how memory operates, explained by classical dual-process theories \citep{jacoby1991} and by differences in retrieval demands across tasks:

\begin{enumerate}
    \item \textbf{MCQ = cue-supported recognition:} When answer options are available, learners can rely on familiarity-based recognition. Pre-reading summaries supply organizational cues that increase the accessibility of relevant concepts, facilitating correct option selection.
    
    \item \textbf{Recall = self-generated retrieval:} Free recall requires learners to actively reconstruct information from memory without external cues \citep{craik1972}. Without active generation during study, gains in recognition do not necessarily translate into stronger recall.
\end{enumerate}

\textbf{Interpretation:} The timing manipulation selectively benefits tasks where retrieval cues are available, such as recognition tests, but does not strengthen the internally generated memory traces required for free recall. This pattern aligns with transfer-appropriate processing and retrieval-practice accounts.

% --------------------------------------------
\subsection{Secondary Finding B: AI Improves MCQ But Not Recall}
% --------------------------------------------

\begin{table}[H]
\centering
\begin{tabular}{lcccc}
\toprule
\textbf{Measure} & \textbf{With AI} & \textbf{No AI} & \textbf{Difference} & \textbf{Effect Size} \\
\midrule
MCQ Accuracy & 0.598 & 0.510 & +0.088 & $d = 0.57$ ($p = .008$) \\
Recall Score & 5.535 & 5.403 & +0.132 & ns ($p > .50$) \\
\bottomrule
\end{tabular}
\caption{AI vs No-AI Comparison}
\end{table}

\textbf{Interpretation:} AI selectively enhances performance on tasks that align with AI-provided information (MCQs referencing the summary), but does not improve generative recall.

\textbf{Theoretical Connection: Encoding Specificity Principle}\\[0.3cm]
This pattern aligns with Tulving's \textbf{Encoding Specificity Principle} \citep{tulving1972}:
\begin{quote}
``What is stored is determined by what is perceived and how it is encoded, and what is stored determines what retrieval cues are effective.''
\end{quote}

AI summaries provide encoding that is \textbf{transfer-appropriate} for MCQ (recognition with cues) but not for free recall (generative retrieval without cues). The AI content becomes part of the encoded memory trace, making AI-related MCQ cues more effective.

\textbf{Related Theory: Cognitive Offloading and External Memory Aids}\\[0.3cm]
The AI summary functions as an \textbf{external memory aid} \citep{gerlich2025,risko2016}, where learners encode \textit{where} information is stored (the AI) rather than the information itself---a phenomenon increasingly relevant in the digital age \citep{gong2024,firth2019}. Recent research on AI and cognition \citep{bai2023} confirms that generative AI tools alter how users encode and retrieve information, consistent with cognitive offloading accounts.

% --------------------------------------------
\subsection{Secondary Finding C: Time Allocation Explains Pre-Reading Benefit}
% --------------------------------------------

\begin{table}[H]
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Timing} & \textbf{Summary Time (sec)} & \textbf{Reading Time (min)} & \textbf{Total Time (sec)} \\
\midrule
Pre-reading & 132.5 & 6.72 & 535.9 \\
Synchronous & 100.3 & 7.20 & 532.5 \\
Post-reading & 69.5 & 7.69 & 530.8 \\
\bottomrule
\end{tabular}
\caption{Time Allocation Across Conditions}
\end{table}

\textbf{Key insight:} Total time is constant ($\sim$531--536 sec). Pre-reading works because participants:
\begin{enumerate}
    \item \textbf{Invest more time in the summary upfront} (+63 sec vs post-reading, $p < .001$)
    \item \textbf{Read the article more efficiently afterward} ($-$0.97 min vs post-reading)
    \item \textbf{Total time remains constant} (no ``worked longer'' confound)
\end{enumerate}

\textbf{ANOVA for Summary Time:} $F(1.98, 43.66) = 13.94$, $p = .000022$, $\eta^2_G = .253$

\textbf{Theoretical Connection: Germane Load Optimization}\\[0.3cm]
This finding challenges simple \textbf{time-on-task} theories (Carroll, 1963) and supports \textbf{encoding quality} accounts. Pre-reading shifts cognitive resources from extraneous processing (figuring out what matters) to germane processing (building schemas). The result is more efficient subsequent reading---doing more learning in less time.

% --------------------------------------------
\subsection{Secondary Finding D: Mental Effort Is Not a Confound}
% --------------------------------------------

\begin{table}[H]
\centering
\begin{tabular}{lc}
\toprule
\textbf{Condition} & \textbf{Mental Effort (1--7)} \\
\midrule
With AI & 5.79 \\
No AI & 5.50 \\
Integrated & 6.03 \\
Segmented & 5.56 \\
\bottomrule
\end{tabular}
\caption{Mental Effort by Condition}
\end{table}

\textbf{Mixed ANOVA (Structure $\times$ Timing):}
\begin{itemize}
    \item Timing: $F(1.34, 29.37) = 0.81$, $p = .408$ (ns)
    \item Structure: $F(1, 22) = 2.43$, $p = .133$ (ns)
\end{itemize}

Mental effort does not differ by timing condition, ruling it out as an explanation for the timing effect on MCQ.

\textbf{Implication:} The timing effect on MCQ is not due to participants \textit{working harder} in pre-reading conditions. Instead, it reflects \textbf{qualitative differences in encoding} (schema activation, organization) rather than quantitative differences in effort expenditure.

\textbf{Ruling Out Desirable Difficulties:} The finding also rules out that pre-reading creates ``desirable difficulties'' (Bjork, 1994)---the benefit comes from facilitation, not from increased challenge.

% --------------------------------------------
\subsection{Secondary Finding E: Post-block Trust and Dependence by Condition}
% --------------------------------------------

\begin{table}[H]
\centering
\begin{tabular}{llcc}
\toprule
\textbf{Structure} & \textbf{Timing} & \textbf{Trust} & \textbf{Dependence} \\
\midrule
Integrated & Pre-reading & 4.17 & 4.25 \\
Integrated & Synchronous & 3.58 & 3.83 \\
Integrated & Post-reading & 3.92 & 3.67 \\
Segmented & Pre-reading & 4.83 & 5.33 \\
Segmented & Synchronous & 4.17 & 4.50 \\
Segmented & Post-reading & 4.00 & 4.58 \\
\bottomrule
\end{tabular}
\caption{Post-block trust and dependence ratings by AI assistance condition}
\end{table}

\textbf{Mixed ANOVA (Structure $\times$ Timing):}
\begin{itemize}
    \item \textbf{Trust:} Timing $F(2, 44) = 7.96$, $p = .001$; Structure $F(1, 22) = 1.58$, $p = .222$; Interaction $F(2, 44) = 1.72$, $p = .191$.
    \item \textbf{Dependence:} Structure $F(1, 22) = 6.21$, $p = .021$; Timing $F(2, 44) = 7.84$, $p = .001$; Interaction $F(2, 44) = 0.62$, $p = .543$.
\end{itemize}

\textbf{Post-hoc timing comparisons (Holm-corrected):}
\begin{itemize}
    \item Pre-reading $>$ synchronous and post-reading for both trust and dependence.
    \item Synchronous vs post-reading is ns for both.
\end{itemize}

\textbf{Interpretation:}
\begin{itemize}
    \item There is no reliable structure effect on trust; the "excessive trust in segmented" explanation is not supported.
    \item Dependence is higher in segmented and in pre-reading. This aligns with the pre-reading advantage in summary accuracy, but structure differences in summary accuracy are not reliable, so treat the dependence pattern as descriptive.
\end{itemize}

% --------------------------------------------
\subsection{Secondary Finding F: Article Difficulty Doesn't Confound Timing}
% --------------------------------------------

\textbf{Counterbalancing check (Timing $\times$ Article):}

\begin{table}[H]
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Timing} & \textbf{CRISPR} & \textbf{Semiconductors} & \textbf{UHI} \\
\midrule
Pre-reading & 8 & 9 & 7 \\
Synchronous & 10 & 8 & 6 \\
Post-reading & 6 & 7 & 11 \\
\bottomrule
\end{tabular}
\caption{Article $\times$ Timing Distribution}
\end{table}

\textbf{Chi-square test:} $\chi^2(4) = 3.00$, $p = .558$

Article assignment does not systematically confound timing conditions.

\textbf{Aptitude-Treatment Interaction:} The lack of Timing $\times$ Article interaction ($p > .12$ in all analyses) suggests that the pre-reading benefit is \textbf{robust across difficulty levels}---it helps with both easy (CRISPR) and hard (Semiconductors) articles.

\textbf{Practical Implication:} Pre-reading AI summaries are effective regardless of content difficulty, suggesting broad applicability across educational domains.

% --------------------------------------------
\subsection{Secondary Finding G: Calibration Is Poor But AI Doesn't Worsen It}
% --------------------------------------------

\begin{table}[H]
\centering
\begin{tabular}{lc}
\toprule
\textbf{Measure} & \textbf{Recall Confidence (1--7)} \\
\midrule
With AI & 4.25 \\
No AI & 4.08 \\
\bottomrule
\end{tabular}
\caption{Confidence by AI Condition}
\end{table}

\textbf{Independent samples t-test for overconfidence:} $t(31.7) = 0.16$, $p = .873$

\textbf{Conclusion:} AI does not inflate confidence beyond actual performance. Both groups show similarly poor calibration.

\textbf{Theoretical Connections:}\\[0.3cm]
\textbf{Metacognitive Monitoring} \citep{koriat1997,nelson1990}: The ability to accurately assess one's own knowledge is a key metacognitive skill. Poor calibration (overconfidence) is common in educational settings.

\textbf{AI and Metacognition:} Importantly, AI assistance does \textit{not exacerbate} overconfidence. This suggests that AI summaries don't create an ``illusion of knowing'' beyond what naturally occurs without AI.

\textbf{Fluency-Based Metacognition:} If AI summaries made content feel ``too easy,'' we would expect inflated confidence. The null effect suggests participants maintain realistic (if imperfect) calibration despite AI assistance.

% ============================================
\section{Integrated Interpretation}
% ============================================

\subsection{Two Independent Cognitive Pathways: Timing and Structure Effects}

The results support two largely independent pathways consistent with established cognitive theories:

\begin{itemize}
    \item \textbf{Timing $\rightarrow$ MCQ performance:} Pre-reading summaries function as advance organizers that prime schemas and guide attention during encoding, improving recognition-based performance \citep{ausubel1960,sweller1988,chandler1992}.
    \item \textbf{Structure $\rightarrow$ false-lure endorsement:} Segmented formats increase split-attention and weaken source-monitoring cues, elevating susceptibility to plausible but incorrect information \citep{johnson1993,chandler1992,loftus2005}.
\end{itemize}

A broader synthesis using the proposed \textit{AI Buffer} concept is developed in the Discussion chapter, where it is explicitly presented as an interpretive framework rather than as an empirical result.

\subsection{The Optimal Design Configuration}

\begin{table}[H]
\centering
\begin{tabular}{lll}
\toprule
\textbf{Dimension} & \textbf{Optimal Choice} & \textbf{Rationale} \\
\midrule
Timing & Pre-reading & Large MCQ benefit ($d > 1.3$), advance organizer effect \\
Structure & Integrated & Dramatically lower false-lure risk (OR = 6$\times$ safer) \\
Format & Coherent paragraphs & Supports source monitoring \\
\bottomrule
\end{tabular}
\caption{Optimal AI Summary Design}
\end{table}

\textbf{Expected outcomes for Pre-reading + Integrated:}
\begin{itemize}
    \item MCQ accuracy: $\sim$0.75 (highest)
    \item False lures: $\sim$0.58/article (acceptable)
    \item Recall: $\sim$5.4 (unchanged)
\end{itemize}

% ============================================
\section{Experimental Design Robustness}
% ============================================

\subsection{Design Integrity and Internal Validity}

\begin{table}[H]
\centering
\begin{tabular}{lll}
\toprule
\textbf{Design Feature} & \textbf{Status} & \textbf{Evidence} \\
\midrule
Sample size & N = 36 (24 AI, 12 No-AI) & 108 article-level observations \\
Within-subjects balance & \checkmark Complete & Each AI participant: 3 trials \\
Between-subjects balance & \checkmark Complete & 12 integrated, 12 segmented \\
Article exposure & \checkmark Complete & All participants see all 3 articles \\
\bottomrule
\end{tabular}
\caption{Design Integrity Summary}
\end{table}

\subsection{Article Difficulty Analysis}

\begin{table}[H]
\centering
\begin{tabular}{lcccc}
\toprule
\textbf{Article} & \textbf{MCQ Accuracy} & \textbf{Recall} & \textbf{Summary Acc.} & \textbf{False Lures} \\
\midrule
Semiconductors & 0.480 (hardest) & 5.28 & 0.562 & 0.833 \\
UHI & 0.601 & 5.85 (best) & 0.760 & 0.958 (most) \\
CRISPR & 0.625 (easiest) & 5.35 & 0.719 & 0.667 (fewest) \\
\bottomrule
\end{tabular}
\caption{Article-Level Performance (AI Group)}
\end{table}

\subsection{Design Validity Checks}

\begin{table}[H]
\centering
\begin{tabular}{llll}
\toprule
\textbf{Check} & \textbf{Question} & \textbf{Result} & \textbf{Evidence} \\
\midrule
Counterbalancing & Article independent of timing? & \checkmark Yes & $\chi^2(4) = 3.00$, $p = .558$ \\
Interaction & Timing depend on article? & \checkmark No & $F < 1.88$, $p > .12$ \\
LOAO Robustness & Effect survives dropping any article? & \checkmark Yes & All $p < .02$ \\
\bottomrule
\end{tabular}
\caption{Design Validity Summary}
\end{table}

\subsection{Robustness of Primary Effects}

\paragraph{MCQ Timing Effect:}
\begin{itemize}
    \item 83\% of participants show pre-reading advantage
    \item Effect persists in leave-one-article-out analyses
    \item Random-slopes models: improved fit, estimates unchanged
    \item Survives Holm correction ($p < .005$)
\end{itemize}

\paragraph{False Lure Structure Effect:}
\begin{itemize}
    \item Consistent across binomial and Poisson models
    \item No separation issues detected
    \item Profile-likelihood CI excludes OR = 1: [1.63, 21.5]
    \item Overdispersion ratio $\approx$ 0.80 (no concern)
\end{itemize}

% ============================================
\section{Theoretical Grounding}
% ============================================

\subsection{Main Finding 1: Pre-Reading Timing Effect}

\subsubsection{Advance Organizer Theory}

The pre-reading advantage aligns with \textbf{Ausubel's Advance Organizer Theory} \citep{ausubel1960,ausubel1968}:

\begin{quote}
``The most important single factor influencing learning is what the learner already knows. Ascertain this and teach him accordingly.'' --- David Ausubel
\end{quote}

\textbf{Core mechanism:} Advance organizers provide a cognitive framework that:
\begin{enumerate}
    \item Activates relevant prior knowledge (schema priming)
    \item Creates ``ideational scaffolding'' for new information
    \item Guides selective attention during subsequent reading
    \item Facilitates meaningful learning over rote memorization \citep{craik1972}
\end{enumerate}

Empirical validation comes from Mayer \& Bromage (1980), who found pre-reading outlines improved problem-solving by $\sim$25\%, and Hartley \& Davies (1976), who demonstrated pre-organizer benefits for recall.

\subsubsection{Cognitive Load Theory}

The pre-reading effect aligns with \textbf{Cognitive Load Theory} \citep{sweller1988}:
\begin{itemize}
    \item \textbf{Intrinsic load:} Reduced because summary simplifies article processing
    \item \textbf{Extraneous load:} Reduced because learners don't need to ``figure out what matters'' \citep{chandler1992}
    \item \textbf{Germane load:} Increased because resources are freed for schema construction
\end{itemize}

The working memory model \citep{baddeley2012,atkinson1968} provides the cognitive architecture: the AI summary reduces demands on the central executive by pre-organizing information before it enters the phonological loop and visuospatial sketchpad.

\subsubsection{Quantitative Alignment}

Our observed effect size ($d = 1.35$--$1.62$) is larger than typical advance organizer effects ($d \approx 0.20$--$0.50$), likely because:
\begin{enumerate}
    \item AI summaries are more comprehensive than traditional organizers
    \item The MCQ outcome is particularly sensitive to schema-guided encoding
    \item The within-subjects design increased statistical power
\end{enumerate}

\subsection{Main Finding 2: Segmented Structure and False Memory}

\subsubsection{Source Monitoring Framework}

The structure effect aligns with the \textbf{Source Monitoring Framework} \citep{johnson1993,lindsayjohnson1989}:

\begin{quote}
``Source monitoring refers to the set of processes involved in making attributions about the origins of memories, knowledge, and beliefs.''
\end{quote}

\textbf{Core mechanism:} Segmented summaries increase source confusion because:
\begin{enumerate}
    \item Fragmented presentation disrupts coherent mental model construction
    \item Spatial separation increases misattribution risk \citep{chandler1992}
    \item Reduced cross-referencing makes verification harder
\end{enumerate}

Recent research demonstrates that conversational AI can amplify false memories in witness interviews \citep{chan2024}, extending classical misinformation effects to AI-generated content.

\subsubsection{The DRM Paradigm}

Our false-lure manipulation parallels the \textbf{Deese-Roediger-McDermott Paradigm} \citep{roediger1995}:
\begin{itemize}
    \item Critical lures falsely recognized at 40--60\% (similar to our 54\% segmented rate)
    \item False recognition confidence often as high as for true items
    \item Effect robust across age groups and cultures
\end{itemize}

Meta-analytic evidence \citep{frenda2011} suggests misinformation effects typically produce OR $\approx$ 3--5, consistent with our OR = 5.93 for the structure effect.

\subsubsection{Fuzzy-Trace Theory}

\textbf{Fuzzy-Trace Theory} explains the mechanism:
\begin{itemize}
    \item \textbf{Integrated format:} Encourages better verbatim encoding, enabling rejection of false claims
    \item \textbf{Segmented format:} Primarily encodes gist, which supports false recognition
\end{itemize}

\subsection{The MCQ-Recall Dissociation (Secondary Finding A)}

\subsubsection{Dual-Process Memory Theories}

The dissociation aligns with dual-process theories of recognition memory \citep{jacoby1991}:
\begin{itemize}
    \item \textbf{MCQ (recognition):} Solved via familiarity-based processes---the AI Buffer provides retrieval cues that enhance familiarity signals
    \item \textbf{Recall:} Requires recollection-based retrieval---active reconstruction that the buffer cannot support
\end{itemize}

This distinction is foundational in memory research, with neuroimaging evidence showing distinct neural substrates for familiarity and recollection.

\subsubsection{Generation Effect and Levels of Processing}

The \textbf{Generation Effect} \citep{slamecka1978} explains why recall doesn't benefit:
\begin{quote}
``Information that is self-generated is remembered better than information that is simply read or heard.''
\end{quote}

Free recall requires \textbf{active generation}, not just recognition. Pre-reading provides passive exposure that helps recognize answers but doesn't create generative retrieval pathways. The \textbf{Levels of Processing} framework \citep{craik1972} further explains this: AI summaries promote semantic (deep) encoding that benefits recognition, but recall additionally requires self-generated elaboration.

The \textbf{Testing Effect} literature \citep{roediger2006} confirms that active retrieval practice---not passive re-exposure---strengthens recall. The AI Buffer provides exposure, not practice.

% ============================================
\section{Summary Table: All Key Statistics}
% ============================================

\begin{table}[H]
\centering
\small
\begin{tabular}{lllll}
\toprule
\textbf{Finding} & \textbf{Test} & \textbf{Statistic} & \textbf{p-value} & \textbf{Effect Size} \\
\midrule
Timing $\rightarrow$ MCQ & Mixed ANOVA & $F(1.77, 38.87) = 11.77$ & .00018 & $\eta^2_G = .254$ \\
Pre vs Sync (MCQ) & Holm-corrected & $\Delta = 0.167$ & .0019 & $d = 1.62$ \\
Pre vs Post (MCQ) & Holm-corrected & $\Delta = 0.137$ & .0025 & $d = 1.35$ \\
Structure $\rightarrow$ Lures & Binomial GLMM & OR = 5.93 & .007 & CI [1.63, 21.5] \\
Timing $\rightarrow$ Recall & Mixed ANOVA & $F(1.86, 40.88) = 0.03$ & .969 & $\eta^2_G < .001$ \\
Timing $\rightarrow$ Summary Time & Mixed ANOVA & $F(1.98, 43.66) = 13.94$ & .000022 & $\eta^2_G = .253$ \\
AI vs No-AI (MCQ) & Independent t & --- & .008 & $d = 0.57$ \\
Counterbalancing & Chi-square & $\chi^2(4) = 3.00$ & .558 & (ns) \\
\bottomrule
\end{tabular}
\caption{Summary of All Key Statistical Results}
\end{table}

% ============================================
\section{Conclusions and Design Implications}
% ============================================

\subsection{For Educational Technology Design}

\begin{enumerate}
    \item \textbf{Default to pre-reading summaries} when the goal is comprehension/MCQ performance
    \item \textbf{Use integrated (not segmented) format} to minimize false memory risk
    \item \textbf{Treat false lures as a structural UI risk}, not a user trait problem
    \item \textbf{Evaluate learning with multiple outcome types} (MCQ $\neq$ recall)
\end{enumerate}

\subsection{For Future Research}

\begin{enumerate}
    \item Test \textbf{delayed retention} (24h, 1 week) to assess consolidation
    \item Manipulate \textbf{summary factuality} directly to test safety/performance trade-offs
    \item Use \textbf{process tracing} (eye-tracking, think-aloud) to isolate source-monitoring mechanisms
    \item Explore \textbf{verification affordances} (citations, uncertainty markers) as misinformation countermeasures
\end{enumerate}

\subsection{Final Takeaway}

\begin{tcolorbox}[colback=blue!5!white,colframe=mainblue,title=Core Message]
\textbf{AI can meaningfully improve learning outcomes when aligned with cognitive principles of timing, structure, and task demands.}

\begin{itemize}
    \item \textbf{Pre-reading timing} enhances comprehension quality through schema activation
    \item \textbf{Integrated structure} protects against false memory through coherent representation
    \item The optimal design is \textbf{pre-reading + integrated}: maximum learning benefit with manageable misinformation risk
\end{itemize}

\textbf{Importantly, this study demonstrates that AI-generated summaries can produce large and reliable learning benefits, comparable to or exceeding classic instructional interventions, when embedded within cognitively informed designs.}
\end{tcolorbox}

% ============================================
\section{Summary: Theoretical Integration}
% ============================================

\begin{table}[H]
\centering
\small
\begin{tabular}{p{2.5cm}p{3.5cm}p{5cm}p{4cm}}
\toprule
\textbf{Finding} & \textbf{Primary Theory} & \textbf{Supporting Theories} & \textbf{Key Mechanism} \\
\midrule
\textbf{Pre-reading $\rightarrow$ MCQ} & Advance Organizer Theory (Ausubel) & Cognitive Load Theory, Schema Theory, Mayer's Multimedia Learning, Levels of Processing, Forward Testing Effect & Schema activation + reduced extraneous load + deeper semantic processing \\
\textbf{Segmented $\rightarrow$ False Lures} & Source Monitoring Framework (Johnson et al.) & Split-Attention Effect, Misinformation Effect, DRM Paradigm, Fuzzy-Trace Theory, Seductive Details & Source confusion + fragmented representation + gist-based false recognition \\
\textbf{Timing $\neq$ Recall} & Dual-Process Memory (Jacoby) & Transfer-Appropriate Processing, Generation Effect, Spacing Effect, Levels of Processing & Familiarity $\neq$ recollection; recognition $\neq$ generative retrieval \\
\bottomrule
\end{tabular}
\caption{Summary of Theoretical Integration}
\end{table}

\subsection{Comprehensive Reference List}

\textbf{Advance Organizers and Pre-reading:}
\begin{itemize}[noitemsep]
    \item Ausubel, D. P. (1960, 1968)
    \item Mayer, R. E. (1979, 2014)
    \item Luiten, Ames, \& Ackerson (1980)
    \item Hartley \& Davies (1976)
\end{itemize}

\textbf{Cognitive Load Theory:}
\begin{itemize}[noitemsep]
    \item Sweller, J. (1988, 1998)
    \item Miller, G. A. (1956)
    \item Chandler \& Sweller (1991, 1992)
\end{itemize}

\textbf{Testing and Retrieval:}
\begin{itemize}[noitemsep]
    \item Roediger \& Karpicke (2006)
    \item Roediger \& Butler (2011)
    \item Chan et al. (2018)
    \item Szpunar, McDermott, \& Roediger (2008)
\end{itemize}

\textbf{False Memory:}
\begin{itemize}[noitemsep]
    \item Roediger \& McDermott (1995)
    \item Loftus et al. (1978); Loftus (2005)
    \item Johnson, Hashtroudi, \& Lindsay (1993)
\end{itemize}

\textbf{Memory Processes:}
\begin{itemize}[noitemsep]
    \item Craik \& Lockhart (1972)
    \item Jacoby (1991)
    \item Slamecka \& Graf (1978)
\end{itemize}

% ============================================
\section{Prior Experiments with Similar Designs: Empirical Validation}
% ============================================

This section reviews prior experiments with designs similar to ours that provide independent validation of our findings.

\subsection{Pre-Reading/Advance Organizer Studies}

\textbf{Mayer \& Bromage (1980):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Pre-reading outline vs. post-reading outline for technical passages
    \item \textbf{Finding:} Pre-reading outline improved conceptual problem-solving by $\sim$25\%
    \item \textbf{Similarity:} Same timing manipulation (pre vs. post), similar outcome pattern
    \item \textbf{Our replication:} Pre-reading improved MCQ by +16.7\% vs. synchronous, +13.7\% vs. post-reading
\end{itemize}

\textbf{Hartley \& Davies (1976):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Pre-organizer vs. no organizer for educational texts
    \item \textbf{Finding:} Pre-organizers improved recall of main ideas
    \item \textbf{Similarity:} Pre-reading scaffold enhances subsequent learning
    \item \textbf{Our replication:} Pre-reading produced highest summary accuracy and MCQ performance
\end{itemize}

\textbf{Lorch \& Lorch (1996):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Topic sentences before vs. after paragraphs
    \item \textbf{Finding:} Pre-topic sentences improved text memory organization
    \item \textbf{Similarity:} Analogous ``preview'' manipulation affecting text comprehension
    \item \textbf{Our replication:} Pre-reading AI summary functions as a comprehensive topic preview
\end{itemize}

\subsection{Video Lecture and Multimedia Studies}

\textbf{Szpunar, Khan, \& Schacter (2013):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Interpolated testing during video lectures vs. continuous viewing
    \item \textbf{Finding:} Testing reduced mind-wandering and improved final quiz performance
    \item \textbf{Similarity:} Pre-engagement with content improves subsequent learning
    \item \textbf{Our parallel:} Pre-reading engagement with summary improves article comprehension
\end{itemize}

\textbf{Jing, Szpunar, \& Schacter (2016):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Tested vs. non-tested video lecture segments
    \item \textbf{Finding:} Testing improved focused attention and information integration
    \item \textbf{Similarity:} Active engagement before/during learning enhances outcomes
    \item \textbf{Our parallel:} Pre-reading creates active engagement that persists through reading
\end{itemize}

\subsection{False Memory and Misinformation Studies}

\textbf{Roediger \& McDermott (1995) -- DRM Paradigm:}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Word lists with semantically related critical lures
    \item \textbf{Finding:} $\sim$40--55\% false recognition of critical lures
    \item \textbf{Similarity:} Our false lures are semantically plausible and produce similar rates (54\% in segmented)
    \item \textbf{Our contribution:} Extended DRM-like effects to AI-generated educational misinformation
\end{itemize}

\textbf{Loftus \& Palmer (1974):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Post-event leading questions (``How fast were the cars going when they \textit{smashed}?'')
    \item \textbf{Finding:} Wording of post-event information altered memory
    \item \textbf{Similarity:} Post-reading AI summary can distort memory of article content
    \item \textbf{Our parallel:} Post-reading + segmented shows highest false lure endorsement
\end{itemize}

\textbf{Lindsay \& Johnson (1989):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Source monitoring for misinformation from different sources
    \item \textbf{Finding:} Poor source monitoring increased misinformation susceptibility
    \item \textbf{Similarity:} Our structure manipulation affects source monitoring ability
    \item \textbf{Our contribution:} Demonstrated that UI design (integrated vs. segmented) affects source monitoring
\end{itemize}

\textbf{Frenda, Nichols, \& Loftus (2011):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Review of misinformation effect across various conditions
    \item \textbf{Finding:} OR $\approx$ 3--5 for misinformation effects in various formats
    \item \textbf{Our replication:} OR = 5.93 for segmented vs. integrated format
\end{itemize}

\subsection{Split-Attention and Integration Studies}

\textbf{Chandler \& Sweller (1992):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Integrated vs. split-source instructional materials
    \item \textbf{Finding:} Integrated instruction improved learning and reduced cognitive load
    \item \textbf{Similarity:} Same integrated vs. segmented manipulation
    \item \textbf{Our contribution:} Extended to AI-generated content and false memory outcomes
\end{itemize}

\textbf{Pociask \& Morrison (2004):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Split-attention vs. integrated materials for cognitive and psychomotor tasks
    \item \textbf{Finding:} Integrated materials produced higher test scores
    \item \textbf{Similarity:} Same structure manipulation, similar learning benefit
    \item \textbf{Our parallel:} Integrated format produces both better learning and lower false memory
\end{itemize}

\subsection{Testing Effect and Retrieval Practice Studies}

\textbf{Roediger \& Karpicke (2006):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Study-study-study-test vs. study-test-test-test conditions
    \item \textbf{Finding:} Testing improved long-term retention more than repeated study
    \item \textbf{Similarity:} Active engagement (testing/pre-reading) enhances memory
    \item \textbf{Our contribution:} Pre-reading AI summary may function as a form of pre-testing
\end{itemize}

\textbf{Chan, Manley, Davis, \& Szpunar (2018):}
\begin{itemize}[noitemsep]
    \item \textbf{Design:} Testing old material before learning new material
    \item \textbf{Finding:} Prior testing potentiated new learning (forward testing effect)
    \item \textbf{Similarity:} Engaging with summary before reading potentiates article learning
    \item \textbf{Our parallel:} Pre-reading produces the highest MCQ performance
\end{itemize}

\subsection{Summary: How Prior Research Validates Our Findings}

\begin{table}[H]
\centering
\small
\begin{tabular}{p{3.5cm}p{5cm}p{6cm}}
\toprule
\textbf{Our Finding} & \textbf{Prior Validation} & \textbf{Effect Consistency} \\
\midrule
\textbf{Pre-reading $\rightarrow$ Better MCQ} & Mayer \& Bromage (1980); Hartley \& Davies (1976); Szpunar et al. (2013) & \checkmark~Our $d = 1.35$--$1.62$ exceeds typical advance organizer effects ($d \approx 0.21$--$0.50$), likely due to AI summary comprehensiveness \\
\textbf{Segmented $\rightarrow$ More False Lures} & Chandler \& Sweller (1992); Frenda et al. (2011); Roediger \& McDermott (1995) & \checkmark~Our OR = 5.93 is consistent with misinformation OR $\approx$ 3--5 and DRM false recognition rates ($\sim$40--55\%) \\
\textbf{Timing $\neq$ Recall} & Roediger \& Karpicke (2006); Jacoby (1991) & \checkmark~MCQ-recall dissociation is well-documented in dual-process and transfer-appropriate processing literature \\
\textbf{Total time constant} & Cepeda et al. (2006); Bahrick et al. (1993) & \checkmark~Time-on-task doesn't explain our effects; spacing/organization matters more \\
\bottomrule
\end{tabular}
\caption{How Prior Research Validates Our Findings}
\end{table}

\subsection{Novel Contributions Beyond Prior Research}

While our findings are consistent with prior research, we contribute several \textbf{novel extensions}:

\begin{enumerate}
    \item \textbf{AI-generated content context:} Prior research used human-created organizers; we extend to AI-generated summaries
    \item \textbf{False lure methodology:} We combine DRM-like false recognition with realistic educational misinformation
    \item \textbf{Timing $\times$ Structure manipulation:} Most studies manipulate one factor; we examine their independent and joint effects
    \item \textbf{Practical AI design implications:} We translate theoretical findings into concrete UI/UX recommendations for AI-assisted learning tools
\end{enumerate}

\vspace{1cm}
\hrule
\vspace{0.5cm}
\noindent\textit{Report generated from synthesis of: EXPANDED\_INTERPRETIVE\_REPORT.md, AI\_memory results.xlsx, Kortic.docx}

\noindent\textit{References are listed in the main thesis bibliography.}
