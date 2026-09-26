# Pre-registration: confirmatory Belebele test (Yoruba vs. English under compression)

*Written and committed on 2026-09-26, before any model was run on the confirmatory
items. Nothing below changes after this commit. Any deviation will be listed, with
reasons, in the "Confirmatory test" section of the README.*

## Background

The pilot ([README](README.md), 200 Belebele questions per language) suggested
that at Q3_K_M, Yoruba keeps a smaller share of its above-chance reading skill
than English does. Gap (Yoruba minus English skill kept): −48 points for Gemma 4
E4B and −40 for Qwen 3.5 4B. That comparison was chosen after seeing the data,
so it is a hypothesis, not a finding. This test checks it on questions the pilot
did not use.

## Data: the held-out set

- **Source:** `facebook/belebele`, configs `eng_Latn` and `yor_Latn`, at the same
  pinned revision as the pilot (`7899cdfa4e1e0d733fd77c848e2c273cb1d32be2`).
- **Items:** every question the pilot did not use, in either language.
  - **573 questions per language, 1,146 items in total.**
  - Built by [`scripts/build_confirm.py`](scripts/build_confirm.py) with the
    pilot's prompt function (`build_evals.belebele_item`).
  - Deterministic: no sampling.
- **File:** `data/confirm.jsonl`, SHA-256
  `9f58ea6abf742db28441ed7358a6b889b2fc671d0f871655c76e6099fc68f27b`.
  - The file is not committed, because it contains dataset text; the script
    rebuilds it byte for byte.
- **Pairing:** English and Yoruba items are paired by the dataset's own
  question key, (`link`, `question_number`).
  - This key matches 1:1 across the two languages, and the correct answer
    agrees for all 900 questions.
  - Each item keeps its language's row number in `id`, and gets a shared
    `pair` field (the English row number).

### Why 573 and not ~700

The plan assumed the two language files list the questions in the same row
order. They don't: rows 0–177 line up, but 722 of the 900 row numbers point to
different questions in English and Yoruba.

- **Effect on the pilot:** it paired languages by row number, so only 42 of its
  200 English/Yoruba "pairs" were actually the same question. The pilot touched
  327 distinct questions: 200 in each language, 73 of them shared.
- **What this test does:** it drops all 327, so no question from the pilot
  enters it in either language, and it pairs by the real question key.
- **Pilot results:** they are left unchanged. The per-language accuracies are
  unaffected. The pilot's "same questions" pairing (the gap intervals and the
  token-tax passage comparison) was mostly between different questions.

## Hypothesis

**H1:** At Q3_K_M, Yoruba keeps less of its above-chance Belebele skill than
English does, in the same model.

## Primary test (one per model: Gemma 4 E4B, Qwen 3.5 4B)

- **Skill kept:** for each language, skill_kept = (acc_Q3_K_M − 0.25) ÷
  (acc_Q8_0 − 0.25), where 0.25 is chance on 4-choice questions.
- **Gap:** skill_kept(yor) − skill_kept(eng). The point estimate uses all 573
  questions.
- **Paired bootstrap over questions:**
  - B = 10,000 resamples of the 573 `pair` numbers, with replacement, from
    `numpy.random.default_rng(20260926)`.
  - The one index matrix is used for both languages, both quants and both
    models.
  - Each resample recomputes both skill_kept values and their gap.
- **One-sided p-value for gap < 0:** p = (1 + #{resamples with gap ≥ 0 or
  undefined}) ÷ (B + 1).
  - A resample is *undefined* when its Q8_0 accuracy is at or below 0.25.
    Undefined resamples count against H1.
- **Multiplicity:** Holm adjustment across the two models' primary p-values.
- **Decision rule:** H1 is **supported** for a model if its Holm-adjusted p is
  < 0.05, and **not supported** otherwise.
  - The outcome is reported for each model, whichever way it goes.
  - "Not supported" means this test did not find the effect. It does not mean
    the effect was shown to be absent.
- **Also reported:** the gap's 95% percentile interval from the same resamples,
  and each language's skill kept with its interval.

## Secondary (exploratory)

- The same gap and one-sided p at Q4_K_M, labelled exploratory, with no
  decision rule and no multiplicity correction.
- Accuracies with bootstrap intervals, for description.
- Nothing else is analysed as a test.

The analysis is fixed in code: [`scripts/confirm_report.py`](scripts/confirm_report.py),
committed with this file and tested only on synthetic data.

## Fixed settings

Identical to the pilot. The run script imports the pilot's server launcher and
request function rather than copying them.

| Setting | Value |
|---|---|
| Prompt | the pilot's Belebele prompt; English instructions, passage/question/options in the item's language |
| Decoding | temperature 0, `max_tokens` 8, grammar `root ::= "A" \| "B" \| "C" \| "D"` |
| Thinking | off (`--reasoning-budget 0`, `enable_thinking: false`) |
| Server | `llama-server` llama.cpp build 7fe450e19 (Metal), `-ngl 99`, `--jinja` |
| Context and slots | 4 slots × 4,096 tokens (`-c 16384 -np 4`) |
| Warm-up | one request per config, discarded |
| Configs | Gemma 4 E4B and Qwen 3.5 4B × Q8_0, Q4_K_M, Q3_K_M × English and Yoruba |

The GGUFs are reused from the pilot, not re-quantized (SHA-256):

| File | SHA-256 |
|---|---|
| `google_gemma-4-E4B-it-Q8_0.gguf` | `6a6eba0d36a051b5d924211a889c1436717006e7c5d413830c47caa1d46cb598` |
| `google_gemma-4-E4B-it-Q4_K_M.gguf` | `20052ebf38e68e5f255b54fe61e9ff3288971754f425c2fdabcd8c3fc99da93e` |
| `google_gemma-4-E4B-it-Q3_K_M.gguf` | `d22d6977a58b3333b86aded357336ec68906e4897f504029a473346676ac70d3` |
| `Qwen_Qwen3.5-4B-Q8_0.gguf` | `5c74c0ede371924357dff0cb6ba145bd67208b9b2389ded681adfff3f7608db7` |
| `Qwen_Qwen3.5-4B-Q4_K_M.gguf` | `7bbe16b99cf67c36ac92a2216a387d56e1e4db76ec1bfc0db6f5726ee1b7ac6a` |
| `Qwen_Qwen3.5-4B-Q3_K_M.gguf` | `3030327841eded0a4f28c1e0911293fb76e04351d8b800811ac1537e9a8abc57` |

## Procedure

- **Before running:** Ollama and other heavy apps are quit.
- **The run:** [`scripts/bench_confirm.py`](scripts/bench_confirm.py) runs
  unattended and writes `results/confirm/<model>__<quant>.jsonl`, in the pilot's
  format plus `pair`.
  - It resumes at the item level after an interruption.
  - It never prints accuracies.
- **No peeking:** no accuracy, gap or test is computed until all six configs
  have finished every item. The analysis script refuses to run on incomplete
  data.
- **No exclusions:** every item counts. A failed request is retried, never
  dropped.

## Expected precision (estimated from the pilot)

[`scripts/prereg_power.py`](scripts/prereg_power.py) simulates 500 datasets of
573 questions per language, by resampling the pilot's items, and runs this test
on each (2,000 resamples per dataset).

| Model | Pilot gap | Pilot 95% CI width | Expected 95% CI width here | SD of the gap estimate | Power if the true gap equals the pilot's | Power at half the pilot gap |
|---|---|---|---|---|---|---|
| Gemma 4 E4B | −48 pts | 86 pts | **≈ 49 pts** | 12.0 pts | 0.93–0.96 | ≈ 0.52–0.64 |
| Qwen 3.5 4B | −40 pts | 63 pts | **≈ 36 pts** | 8.9 pts | 0.96–0.98 | ≈ 0.61–0.72 |

- **Reading the power columns:** each gives a range because the Holm threshold
  for a model is 0.025 or 0.05, depending on the other model's p.
- **Half the pilot gap:** computed from a normal approximation using the
  simulated SD.
- **Expect lower power than the first column suggests.** The pilot gaps were
  picked out *because* they looked large, so the true gaps are likely smaller.
  The half-gap column is the more realistic guide.
- **What the width means:** with an SD of 9–12 points, only gaps larger than
  roughly 20–25 points can be reliably told apart from zero. Small differences
  cannot be resolved.
