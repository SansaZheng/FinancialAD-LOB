# Stage011: fresh-date lifecycle and depth-resolved evaluation

Stage010 is retained as a diagnostic benchmark. Its audit found474 of2222
interventions with passive synthetic liquidity omitted inside the visible price
range, and46 with marketable synthetic orders. Those results cannot support a
realistic manipulation-detection claim. Its unstarted stock/combined batches
were cancelled; the running date/style diagnostic was preserved.

Stage011 uses untouched2017-01-16/17/18 WSE partitions for five stocks. The source
license, full-day acquisition and independent replay checks are unchanged.
Active inserted quantities are merged by absolute price with each observed
base book, retained until their explicit withdrawal, and projected to the best
five prices. An absent base price can therefore still carry synthetic liquidity.
If an active insertion becomes marketable, the entire intervention is censored
for either class; no fill or instant cancellation is invented. This is a
conditional passive-book overlay, **not** a matching engine or an endogenous
market simulation. Background trades do not react to inserted liquidity.

Positive policies are coordinated burst or wave withdrawal; benign controls
have matched volume distributions, burst per-order lifetime marginals, or wave
lifetime multisets. Coordination dependence is the intended distinction.
Random benign policies can coincide with a positive observable pattern; such
collisions are retained and counted. No label is a finding of real trader intent.
Both intervention classes finish before the window endpoint, removing the old
persistent-volume shortcut. Interventions remain in event time, not the target
paper's millisecond clock. Full source days are archived, but evaluation windows
are25 contiguous events with stride64.

The method now retains additions/removals and coverage masks for every side and
level. A price absent from a snapshot means known zero only if it lies inside
that snapshot's observed price range; otherwise its flow is unknown. The rank
ablation has exactly the same masks and substitutes same-rank volumes. The
stronger L1-flow cascade receives the same observed information at the best
level only, challenging whether gains require multilevel dynamics.

All11 methods receive the same source partitions. Supervised methods share the
same generated training labels; one-class detectors fit designated normal
training examples only. Hyperparameter selection uses six validation trials.
Five seeds, ten epochs per trained neural stage, and date/stock/combined/style
splits remain fixed. Constant features are identified from training only and
removed before choosing a nominal200k-parameter fusion width. Actual parameter
counts, masks, checkpoints, selections, predictions and hashes are saved.

See `configs/011-preregistered.json`. The raw Transformer architecture remains
the compact JFDS adaptation described in `010-reproduction-fidelity.md`; original
LOBSTER2015 labels/code and eight execution/cancellation manual channels remain
unavailable. Thus comparison with the source paper's0.675 is still invalid.
No method hyperparameters will be changed based on fresh-date test results.

中文结论：新版修复了已发现的可见挂单截断，采用更匹配的对照和逐档信息，并在新日期上评测；它仍是明确受限的半合成风险模式任务，不能替代真实意图标签或原论文同数据复现。
