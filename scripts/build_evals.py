"""Build the fixed eval sets in data/*.jsonl. Deterministic: same SEED -> same items.

Each line: {"id", "task", "lang", "prompt", "choices", "answer"}.
Instructions are always in English; only the content (passage/tweet) changes
language, so differences in score come from the content, not the instructions.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import load_dataset

from config import DATA_DIR, N_ITEMS, SEED

LETTERS = ["A", "B", "C", "D"]
SENTIMENTS = ["positive", "negative", "neutral"]


def belebele(langs=("eng_Latn", "yor_Latn")):
    """Reading comprehension. The same question indices for every language (the rows are parallel translations)."""
    sets = {lang: load_dataset("facebook/belebele", lang)["test"] for lang in langs}
    n = len(sets[langs[0]])
    idx = sorted(random.Random(SEED).sample(range(n), N_ITEMS))
    out = []
    for lang, ds in sets.items():
        for i in idx:
            row = ds[i]
            options = "\n".join(f"{L}. {row[f'mc_answer{k + 1}']}" for k, L in enumerate(LETTERS))
            prompt = (
                "Read the passage and answer the question.\n\n"
                f"Passage:\n{row['flores_passage']}\n\n"
                f"Question: {row['question']}\n\n"
                f"{options}\n\n"
                "Answer with only the letter of the correct option (A, B, C, or D)."
            )
            out.append({
                "id": f"belebele-{lang[:3]}-{i}",
                "task": "belebele",
                "lang": lang[:3],
                "prompt": prompt,
                "choices": LETTERS,
                "answer": LETTERS[int(row["correct_answer_num"]) - 1],
            })
    return out


def balanced_sample(rows, label_of, rng):
    """N_ITEMS rows, as close to equal per class as possible (so accuracy isn't dominated by one label)."""
    by_label = {s: [r for r in rows if label_of(r) == s] for s in SENTIMENTS}
    per = [N_ITEMS // 3 + (1 if k < N_ITEMS % 3 else 0) for k in range(3)]
    picked = []
    for s, k in zip(SENTIMENTS, per):
        picked += rng.sample(by_label[s], k)
    rng.shuffle(picked)
    return picked


def sentiment_prompt(text):
    return (
        "Classify the sentiment of this social media post as positive, negative, or neutral.\n\n"
        f"Post: {text}\n\n"
        "Answer with only one word: positive, negative, or neutral."
    )


def sentiment():
    rng = random.Random(SEED)
    out = []

    # English: tweet_eval labels are 0=negative, 1=neutral, 2=positive.
    eng_names = {0: "negative", 1: "neutral", 2: "positive"}
    eng = [{"text": r["text"], "label": eng_names[r["label"]]} for r in load_dataset("cardiffnlp/tweet_eval", "sentiment")["test"]]
    for k, r in enumerate(balanced_sample(eng, lambda r: r["label"], rng)):
        out.append({"id": f"senti-eng-{k}", "task": "sentiment", "lang": "eng",
                    "prompt": sentiment_prompt(r["text"]), "choices": SENTIMENTS, "answer": r["label"]})

    for lang in ["pcm", "yor"]:
        rows = [{"text": r["tweet"], "label": r["label"]} for r in load_dataset("masakhane/afrisenti", lang)["test"]]
        for k, r in enumerate(balanced_sample(rows, lambda r: r["label"], rng)):
            out.append({"id": f"senti-{lang}-{k}", "task": "sentiment", "lang": lang,
                        "prompt": sentiment_prompt(r["text"]), "choices": SENTIMENTS, "answer": r["label"]})
    return out


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    items = belebele() + sentiment()
    path = DATA_DIR / "evals.jsonl"
    with path.open("w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    from collections import Counter
    print(path, len(items), Counter((i["task"], i["lang"]) for i in items))
