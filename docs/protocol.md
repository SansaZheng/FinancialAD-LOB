# Preregistered evaluation contract — version 1

Status: implementation and engineering qualification, **not benchmark results**.
Quality target: CCF A; no venue selected and no acceptance/novelty guarantee.

## Scientific question

Does price-aligned liquidity lifecycle information improve discrimination of
multilevel manipulation-like episodes under domain shift, beyond the benefits of
extra labels, extra features, extra parameters, or the injection recipe itself?

The starting paper is [Lin & Yang, arXiv:2508.17086](https://arxiv.org/abs/2508.17086).
Its reported 0.675 is a literature value, not our baseline. Reproducing it requires
the original data, injection implementation, split and metric definition.

## Data and evidence levels

1. Engineering fixtures: generated arrays, no financial conclusions.
2. Semi-synthetic: real market backgrounds with injected and labeled episodes.
   Conclusions concern recovery of those generators, not detection of intent.
3. Real labeled: independently verified events with documented adjudication.
   Account/intent claims require the necessary order/trader evidence.

The first two cannot be relabeled as the third. FI-2010 price-direction labels
are not manipulation labels. A different intraday interval is not another date.
A single stock on many dates is not cross-stock evaluation.

Target: at least five stocks and twenty dates, multiple liquidity regimes; this
is an acquisition target, not an assertion that data exist locally. Ten datasets
and ten comparable baselines (including two relevant 2026 works) remain planning
targets subject to availability and relevance. Do not multiply identical data
by split/seed and call them independent datasets.

## Frozen protocols

* Cross-date: earlier complete sessions train, subsequent sessions validate, later
  sessions test. No randomly shuffled overlapping windows.
* Cross-stock: disjoint training, validation and test stocks, with source/session
  metadata retained. Rotate held-out stocks using a declared outer fold table.
* Combined: training stocks on early dates train; same stocks on intermediate
  dates validate; held-out stocks on later dates test. Other data are unused.
* Generator shift: train on one or more generator families, validate on declared
  training-family parameters, test on held-out families and parameter ranges.
  Do not select methods on the held-out-family test scores.

All representations, normalization statistics and feature thresholds are fitted
on training data. Windows are constructed inside partitions, with purging and an
embargo at least as long as the longest feature lookback/event context when
within-session splits are used. Entire source episodes and matched hard-negative
counterparts stay in one partition. Audit event, source and sample identities.
Retain original timestamps; predictions are available at the window endpoint.

## Supervision and optimization fairness

Freeze seeds 0–4. A deterministic, saved subset of positive and negative training
window IDs is shared by every supervised model. Report unique labeled events as
well as labeled windows; overlapping windows do not count as independent labels.
Evaluate positive-label budgets such as 8, 32 and 128 only where feasible. The
validation label budget is shared, disclosed, and never silently increased.

Keep unsupervised clean-normal training as a separately labeled regime; it must
not be used to attribute gains solely to supervised architecture. Likewise,
representation pretraining is a separate factor with equal unlabeled data access.

The current tabular runner has six predeclared validation trials per method.
Equal trial count is not equal compute: record wall time and report compute as
a separate axis. Neural controls use equal step budgets, the same early-stopping
rules and an explicit parameter-matched comparison. Test data are scored once
after validation-only selection. Publish all trials and failures.

## Metrics and uncertainty

Primary: step average precision (AP), explicitly distinct from trapezoidal PR
AUC until the source paper's metric implementation is recovered. Report test
prevalence alongside every PR score. Secondary: event recall, precision and
recall at validation-calibrated FPR, per-stock/date metrics, worst-group AP,
event-level alarm rate and latency where onset/duration metadata exist.

Window FPR is not alarms/hour. For operational reporting, deduplicate nearby
alerts with a frozen cooldown and divide by the actual observed normal hours.
An event is hit only by an alarm emitted during its detectable interval; do not
backdate window predictions. Detection delay uses authoritative event onset.

Use five paired seeds and paired stock-date block bootstrap intervals (2,000
replicates), with sensitivity to date-only clustering for shared market shocks.
Do not claim statistical significance from a confidence interval that contains
zero. Predeclare the principal contrast to limit post-hoc method shopping.

## Decisive controls and falsification

Compare snapshot-only and event-informed models using identical input views.
Include size-matched genuine execution, genuine cancellation, quote migration,
large persistent liquidity, missing messages, volatility bursts and feed gaps.
An injection detector can otherwise learn volume or labeling artifacts.

The candidate is falsified if its gain disappears against the same-input TCN/
Transformer, fails unseen-generator tests, vanishes on equal-label controls, or
raises alarms on matched legitimate events. Such failures remain in the report.

中文结论：先固定数据隔离、标签预算和比较规则；所有指标必须带证据级别，不能把人工注入识别当成真实操纵识别。
