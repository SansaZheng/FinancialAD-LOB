# Candidate: price-aligned liquidity dynamics

Status: implemented prototype and falsifiable hypothesis; **novelty unverified**.

Adjacent LOB ranks are not stable objects: when quotes move, level 2 can become
level 1. Direct rank-wise differences can mistake migration for new liquidity
or cancellation. `lobbench.liquidity` aligns adjacent snapshots by actual price,
marks prices not visible in both snapshots as censored, and incorporates
cancel/execution messages only from the interval already observed.

Tokens encode side, distance to midprice in ticks, log volume, aligned additions/
removals, cancellation and execution volume, and an observation mask. A shared
token MLP and attention pooling integrate price levels; causal dilated temporal
convolutions model buildup and disappearance. This is not a trader-identity
model and cannot establish intent from anonymous snapshots.

`lobbench.models.LiquidityDynamics` emits timestamp-level logits.
`paired_loss` combines supervised BCE and prediction consistency. Only valid
label-preserving augmentations may enter that loss. Arbitrarily altering the
execution/cancellation outcome is **not** label-preserving. The augmentation
generator is pending. A matched-budget supervised neural runner is implemented
in `lobbench.sequence_run`; paired loss stays inactive until an augmentation is
validated. See `improvement-009.md` for the observation-aware wrapper and controls.

Planned ablations:

| Comparison | Question |
|---|---|
| Same-input TCN / Transformer | Are gains more than event channels? |
| Rank-aligned vs price-aligned | Does quote migration confound detection? |
| With/without execution vs cancel distinction | Is lifecycle information useful? |
| With/without consistency loss | Does valid augmentation improve domain shift? |
| Parameter-matched snapshot model | Is model capacity the explanation? |
| Shared vs stock-specific encoding | Does the representation transfer? |

Primary antecedents include Fabre & Challet's distance-aware order-flow modeling
([2025](https://arxiv.org/abs/2504.15908)) and the TCN-based weak-label framework
of Kularatnam & Stathaki ([2024](https://arxiv.org/abs/2403.13429)). A new encoder
assembled from known parts is not, by itself, evidence of a CCF A contribution.

中文结论：候选方法针对档位移动造成的伪变化，但创新性和性能增益尚待相同输入、相同标签预算下的严格对照验证。
