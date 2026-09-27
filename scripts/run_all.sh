#!/bin/sh
# Full pipeline. Quality runs start as soon as each model's Q8_0 lands;
# the speed sweep runs last, when nothing else is using the machine.
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python

wait_for() { while [ ! -f "models/$1" ]; do sleep 30; done; }

[ -f data/evals.jsonl ] || $PY scripts/build_evals.py

wait_for Qwen_Qwen3.5-4B-Q8_0.gguf
$PY scripts/quantize.py
$PY scripts/bench_quality.py --only qwen3.5-4b

wait_for google_gemma-4-E4B-it-Q8_0.gguf
$PY scripts/quantize.py
$PY scripts/bench_quality.py --only gemma4-e4b

$PY scripts/bench_speed.py
$PY scripts/token_tax.py  # pilot count (superseded; not correctly paired)
$PY scripts/report.py

# Confirmatory test (PREREG.md): held-out set, run, pre-registered analysis, corrected token tax
$PY scripts/build_confirm.py
$PY scripts/bench_confirm.py
$PY scripts/confirm_report.py
$PY scripts/token_tax.py --confirm  # after bench_confirm.py: reads its prompt-token counts
echo "PIPELINE COMPLETE"
