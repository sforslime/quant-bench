# Squeezing local LLMs: what compression costs in English, Pidgin and Yoruba

*A one-day benchmark on a 24 GB Apple M4 MacBook.*

## The question

Running an AI model on your own laptop means **quantizing** it: storing each of
its billions of weights in fewer bits (8, 6, 4, 3, even 2 instead of 16). The
file shrinks and replies get faster, but the model gets somewhat worse.

Most quantization benchmarks only measure English. This one asks:

1. **How much quality, speed and memory changes at each compression level on a normal Mac?**
2. **Does compression hurt Yoruba and Nigerian Pidgin more than English?**

## TL;DR

- **Q4_K_M is the sweet spot for English and Pidgin.** Compared with Q8_0, it
  generates **45–56% faster**, its file is **34–40% smaller**, and it uses
  **31–34% less GPU memory**. Neither model showed a significant quality loss on
  any English or Pidgin task at Q4_K_M (not even before correcting for multiple
  tests).
- **Yoruba tends to break first, but the evidence is moderate, not conclusive.**
  - At Q3_K_M, English keeps 88–102% of its above-chance reading skill, while
    Yoruba keeps 39–62%.
  - The paired Yoruba-minus-English gap at Q3_K_M excludes zero for both
    models: Gemma −48 points (95% CI −86 to −1), Qwen −40 (−70 to −8).
  - However, that comparison was chosen after seeing the data. No single Yoruba
    drop above Q2_K survives correction for the 40 tests run.
  - Gemma's Yoruba trends down at Q4 (41.5% → 37.0%), but not significantly.
  - Settling this needs a larger test (see [Next steps](#next-steps)).
- **The gap before compression is far bigger than anything compression does.**
  Both models score **~92% in English and ~43% in Yoruba** on the same
  questions (chance is 25%). Some of that gap may come from the setup, since the
  instructions are always in English (see [Limitations](#limitations)).
- **Yoruba pays a "token tax".** The same Belebele passages cost **2.35×
  (Gemma) and 2.57× (Qwen) as many tokens** in Yoruba as in English, even
  though the Yoruba text is 4% *shorter* in characters. Yoruba is slower to
  process and fills the context window faster.
- **Don't go below Q4 on a Mac.** Q3_K_M is no faster than Q4_K_M (on Gemma it
  is 15% slower), and it loses quality. Q2_K collapses: the models mostly repeat
  one answer letter.

## Results

### Reading comprehension: English vs. Yoruba

![Share of skill above chance kept at each quant, with 95% CIs](results/skill_kept.png)

**Skill kept** = (accuracy − 25% chance) ÷ (Q8_0 accuracy − 25%). Raw accuracy
understates Yoruba's loss, because Yoruba starts close to chance. Going from
41.5% to 31.5% removes more than half of what the model actually knows.

**Error bars** come from a paired bootstrap. The 200 question IDs are resampled
2,000 times, and each resample uses the same questions for the quant and for
Q8_0. Yoruba's intervals are wide because it starts less than 20 points above
chance (16.5 for Gemma, 19.5 for Qwen), so a few questions swing the ratio a
lot. Values below 0 mean worse than random guessing, i.e. collapse. They are
plotted in the shaded area, not clipped.

| Skill kept (95% CI) | Gemma, English | Gemma, Yoruba | Qwen, English | Qwen, Yoruba |
|---|---|---|---|---|
| Q6_K | 100% (98–102) | 88% (67–109) | 101% (100–102) | 100% (83–121) |
| Q4_K_M | 98% (94–101) | 73% (41–104) | 98% (93–102) | 95% (71–125) |
| Q3_K_M | 88% (81–94) | 39% (0–86) | 102% (96–107) | 62% (31–95) |
| Q2_K | −7% (−15–1) | −21% (−65–15) | 41% (30–50) | 15% (−17–50) |

**Yoruba minus English skill kept.** This is the direct test of "does Yoruba
lose more?". Each resample of question numbers is shared by both languages
(Belebele's questions are parallel translations). Negative means Yoruba lost
more.

| Gap (95% CI) | Q6_K | Q4_K_M | Q3_K_M | Q2_K |
|---|---|---|---|---|
| Gemma 4 E4B | −12 (−34 to +9) | −25 (−57 to +6) | **−48 (−86 to −1)** | −14 (−57 to +24) |
| Qwen 3.5 4B | −1 (−17 to +20) | −3 (−28 to +27) | **−40 (−70 to −8)** | −25 (−58 to +10) |

These intervals are uncorrected, and this analysis was added after seeing the
results. The consistent direction in both models is suggestive, but it is not
confirmation.

![Belebele accuracy by quant and language](results/belebele_by_language.png)

| Accuracy | Gemma 4 E4B, English | Gemma 4 E4B, Yoruba | Qwen 3.5 4B, English | Qwen 3.5 4B, Yoruba |
|---|---|---|---|---|
| Q8_0 | 93.5% | 41.5% | 91.5% | 44.5% |
| Q6_K | 93.5 | 39.5 | 92.0 | 44.5 |
| Q4_K_M | 92.0 | 37.0 | 90.0 | 43.5 |
| Q3_K_M | **85.0** ▼ | 31.5 ▽ | 92.5 | 37.0 ▽ |
| Q2_K | 20.0 ▼ | 21.5 ▼ | 52.0 ▼ | 28.0 ▼ |

Each quant is compared with the same model's Q8_0 on the same 200 questions
(exact McNemar test):
- **▼** = significant after Holm correction across all 40 paired tests
  (2 models × 4 quants × 5 task-language sets).
- **▽** = p < 0.05 before correction only.

At Q2_K, below-chance scores reflect the model repeating one letter (Gemma
answers "A" 77% of the time), not comprehension.

**Sanity check.** Neither model's publisher reports Belebele:
- The [Gemma 4 technical report](https://arxiv.org/abs/2607.02770) doesn't include it.
- The [Qwen 3.5 4B model card](https://huggingface.co/Qwen/Qwen3.5-4B) lists
  other multilingual benchmarks (MMMLU, MMLU-ProX, INCLUDE, …).

So there is no published number to match exactly. As a plausibility check, the
[Belebele paper](https://arxiv.org/abs/2308.16884) (appendix tables) reports:

| Model | Setup | English | Yoruba |
|---|---|---|---|
| GPT-3.5-turbo | zero-shot | 87.7% | 29.1% |
| Llama 2 70B | five-shot | 90.9% | 28.3% |

Our Q8_0 scores (English 91.5–93.5%, Yoruba 41.5–44.5%) are consistent with
newer small models slightly exceeding those 2023 results. The setups differ
(prompt format, shots, answer extraction), so this is not a like-for-like
comparison.

### Sentiment: English, Pidgin, Yoruba

![Sentiment accuracy by quant and language](results/sentiment_by_language.png)

This is the noisier task: tweets with crowd labels, and chance is 33%. The
evidence is mixed, and **none of the drops above Q2_K survive Holm
correction**:

- **Qwen:** Yoruba is the only language that trends down before Q2. It loses
  6.5 points at Q4 (p = 0.04, Holm 1.0) and 12.5 at Q3 (p = 0.007, Holm 0.20).
  English and Pidgin are flat.
- **Gemma:** Yoruba sentiment does *not* degrade; it scores slightly higher at
  Q4 and Q3, within noise. Pidgin drops 8.5 points at Q3 (p = 0.02, Holm 0.60).

### Speed and memory

![Generation and prompt speed by quant](results/speed.png)

| | Q8_0 | Q6_K | **Q4_K_M** | Q3_K_M | Q2_K |
|---|---|---|---|---|---|
| **Gemma 4 E4B**: generation, tok/s | 19.7 | 23.3 | **28.6** | 24.4 | 26.0 |
| File size, GB | 8.0 | 6.2 | **5.3** | 4.9 | 4.4 |
| GPU memory, GB (at 16k context) | 8.3 | 6.5 | **5.7** | 5.2 | 4.8 |
| **Qwen 3.5 4B**: generation, tok/s | 17.8 | 22.3 | **27.8** | 26.8 | 32.0 |
| File size, GB | 4.6 | 3.6 | **2.8** | 2.3 | 2.0 |
| GPU memory, GB (at 16k context) | 5.0 | 4.0 | **3.3** | 2.9 | 2.5 |

*File size* is the GGUF on disk. *GPU memory* is llama.cpp's own accounting of
weights + KV cache + compute scratch on the GPU, with a 16,384-token context
(4 slots × 4,096).

- **Generation** (writing the reply) is limited by how fast weights stream from
  memory, so smaller files are faster. The exception is Q3_K_M, likely because
  its 3-bit packing costs more compute to unpack than it saves in bandwidth.
- **Prompt reading** is compute-bound and stays at ~300–370 tok/s at every
  level. Compression doesn't make long prompts faster.
- With 4,096 tokens already in context, generation is only 0–8% slower.
- **Gemma E4B barely shrinks below Q4.** Its large per-layer embedding tables
  sit on the CPU and don't compress much. The Q2_K file is still 4.4 GB, versus
  5.3 GB for Q4_K_M.

![Quality vs file size](results/quality_vs_size.png)

### Token tax

Measured with each model's own tokenizer on the **182 unique parallel Belebele
passages** in the eval set. Passages only, special tokens excluded
([`scripts/token_tax.py`](scripts/token_tax.py)).

| | English passage | Yoruba passage | Yoruba ÷ English | Full prompt, Yoruba ÷ English |
|---|---|---|---|---|
| Gemma 4 E4B | 97.4 tokens | 229.4 tokens | **2.35×** | 1.88× |
| Qwen 3.5 4B | 98.7 tokens | 253.9 tokens | **2.57×** | 2.02× |

The Yoruba passages average 456 characters versus 477 for English, so the tax
comes from tokenization, not from longer text. The likely cause, not measured
here, is that tone-marked characters (ẹ, ọ, ṣ, à, é, …) are rare in the
tokenizers' training data and split into several tokens each. The "full prompt" column includes the
shared English instructions and chat template, which dilutes the ratio. The
sentiment sets are different tweets in each language, not translations, so
they can't be compared this way.

### Recommendation for the Telegram bot

- **English/Pidgin chat:** Qwen 3.5 4B **Q4_K_M**. It is a 2.8 GB file, uses
  3.3 GB of GPU memory at 16k context, and replies at ~28 tok/s, with no
  measurable loss vs. Q8_0. Gemma E4B Q4_K_M is equally fast and about as
  accurate, but its file is 5.3 GB and it needs 5.7 GB of GPU memory (1.7× Qwen).
- **If Yoruba matters:** Qwen 3.5 4B **Q6_K**. It is a 3.6 GB file, uses 4.0 GB
  of GPU memory, and replies at ~22 tok/s, with no measurable loss. Better still,
  don't rely on a 4B model for written Yoruba at all: ~44% on 4-choice questions
  is not usable.

Full tables are in [`results/summary.md`](results/summary.md). They include
accuracy CIs, paired tests with raw and Holm p-values, skill-kept CIs,
macro-F1, token counts, memory breakdown, and speed at both context depths.

## Setup

| | |
|---|---|
| Machine | Apple M4 (10-core), 24 GB unified memory, macOS 27.0 |
| Runtime | llama.cpp build 7fe450e19 (Metal), via `llama-server` and `llama-bench` |
| Models | Gemma 4 E4B-it, Qwen 3.5 4B (both ~4B-class, instruction-tuned) |
| Quant levels | Q8_0 (reference), Q6_K, Q4_K_M, Q3_K_M, Q2_K |

**The reference is Q8_0, not full precision (BF16).** Q8_0 is near-lossless in
practice, but not identical. "Skill kept" and "change vs. Q8_0" are relative to
Q8_0, so they slightly *understate* the total loss from full precision.

**How the quantized files were made.**
- Q8_0 GGUFs were downloaded from bartowski's Hugging Face repos, and their
  SHA-256 checksums were verified against the published values.
- The lower levels were made locally from Q8_0 with `llama-quantize`, using
  plain K-quants (no importance matrix).
- This gives one recipe for both models, and matches how the default Ollama
  library files are made.
- Importance-matrix quants would likely score a little higher at Q3/Q2.

### Tasks (200 items each, same items for every config)

| Task | Languages | Source |
|---|---|---|
| Reading comprehension, 4-choice | English, Yoruba (the *same* questions translated) | Belebele (`facebook/belebele`) |
| Sentiment (positive/negative/neutral), class-balanced | English, Nigerian Pidgin, Yoruba | TweetEval (`cardiffnlp/tweet_eval`); AfriSenti (`masakhane/afrisenti`) |

- **Prompts:** instructions are always in English; only the passage or post
  changes language.
- **Decoding:** temperature 0. Output is grammar-constrained to a valid label,
  so scores measure knowledge, not formatting. Qwen's thinking mode is off.
- **Accuracy CIs:** 95% bootstrap over items. With 200 items, a single
  accuracy is uncertain by roughly ±4–7 points (±4 near 90%, ±7 near 50%).
- **Why McNemar:** each item is either right or wrong under both quants, so the
  test compares only the items where they disagree. It is paired, and much
  more sensitive than comparing two separate accuracies.
- **Multiple comparisons:** Holm step-down correction across all 40
  quant-vs-Q8_0 tests. Both raw and adjusted p-values are in `results/summary.md`.

### Speed
`llama-bench`, 5 repetitions:
- prompt processing of 512 tokens (pp512)
- generation of 128 tokens (tg128)

Both were measured at empty context and with 4,096 tokens already in context,
with no other heavy processes running.

## Data and reproducibility

- **Eval set:** built by `scripts/build_evals.py` with seed `42` from pinned
  dataset versions (Hugging Face commit SHAs in the script). SHA-256 of
  `data/evals.jsonl`:
  `3594026aa65ecfc5ebd980ae275019e898cc4dd59005d40c7c63fcd0d76a4786`.
  Rebuilding reproduces this hash exactly.
- **Per-item results are committed:**
  - `results/quality/<model>__<quant>.jsonl` has one line per question: item
    ID, gold label, prediction, correct or not, prompt tokens and latency.
  - `<model>__<quant>.meta.json` holds that config's memory and timing.
  - `results/speed.jsonl` holds the raw llama-bench numbers.
  - `results/token_tax.json` holds the tokenizer counts.
- **Re-running the analysis needs no models:** `python scripts/report.py`
  regenerates every table and chart from the committed files.

### Reproduce from scratch

```sh
brew install llama.cpp
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
sh scripts/download.sh          # Q8_0 files + checksum check
sh scripts/run_all.sh           # evals, quantize, quality, speed, token tax, report
```

| Script | Does |
|---|---|
| `scripts/build_evals.py` | builds the fixed 1,000-item eval set in `data/evals.jsonl` |
| `scripts/quantize.py` | Q8_0 → Q6_K / Q4_K_M / Q3_K_M / Q2_K |
| `scripts/bench_quality.py` | runs every item through every config, records GPU memory |
| `scripts/bench_speed.py` | llama-bench sweep |
| `scripts/token_tax.py` | English vs. Yoruba token counts on the parallel passages |
| `scripts/report.py` | tables (`results/summary.md`) and charts (`results/*.png`) |

## Limitations

- **English-only instructions.** The instructions are in English, so the Yoruba
  tasks are partly cross-lingual. Some of the English–Yoruba gap may come from
  the setup rather than from Yoruba reading ability.
- **Sample size.** 200 items per task-language set. Only the Q2_K collapses and
  Gemma's Q3_K_M English drop survive Holm correction. The Yoruba-vs-English
  gap analysis was added after seeing the data, and is uncorrected.
- **Reference.** Q8_0 is the reference, not BF16 (see Setup).
- **Model coverage.** Two models, both ~4B. Bigger models may degrade differently.
- **Sentiment labels.** AfriSenti labels come from tweets and are noisy. Treat
  the sentiment accuracies as relative (quant vs. quant), not absolute.
- **Answer balance.** Belebele's correct answers are not perfectly balanced
  across A–D in this sample (C is most common, at 31%).
- **Parallel slots.** The quality runs used 4 parallel server slots. This
  barely affects results at temperature 0, but is not bit-for-bit identical to
  single-request runs.
- **Memory measurement.** Memory is llama.cpp's own GPU accounting. macOS
  process RSS was also recorded, but it is unreliable for Metal and
  memory-mapped models (it *rose* as files shrank), so it isn't reported.
- **Speed.** Speed comes from a single machine and a single llama.cpp build.
  Q3_K being slower than Q4_K reflects this build's Metal kernels, and may change.

## Next steps

- Re-run Belebele on **all 900 questions** at Q8_0, Q4_K_M and Q3_K_M. That is
  4.5× the data, enough to confirm or reject the Yoruba-vs-English gap with a
  pre-registered test.
- Add a **Yoruba-instructions** variant to separate reading ability from the
  cross-lingual setup.
- Compare against **importance-matrix quants** and a **BF16** reference.

## License

The code is MIT-licensed (see [LICENSE](LICENSE)). The datasets keep their own
licenses, per their Hugging Face cards:
- Belebele: CC BY-SA 4.0
- AfriSenti (`masakhane/afrisenti`): CC BY-NC-SA 2.0
- TweetEval: listed as "unknown"

This repo does not redistribute dataset text. The result files contain only
item IDs, gold labels and model predictions.

## References

- Bandarkar et al. (2023). *The Belebele Benchmark: a Parallel Reading
  Comprehension Dataset in 122 Language Variants.* [arXiv:2308.16884](https://arxiv.org/abs/2308.16884)
- Muhammad et al. (2023). *AfriSenti: A Twitter Sentiment Analysis Benchmark
  for African Languages.*
- Barbieri et al. (2020). *TweetEval: Unified Benchmark and Comparative
  Evaluation for Tweet Classification.*
