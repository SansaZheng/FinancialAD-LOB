# Observation-aware sequence comparisons

The implemented improvement addresses a representation error: an absent event
feed must not be encoded as measured zero. This is a correctness improvement,
not established methodological novelty or an AP gain.

## Implemented changes

The ten-channel encoder adds `cancel_observed` and `execute_observed` to the
original eight channels. Complete interval coverage must be declared explicitly;
an empty message list defaults to unknown. WSE deletion messages are not treated
as verified cancellations. Both adjacent book endpoints must be noncrossed.

All three new sequence controls share a gate that discards filled values in
unavailable event channels and price changes at censored levels. Training-only
normalization excludes missing values from moments, preserves binary masks and
gates again afterwards. This prevents standardized imputations from becoming
apparently observed flow.

| Supervised adapter | Width | Parameters |
|---|---:|---:|
| Shared level attention + causal TCN candidate | 55 | 31,187 |
| Rank-flattened causal TCN | 54 | 31,915 |
| Rank-flattened causal Transformer | 40 | 30,561 |

Widths maximize capacity within the same 32,000-parameter ceiling, using only
architecture counts. Maximum difference is about 4.2% of the largest model.
This does not equalize FLOPs or wall time. The Transformer uses triangular causal
attention, sinusoidal positions and independently initialized layers, consistent
with the [PyTorch 2.8 API](https://docs.pytorch.org/docs/2.8/generated/torch.nn.TransformerEncoder.html).
The legacy `LiquidityDynamics` core retains its eight-channel default; the new
wrapper explicitly requests ten channels and applies observation gates.

## Fair-training contract

`lobbench.sequence_run` shares input sequences, labeled IDs, batch-index schedules,
six fixed validation trials, optimizer-step budgets and normalization fit IDs.
Trials are three learning rates times two weight decays. There is no early
stopping. Selection uses validation AP; thresholds use validation negatives;
test inference follows selection. It saves source/split/label/batch hashes,
normalizer, predictions, checkpoint, versions and actual parameter counts.

Non-engineering training requires CQ. Locally, engineering opt-in permits at
most 20 steps per trial and 10 MiB input. CPU execution is qualified; the CUDA
option exists but is not yet GPU-qualified. Only trusted state dictionaries
should be loaded, with `weights_only=True`.

After legal labels and session checks, use the same configuration for
`liquidity`, `tcn` and `transformer`:

```bash
python -m lobbench.sequence_run --input /data/PROJECT/windows.jsonl \
  --manifest /data/PROJECT/windows.manifest.json --split configs/split.json \
  --method liquidity --steps 1000 --batch-size 32 --parameter-budget 32000 \
  --positive-budget 32 --negative-budget 256 --seed 0 --device cpu \
  --commit FULL_PUSHED_SHA --output "$CQ_OUTPUT_DIR"
```

These labeled input paths are examples, not acquired data.

## Actual evidence

The WSE-prefix audit processed **152 valid adjacent pairs / 1,520 level tokens**
across two stocks and three dates. **3,040 event-channel values are unknown**, not
verified zeros. Translation and consistent currency-unit rescaling preserve
features to numerical precision (maximum absolute difference below 1e-10).
The diagnostic declares a 1 PLN distance unit, not an unverified exchange tick.
Retained prefixes still include retransmission/preopen states.

31 CPU engineering tests pass locally, including causal checks for all three
models, missing-fill invariance, normalization masks, actual optimizer steps and
shared label/split/batch hashes. Small randomly generated training fixtures are
not financial experiments. See `results/wse-feature-audit-009/`,
`results/engineering/qualification-009-final/`, and
`results/engineering/sequence-architecture-009.json`.

The [source paper](https://arxiv.org/html/2508.17086v2) uses a cascaded
representation with supervised contrastive learning and downstream OC-SVM/IF.
Our generic Transformer is a matched-input control, not that complete pipeline.
Toy AP values cannot establish comparability with the reported 0.675.

## Next discriminating experiments

CQ environment and smoke jobs both completed successfully on canonical source
commit 7023f84a036c. A subsequent CQ acquisition job expanded real-prefix coverage
to five stocks: 61,440 messages, 480 snapshots, 387 valid adjacent feature pairs.
See `results/engineering/stage-009-summary.json`. Scientific training and original
paper reproduction remain pending; these jobs validate data and implementation.

The JFDS predecessor's original model/training source was recovered from its
[CC BY Zenodo release](https://zenodo.org/records/11048480) without downloading
the full archive. `vendor/jfds_reference/PROVENANCE.md` records exact boundaries.
Only static inspection has run; CPU-incompatible unconditional CUDA calls exist
in its training paths and need a documented adapter before integration.

1. Compare raw snapshots, price-aligned changes and observation masks using
   identical frozen windows. Restore rank-wise deltas as an alignment ablation.
2. Add interval duration and order-lifetime dynamics after attribution and
   session filtering are validated. Event-count windows span unequal clock time;
   the current representation does not resolve that issue.
3. Evaluate future dates, five held-out-stock folds and held-out manipulation
   generators. Report paired stock-day uncertainty, including failed settings.
4. Implement the original cascade/contrastive and normal-training OC-SVM/IF
   regimes with separately declared supervision. WSE prefixes are unlabeled;
   they cannot simply be declared clean normal training examples.

中文结论：缺失信息处理和公平神经对照已实现并通过工程检查；真实特征语义更可靠，但操纵检测性能增益仍待正式实验。
