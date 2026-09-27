# Confirmatory Belebele test: results

Pre-registered in [PREREG.md](../../PREREG.md). 573 held-out parallel questions per language; paired bootstrap over question numbers, 10,000 resamples (seed 20260926), one index matrix shared by both languages, all quants and both models.

## Primary test: Yoruba minus English skill kept at Q3_K_M

Decision rule: supported for a model if its Holm-adjusted one-sided p (across the 2 models) is < 0.05.

| model | skill kept, English | skill kept, Yoruba | gap | 95% CI | one-sided p | Holm p | hypothesis |
|---|---|---|---|---|---|---|---|
| gemma4-e4b | 86% (82 to 90) | 62% (39 to 89) | -24.2 pts | -47.4 to +2.9 | 0.0374 | 0.0374 | **supported** |
| qwen3.5-4b | 98% (95 to 101) | 61% (42 to 81) | -37.0 pts | -56.3 to -17.3 | 0.0005 | 0.0010 | **supported** |

## Secondary (exploratory): the same gap at Q4_K_M

No decision rule and no multiplicity correction; for description only.

| model | skill kept, English | skill kept, Yoruba | gap | 95% CI | one-sided p |
|---|---|---|---|---|---|
| gemma4-e4b | 98% (95 to 100) | 83% (65 to 101) | -14.9 pts | -32.5 to +3.5 | 0.0536 |
| qwen3.5-4b | 97% (94 to 99) | 87% (73 to 103) | -9.4 pts | -23.9 to +6.3 | 0.1184 |

![Gap with 95% CI](gap.png)

## Accuracy (bootstrap 95% CI, same resamples)

| model | lang | Q8_0 | Q4_K_M | Q3_K_M |
|---|---|---|---|---|
| gemma4-e4b | English | 91.6% (89.4–93.7) | 90.1% (87.6–92.3) | 82.4% (79.2–85.5) |
| gemma4-e4b | Yoruba | 40.1% (36.1–44.2) | 37.5% (33.7–41.4) | 34.4% (30.5–38.2) |
| qwen3.5-4b | English | 89.4% (86.7–91.8) | 87.3% (84.5–89.9) | 88.1% (85.3–90.8) |
| qwen3.5-4b | Yoruba | 42.9% (38.9–46.9) | 40.7% (36.6–44.7) | 36.0% (31.9–40.0) |

Resamples where skill kept was undefined (Q8_0 at or below chance): 0. They count against the hypothesis in the p-value and are left out of the intervals.
