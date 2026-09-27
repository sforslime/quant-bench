"""Token tax: how many tokens the same Belebele passage costs in English vs. Yoruba,
using each model's own tokenizer (via llama-server's /tokenize on the Q8_0 file;
the tokenizer is identical across quants).

Only Belebele is used: its English and Yoruba passages are translations of each
other, so the comparison is like-for-like. (The sentiment sets are different
tweets per language, so they can't be compared this way.)

The pilot set (default) paired the languages by row number, which Belebele does
not support: its English and Yoruba files are in different orders, so most
pilot "pairs" are different passages. --confirm uses data/confirm.jsonl, paired
by its "pair" field (the dataset's own question key), and is the correct
comparison.

Writes results/token_tax.json (pilot) or results/confirm/token_tax.json (--confirm).
Usage: python scripts/token_tax.py [--confirm]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from bench_quality import URL, start_server
from config import DATA_DIR, MODELS, REFERENCE_QUANT, RESULTS_DIR, gguf_path


def passage(prompt):
    return prompt.split("Passage:\n", 1)[1].split("\n\nQuestion: ", 1)[0]


ap = argparse.ArgumentParser()
ap.add_argument("--confirm", action="store_true", help="use the correctly paired confirmatory set")
args = ap.parse_args()
out_dir = RESULTS_DIR / "confirm" if args.confirm else RESULTS_DIR

items = [json.loads(line) for line in (DATA_DIR / ("confirm.jsonl" if args.confirm else "evals.jsonl")).open()]
key = (lambda it: str(it["pair"])) if args.confirm else (lambda it: it["id"].rsplit("-", 1)[1])
by_lang = {lang: {key(it): passage(it["prompt"]) for it in items
                  if it["task"] == "belebele" and it["lang"] == lang} for lang in ("eng", "yor")}
# Several questions can share a passage; count each parallel passage pair once.
pairs = {by_lang["eng"][i]: by_lang["yor"][i] for i in sorted(by_lang["eng"], key=int)}
if args.confirm:
    # Correct pairing: each English passage has exactly one Yoruba translation.
    assert len(pairs) == len(set(pairs.values()))

out = {}
for model in MODELS:
    proc = start_server(gguf_path(model, REFERENCE_QUANT), out_dir / f"token_tax.{model}.server.log")
    try:
        def count(text):
            r = requests.post(f"{URL}/tokenize", json={"content": text, "add_special": False}, timeout=60)
            r.raise_for_status()
            return len(r.json()["tokens"])

        eng = [count(e) for e in pairs]
        yor = [count(y) for y in pairs.values()]
    finally:
        proc.terminate()
        proc.wait()
    out[model] = {
        "n_passages": len(pairs),
        "eng_tokens_mean": sum(eng) / len(eng),
        "yor_tokens_mean": sum(yor) / len(yor),
        "ratio_of_totals": sum(yor) / sum(eng),
        "eng_chars_mean": sum(map(len, pairs)) / len(pairs),
        "yor_chars_mean": sum(map(len, pairs.values())) / len(pairs),
    }
    print(model, out[model], flush=True)

(out_dir / "token_tax.json").write_text(json.dumps(out, indent=2))
