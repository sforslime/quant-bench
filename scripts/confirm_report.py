"""Pre-registered analysis of the confirmatory Belebele run (PREREG.md).

Reads results/confirm/<model>__<quant>.jsonl and writes results/confirm/summary.md,
results/confirm/summary.json and results/confirm/gap.png.

Primary test, per model: gap = skill_kept(yor) - skill_kept(eng) at Q3_K_M, where
skill_kept = (acc - 0.25) / (acc_Q8_0 - 0.25). Paired bootstrap over the shared
question ("pair") numbers: B resamples, one index matrix used for both languages,
all quants and both models. One-sided p for gap < 0:
    p = (1 + #{b : gap_b >= 0 or undefined}) / (B + 1)
Holm-adjusted across the 2 models; supported if Holm p < 0.05.
Secondary (exploratory): the same gap at Q4_K_M, no decision attached.

Usage: python scripts/confirm_report.py [--dir results/confirm]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import MODELS, RESULTS_DIR
from report import INK, INK_2, LANG_COLOR, LANG_NAME, holm

CHANCE = 0.25
REF, PRIMARY, SECONDARY = "Q8_0", "Q3_K_M", "Q4_K_M"
QUANTS = [REF, SECONDARY, PRIMARY]
N_BOOT = 10_000
SEED = 20260926
ALPHA = 0.05
# Pilot (200-item) point estimates of the gap, from results/skill_gap.json, for reference only.
PILOT_GAP = {("gemma4-e4b", "Q4_K_M"): -0.251, ("gemma4-e4b", "Q3_K_M"): -0.482,
             ("qwen3.5-4b", "Q4_K_M"): -0.029, ("qwen3.5-4b", "Q3_K_M"): -0.400}


def load(results_dir):
    """{model: {(lang, quant): correctness vector ordered by pair}} plus the pair numbers."""
    data = {}
    for model in MODELS:
        vecs = {}
        for quant in QUANTS:
            path = results_dir / f"{model}__{quant}.jsonl"
            if not (results_dir / f"{model}__{quant}.meta.json").exists():
                raise SystemExit(f"{model} {quant} is not finished; the analysis runs only on complete data")
            rows = pd.DataFrame([json.loads(line) for line in path.open()])
            for lang in ("eng", "yor"):
                g = rows[rows.lang == lang].sort_values("pair")
                vecs[(lang, quant)] = (g["pair"].to_numpy(), g["correct"].astype(float).to_numpy())
        pairs = vecs[("eng", REF)][0]
        assert len(set(pairs)) == len(pairs)
        assert all((p == pairs).all() for p, _ in vecs.values()), f"{model}: languages/quants cover different questions"
        data[model] = {k: v for k, (_, v) in vecs.items()}
    return data, pairs


def skill(ref, q):
    """skill_kept along the last axis; nan where the reference is not above chance."""
    denom = ref.mean(-1) - CHANCE
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denom > 0, (q.mean(-1) - CHANCE) / denom, np.nan)


def gap_test(vecs, quant, idx):
    """Point gap, bootstrap gaps and one-sided p for gap < 0, using the given resample index matrix."""
    point = {lang: float(skill(vecs[(lang, REF)], vecs[(lang, quant)])) for lang in ("eng", "yor")}
    boot = {lang: skill(vecs[(lang, REF)][idx], vecs[(lang, quant)][idx]) for lang in ("eng", "yor")}
    diff = boot["yor"] - boot["eng"]
    undefined = int(np.isnan(diff).sum())
    p = (1 + int((diff[~np.isnan(diff)] >= 0).sum()) + undefined) / (len(diff) + 1)
    lo, hi = np.nanpercentile(diff, [2.5, 97.5])
    boot_skill = {lang: np.nanpercentile(boot[lang], [2.5, 97.5]) for lang in boot}
    return {"quant": quant, "skill_eng": point["eng"], "skill_yor": point["yor"],
            "skill_eng_lo": boot_skill["eng"][0], "skill_eng_hi": boot_skill["eng"][1],
            "skill_yor_lo": boot_skill["yor"][0], "skill_yor_hi": boot_skill["yor"][1],
            "gap": point["yor"] - point["eng"], "gap_lo": lo, "gap_hi": hi,
            "p_one_sided": p, "undefined_resamples": undefined}


def analyse(data, n, n_boot=N_BOOT, seed=SEED):
    idx = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    rows = [{"model": m, **gap_test(vecs, q, idx)} for m, vecs in data.items() for q in (PRIMARY, SECONDARY)]
    res = pd.DataFrame(rows)
    prim = res.quant == PRIMARY
    res.loc[prim, "p_holm"] = holm(res.loc[prim, "p_one_sided"]).to_numpy()
    res["role"] = np.where(prim, "primary", "secondary (exploratory)")
    res["supported"] = np.where(prim, res.p_holm < ALPHA, None)
    return res


def accuracy_table(data, idx):
    out = []
    for model, vecs in data.items():
        for (lang, quant), v in vecs.items():
            lo, hi = np.percentile(v[idx].mean(1), [2.5, 97.5])
            out.append({"model": model, "lang": lang, "quant": quant, "acc": v.mean(), "lo": lo, "hi": hi})
    return pd.DataFrame(out)


def chart(res, path):
    """The gap with its 95% CI for each model: primary (Q3_K_M) and exploratory (Q4_K_M)."""
    models = [m for m in MODELS if m in set(res.model)]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ylabels, y = [], 0
    for model in models:
        for quant in (PRIMARY, SECONDARY):
            r = res[(res.model == model) & (res.quant == quant)].iloc[0]
            primary = quant == PRIMARY
            color = LANG_COLOR["yor"] if primary else INK_2
            ax.errorbar([100 * r.gap], [y], xerr=[[100 * (r.gap - r.gap_lo)], [100 * (r.gap_hi - r.gap)]],
                        fmt="o", color=color, ms=8 if primary else 6, elinewidth=2, capsize=4,
                        mfc=color if primary else "white", mew=2, zorder=3)
            ax.plot([100 * PILOT_GAP[(model, quant)]], [y], marker="x", color=INK_2, ms=7, mew=1.5, ls="none", zorder=2)
            note = fmt_p(r.p_one_sided) + (f", Holm {fmt_p(r.p_holm)}" if primary else "")
            ylabels.append(f"{model}  {quant}" + ("" if primary else " (exploratory)")
                           + f"\n{100 * r.gap:+.0f} pts, {note}".replace("-", "−"))
            y += 1
        y += 0.5
    ticks = [0, 1, 2.5, 3.5][: len(ylabels)]
    ax.set_yticks(ticks, ylabels)
    ax.set_ylim(ticks[-1] + 0.6, -1.1)  # inverted, with headroom for the direction labels
    ax.axvline(0, color=INK_2, lw=1)
    lo = min(-100, 100 * res.gap_lo.min() - 10)
    ax.set_xlim(lo, max(40, 100 * res.gap_hi.max() + 15))
    ax.axvspan(lo, 0, color=LANG_COLOR["yor"], alpha=0.05, lw=0)
    ax.annotate("← Yoruba loses more", (0, -0.75), xytext=(-6, 0), textcoords="offset points",
                ha="right", va="center", fontsize=8, color=INK_2)
    ax.annotate("English loses more →", (0, -0.75), xytext=(6, 0), textcoords="offset points",
                ha="left", va="center", fontsize=8, color=INK_2)
    ax.set_xlabel("Yoruba minus English skill kept, percentage points (95% CI)\n× = pilot estimate (200 items)")
    ax.grid(axis="y", visible=False)
    fig.suptitle("Confirmatory test: does 3-bit compression cost Yoruba more of its skill than English?",
                 x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def fmt_p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def verdict(r):
    return "**supported**" if r.supported else "**not supported**"


def write_summary(res, acc, n, results_dir):
    lines = ["# Confirmatory Belebele test: results", "",
             f"Pre-registered in [PREREG.md](../../PREREG.md). {n} held-out parallel questions per language; "
             f"paired bootstrap over question numbers, {N_BOOT:,} resamples (seed {SEED}), one index matrix "
             "shared by both languages, all quants and both models.", "",
             "## Primary test: Yoruba minus English skill kept at Q3_K_M", "",
             "Decision rule: supported for a model if its Holm-adjusted one-sided p (across the 2 models) is < 0.05.", "",
             "| model | skill kept, English | skill kept, Yoruba | gap | 95% CI | one-sided p | Holm p | hypothesis |",
             "|---|---|---|---|---|---|---|---|"]
    for r in res[res.role == "primary"].itertuples():
        lines.append(f"| {r.model} | {100 * r.skill_eng:.0f}% ({100 * r.skill_eng_lo:.0f} to {100 * r.skill_eng_hi:.0f}) | "
                     f"{100 * r.skill_yor:.0f}% ({100 * r.skill_yor_lo:.0f} to {100 * r.skill_yor_hi:.0f}) | "
                     f"{100 * r.gap:+.1f} pts | {100 * r.gap_lo:+.1f} to {100 * r.gap_hi:+.1f} | "
                     f"{r.p_one_sided:.4f} | {r.p_holm:.4f} | {verdict(r)} |")
    lines += ["", "## Secondary (exploratory): the same gap at Q4_K_M", "",
              "No decision rule and no multiplicity correction; for description only.", "",
              "| model | skill kept, English | skill kept, Yoruba | gap | 95% CI | one-sided p |", "|---|---|---|---|---|---|"]
    for r in res[res.role != "primary"].itertuples():
        lines.append(f"| {r.model} | {100 * r.skill_eng:.0f}% ({100 * r.skill_eng_lo:.0f} to {100 * r.skill_eng_hi:.0f}) | "
                     f"{100 * r.skill_yor:.0f}% ({100 * r.skill_yor_lo:.0f} to {100 * r.skill_yor_hi:.0f}) | "
                     f"{100 * r.gap:+.1f} pts | {100 * r.gap_lo:+.1f} to {100 * r.gap_hi:+.1f} | {r.p_one_sided:.4f} |")
    lines += ["", "![Gap with 95% CI](gap.png)", "", "## Accuracy (bootstrap 95% CI, same resamples)", "",
              "| model | lang | " + " | ".join(QUANTS) + " |", "|---|---|" + "---|" * len(QUANTS)]
    for (model, lang), g in acc.groupby(["model", "lang"], sort=False):
        g = g.set_index("quant")
        lines.append(f"| {model} | {LANG_NAME[lang]} | " + " | ".join(
            f"{100 * g.acc[q]:.1f}% ({100 * g.lo[q]:.1f}–{100 * g.hi[q]:.1f})" for q in QUANTS) + " |")
    undefined = int(res.undefined_resamples.sum())
    lines += ["", f"Resamples where skill kept was undefined (Q8_0 at or below chance): {undefined}. "
              "They count against the hypothesis in the p-value and are left out of the intervals."]
    (results_dir / "summary.md").write_text("\n".join(lines) + "\n")
    res.to_json(results_dir / "summary.json", orient="records", indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=RESULTS_DIR / "confirm")
    args = ap.parse_args()
    data, pairs = load(args.dir)
    n = len(pairs)
    res = analyse(data, n)
    acc = accuracy_table(data, np.random.default_rng(SEED).integers(0, n, size=(N_BOOT, n)))
    chart(res, args.dir / "gap.png")
    write_summary(res, acc, n, args.dir)
    print((args.dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
