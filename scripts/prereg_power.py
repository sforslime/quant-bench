"""Expected CI width and power of the confirmatory test (PREREG.md), from the pilot data.

Simulates confirm-sized datasets (N questions per language) by resampling the
pilot's 200 Belebele items with replacement, keeping each item's Q8_0/Q3_K_M
results together, and runs the pre-registered test (confirm_report.gap_test) on
each. The two languages are resampled independently: in the pilot, the English
and Yoruba rows with the same number are mostly different questions, so there is
no real pairing to carry over.

Usage: python scripts/prereg_power.py [--n 573] [--sims 500]
"""
import argparse
import json
import sys
from pathlib import Path
from statistics import NormalDist

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from config import MODELS, RESULTS_DIR
from confirm_report import PRIMARY, REF, gap_test

norm = NormalDist()
B = 2000  # resamples per simulated dataset (the real test uses 10,000)


def pilot(model):
    vecs = {}
    for quant in (REF, PRIMARY):
        rows = [json.loads(line) for line in (RESULTS_DIR / "quality" / f"{model}__{quant}.jsonl").open()]
        for lang in ("eng", "yor"):
            r = sorted((x for x in rows if x["task"] == "belebele" and x["lang"] == lang),
                       key=lambda x: int(x["id"].rsplit("-", 1)[1]))
            vecs[(lang, quant)] = np.array([x["correct"] for x in r], dtype=float)
    return vecs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=573)
    ap.add_argument("--sims", type=int, default=500)
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    idx = rng.integers(0, args.n, size=(B, args.n))
    print(f"N = {args.n} questions per language, {args.sims} simulated datasets, {B} resamples each\n")
    print("| model | pilot gap | pilot 95% CI width | expected 95% CI width (median) | SD of gap estimate "
          "| P(p < 0.05) | P(p < 0.025) | approx. power at half the pilot gap (p < 0.025 to 0.05) |")
    print("|---|---|---|---|---|---|---|---|")
    for model in MODELS:
        vecs = pilot(model)
        pilot_res = gap_test(vecs, PRIMARY, np.random.default_rng(0).integers(0, 200, size=(B, 200)))
        widths, gaps, ps = [], [], []
        for _ in range(args.sims):
            pick = {lang: rng.integers(0, 200, size=args.n) for lang in ("eng", "yor")}
            sim = {(lang, q): v[pick[lang]] for (lang, q), v in vecs.items()}
            r = gap_test(sim, PRIMARY, idx)
            widths.append(r["gap_hi"] - r["gap_lo"])
            gaps.append(r["gap"])
            ps.append(r["p_one_sided"])
        ps, se = np.array(ps), np.std(gaps)
        half = abs(pilot_res["gap"]) / 2 / se
        print(f"| {model} | {100 * pilot_res['gap']:+.0f} pts | {100 * (pilot_res['gap_hi'] - pilot_res['gap_lo']):.0f} pts "
              f"| {100 * np.median(widths):.0f} pts | {100 * se:.1f} pts | {np.mean(ps < 0.05):.2f} | {np.mean(ps < 0.025):.2f} "
              f"| {norm.cdf(half - norm.inv_cdf(0.975)):.2f} to {norm.cdf(half - norm.inv_cdf(0.95)):.2f} |")


if __name__ == "__main__":
    main()
