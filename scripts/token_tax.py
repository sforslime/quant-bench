"""Token tax: how many tokens the same Belebele passage costs in English vs. Yoruba,
using each model's own tokenizer (via llama-server's /tokenize on the Q8_0 file;
the tokenizer is identical across quants).

Only Belebele is used: its English and Yoruba passages are translations of each
other, so the comparison is like-for-like. (The sentiment sets are different
tweets per language, so they can't be compared this way.)

Writes results/token_tax.json. Usage: python scripts/token_tax.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from bench_quality import URL, start_server
from config import DATA_DIR, MODELS, REFERENCE_QUANT, RESULTS_DIR, gguf_path


def passage(prompt):
    return prompt.split("Passage:\n", 1)[1].split("\n\nQuestion: ", 1)[0]


items = [json.loads(line) for line in (DATA_DIR / "evals.jsonl").open()]
by_lang = {lang: {it["id"].rsplit("-", 1)[1]: passage(it["prompt"]) for it in items
                  if it["task"] == "belebele" and it["lang"] == lang} for lang in ("eng", "yor")}
# Several questions can share a passage; count each parallel passage pair once.
pairs = {by_lang["eng"][i]: by_lang["yor"][i] for i in sorted(by_lang["eng"], key=int)}

out = {}
for model in MODELS:
    proc = start_server(gguf_path(model, REFERENCE_QUANT), RESULTS_DIR / f"token_tax.{model}.server.log")
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

(RESULTS_DIR / "token_tax.json").write_text(json.dumps(out, indent=2))
