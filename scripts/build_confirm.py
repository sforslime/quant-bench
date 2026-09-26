"""Build the held-out confirmatory set in data/confirm.jsonl (see PREREG.md).

Every Belebele question not used by the pilot in either language, in eng_Latn and
yor_Latn, from the same pinned dataset revision and with the same prompt as
build_evals.py. Deterministic: no sampling, English row order.

The two languages' rows are NOT in the same order (only rows 0-177 line up), so a
question is identified by its (link, question_number) key, which matches 1:1
across languages. Each item keeps its own language's row number in "id" (as in
the pilot) and gets a shared "pair" (the English row number) for pairing.

Usage: python scripts/build_confirm.py
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_evals import belebele_item, load

from config import DATA_DIR

LANGS = ("eng_Latn", "yor_Latn")


def main():
    pilot = {json.loads(line)["id"] for line in (DATA_DIR / "evals.jsonl").open()}
    sets = {lang: load("facebook/belebele", lang)["test"] for lang in LANGS}
    n = len(sets[LANGS[0]])
    assert all(len(ds) == n for ds in sets.values())
    key = {lang: [(r["link"], r["question_number"]) for r in ds] for lang, ds in sets.items()}
    row_of = {lang: {k: i for i, k in enumerate(keys)} for lang, keys in key.items()}
    assert all(len(r) == n for r in row_of.values()) and set(row_of["eng_Latn"]) == set(row_of["yor_Latn"])

    # Every question the pilot touched in either language is excluded from both.
    pilot_keys = {key[lang][int(pid.rsplit("-", 1)[1])] for lang in LANGS for pid in pilot
                  if pid.startswith(f"belebele-{lang[:3]}-")}
    held_out = [k for k in key["eng_Latn"] if k not in pilot_keys]

    items = []
    for lang, ds in sets.items():
        for k in held_out:
            i = row_of[lang][k]
            assert ds[i]["correct_answer_num"] == sets["eng_Latn"][row_of["eng_Latn"][k]]["correct_answer_num"]
            items.append({**belebele_item(ds[i], lang, i), "pair": row_of["eng_Latn"][k]})
    path = DATA_DIR / "confirm.jsonl"
    with path.open("w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"{path}: {len(items)} items ({len(held_out)} questions per language; {len(pilot_keys)} of {n} used by the pilot dropped)")
    print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
