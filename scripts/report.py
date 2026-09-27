"""Turn results/*.jsonl into summary tables (results/summary.md, results/summary.json) and charts (results/*.png).

Usage: python scripts/report.py
"""
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import MODELS, QUANTS, REFERENCE_QUANT, RESULTS_DIR

QDIR = RESULTS_DIR / "quality"
LANG_NAME = {"eng": "English", "pcm": "Pidgin", "yor": "Yoruba"}
# Reference palette slots 1-3 (validated all-pairs for up to 3 series).
LANG_COLOR = {"eng": "#2a78d6", "pcm": "#eb6834", "yor": "#1baf7a"}
MODEL_COLOR = dict(zip(MODELS, ["#2a78d6", "#eb6834"]))
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
CHANCE = {"belebele": 0.25, "sentiment": 1 / 3}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK,
})


def bootstrap_ci(values, n=2000, seed=0):
    rng = random.Random(seed)
    k = len(values)
    means = sorted(sum(rng.choices(values, k=k)) / k for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def macro_f1(rows):
    labels = sorted({r["answer"] for r in rows})
    f1s = []
    for lab in labels:
        tp = sum(r["pred"] == lab and r["answer"] == lab for r in rows)
        fp = sum(r["pred"] == lab and r["answer"] != lab for r in rows)
        fn = sum(r["pred"] != lab and r["answer"] == lab for r in rows)
        f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return sum(f1s) / len(f1s)


def load_quality():
    rows, metas = [], []
    for path in sorted(QDIR.glob("*__*.jsonl")):
        model, quant = path.stem.split("__")
        for line in path.open():
            rows.append({"model": model, "quant": quant, **json.loads(line)})
        meta = path.with_suffix(".meta.json")
        if meta.exists():
            metas.append(json.loads(meta.read_text()))
    return pd.DataFrame(rows), pd.DataFrame(metas)


def score_table(df):
    out = []
    for (model, quant, task, lang), g in df.groupby(["model", "quant", "task", "lang"]):
        correct = g["correct"].astype(int).tolist()
        lo, hi = bootstrap_ci(correct)
        out.append({
            "model": model, "quant": quant, "task": task, "lang": lang,
            "acc": sum(correct) / len(correct), "ci_lo": lo, "ci_hi": hi, "n": len(correct),
            "macro_f1": macro_f1(g.to_dict("records")) if task == "sentiment" else None,
        })
    t = pd.DataFrame(out)
    ref = t[t.quant == REFERENCE_QUANT].set_index(["model", "task", "lang"])["acc"]
    t["retention"] = [row.acc / ref.get((row.model, row.task, row.lang), float("nan")) for row in t.itertuples()]
    t["qi"] = t.quant.map(QUANTS.index)
    return t.sort_values(["model", "task", "lang", "qi"])


def mcnemar_p(lost, gained):
    """Exact two-sided McNemar test: of the items whose correctness changed, is the split lopsided?"""
    n, k = lost + gained, min(lost, gained)
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_vs_reference(df):
    """Each quant vs. the same model's Q8_0 on the *same items*: change in accuracy, paired 95% CI, McNemar p."""
    out = []
    ref = df[df.quant == REFERENCE_QUANT].set_index(["model", "id"])["correct"]
    for (model, quant, task, lang), g in df[df.quant != REFERENCE_QUANT].groupby(["model", "quant", "task", "lang"]):
        pairs = [(int(ref[(model, i)]), int(c)) for i, c in zip(g["id"], g["correct"]) if (model, i) in ref.index]
        diffs = [q - r for r, q in pairs]
        lo, hi = bootstrap_ci(diffs)
        lost = sum(r == 1 and q == 0 for r, q in pairs)
        gained = sum(r == 0 and q == 1 for r, q in pairs)
        out.append({"model": model, "quant": quant, "task": task, "lang": lang,
                    "delta": sum(diffs) / len(diffs), "delta_lo": lo, "delta_hi": hi,
                    "lost": lost, "gained": gained, "p": mcnemar_p(lost, gained)})
    p = pd.DataFrame(out)
    p["p_holm"] = holm(p["p"])
    p["qi"] = p.quant.map(QUANTS.index)
    return p.sort_values(["model", "task", "lang", "qi"])


def holm(pvals):
    """Holm step-down adjusted p-values over the whole family of tests passed in."""
    m = len(pvals)
    adjusted, running = pd.Series(index=pvals.index, dtype=float), 0.0
    for k, i in enumerate(pvals.sort_values().index):
        running = max(running, min(1.0, (m - k) * pvals[i]))
        adjusted[i] = running
    return adjusted


N_BOOT = 2000


def skill_boot(ref, q, chance, rng):
    """Paired bootstrap of skill kept = (acc_q - chance) / (acc_ref - chance): resample item indices,
    using the same resampled items for both quants. Returns the B resampled values (nan if acc_ref <= chance)."""
    idx = rng.integers(0, len(ref), size=(N_BOOT, len(ref)))
    denom = ref[idx].mean(1) - chance
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denom > 0, (q[idx].mean(1) - chance) / denom, np.nan), idx


def aligned(df, model, quant, task, lang):
    """Correctness vector for one config, ordered by item number so languages and quants line up."""
    g = df[(df.model == model) & (df.quant == quant) & (df.task == task) & (df.lang == lang)]
    g = g.assign(k=g["id"].str.rsplit("-", n=1).str[1].astype(int)).sort_values("k")
    return g["k"].to_numpy(), g["correct"].astype(float).to_numpy()


def skill_intervals(df):
    """Skill kept with paired-bootstrap 95% CIs for every config, plus (Belebele only) the
    Yoruba-minus-English gap, where one resample of question numbers is shared by both languages."""
    rows, gaps = [], []
    for (model, task, lang), _ in df.groupby(["model", "task", "lang"]):
        k_ref, ref = aligned(df, model, REFERENCE_QUANT, task, lang)
        for quant in QUANTS:
            k_q, q = aligned(df, model, quant, task, lang)
            assert (k_ref == k_q).all()
            vals, _ = skill_boot(ref, q, CHANCE[task], np.random.default_rng(0))
            lo, hi = np.nanpercentile(vals, [2.5, 97.5])
            point = (q.mean() - CHANCE[task]) / (ref.mean() - CHANCE[task])
            rows.append({"model": model, "quant": quant, "task": task, "lang": lang,
                         "skill": point, "skill_lo": lo, "skill_hi": hi, "boot_dropped": int(np.isnan(vals).sum())})
    for model in sorted(set(df.model)):
        vecs = {(lang, quant): aligned(df, model, quant, "belebele", lang) for lang in ("eng", "yor") for quant in QUANTS}
        assert all((v[0] == vecs[("eng", REFERENCE_QUANT)][0]).all() for v in vecs.values())
        n = len(vecs[("eng", REFERENCE_QUANT)][1])
        for quant in QUANTS[1:]:
            idx = np.random.default_rng(0).integers(0, n, size=(N_BOOT, n))
            skill = {}
            for lang in ("eng", "yor"):
                ref, q = vecs[(lang, REFERENCE_QUANT)][1], vecs[(lang, quant)][1]
                denom = ref[idx].mean(1) - CHANCE["belebele"]
                with np.errstate(divide="ignore", invalid="ignore"):
                    skill[lang] = np.where(denom > 0, (q[idx].mean(1) - CHANCE["belebele"]) / denom, np.nan)
            diff = skill["yor"] - skill["eng"]
            point = {lang: (vecs[(lang, quant)][1].mean() - 0.25) / (vecs[(lang, REFERENCE_QUANT)][1].mean() - 0.25)
                     for lang in ("eng", "yor")}
            lo, hi = np.nanpercentile(diff, [2.5, 97.5])
            gaps.append({"model": model, "quant": quant, "gap": point["yor"] - point["eng"], "gap_lo": lo, "gap_hi": hi,
                         "share_yor_worse": float(np.nanmean(diff < 0))})
    s = pd.DataFrame(rows)
    s["qi"] = s.quant.map(QUANTS.index)
    return s.sort_values(["model", "task", "lang", "qi"]), pd.DataFrame(gaps)


def load_speed():
    p = RESULTS_DIR / "speed.jsonl"
    return pd.DataFrame([json.loads(l) for l in p.open()]) if p.exists() else pd.DataFrame()


def label_end(ax, x, y, text, color):
    """Emphasize a line's last point; its label is placed later by place_end_labels."""
    ax.plot([x], [y], "o", ms=8, color=color, mec=SURFACE, mew=2, zorder=4)
    ax._end_labels = getattr(ax, "_end_labels", []) + [(x, y, text)]


def place_end_labels(ax, min_gap_frac=0.07):
    """Direct labels at line ends, nudged apart vertically so they never overlap."""
    labels = sorted(getattr(ax, "_end_labels", []), key=lambda l: l[1])
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * min_gap_frac
    placed = []
    for x, y, text in labels:
        ly = max(y, placed[-1] + gap) if placed else y
        placed.append(ly)
        ax.annotate(text, (x, y), xytext=(x + 0.14, ly), textcoords="data", va="center", fontsize=9, color=INK_2)


def chart_by_language(t, task, title, fname):
    models = [m for m in MODELS if m in set(t.model)]
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 3.8), sharey=True, squeeze=False)
    for ax, model in zip(axes[0], models):
        sub = t[(t.model == model) & (t.task == task)]
        for lang, g in sub.groupby("lang"):
            g = g.sort_values("qi")
            ax.fill_between(g.qi, g.ci_lo, g.ci_hi, color=LANG_COLOR[lang], alpha=0.12, lw=0)
            ax.plot(g.qi, g.acc, color=LANG_COLOR[lang], lw=2, marker="o", ms=5)
            label_end(ax, g.qi.iloc[-1], g.acc.iloc[-1], LANG_NAME[lang], LANG_COLOR[lang])
        ax.axhline(CHANCE[task], color=INK_2, lw=1, ls=(0, (3, 3)))
        ax.annotate("chance", (0, CHANCE[task]), xytext=(0, 3), textcoords="offset points", fontsize=8, color=INK_2)
        ax.set_xticks(range(len(QUANTS)), QUANTS)
        ax.set_xlim(-0.3, len(QUANTS) - 0.2)
        ax.set_title(model, loc="left")
        ax.set_xlabel("quantization  (lighter  →  heavier compression)")
    for ax in axes[0]:
        place_end_labels(ax)
    axes[0][0].set_ylabel("accuracy (shaded: 95% CI)")
    axes[0][0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / fname, dpi=160)
    plt.close(fig)


def chart_skill_kept(sk):
    """Share of each model's above-chance skill (at Q8_0) that survives each quant, reading comprehension,
    with paired-bootstrap 95% CIs. Values below 0 mean worse than random guessing (collapse)."""
    models = [m for m in MODELS if m in set(sk.model)]
    bel = sk[sk.task == "belebele"]
    y_lo = min(-0.15, bel.skill_lo.min() - 0.05)
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 4.2), sharey=True, squeeze=False)
    for ax, model in zip(axes[0], models):
        ax.axhspan(y_lo, 0, color=INK_2, alpha=0.07, lw=0)
        ax.annotate("below chance = collapse", (-0.25, y_lo), xytext=(0, 4), textcoords="offset points", fontsize=8, color=INK_2)
        for lang, offset in (("eng", -0.07), ("yor", 0.07)):
            g = bel[(bel.model == model) & (bel.lang == lang)].sort_values("qi")
            x = g.qi + offset
            ax.errorbar(x, g.skill, yerr=[g.skill - g.skill_lo, g.skill_hi - g.skill],
                        color=LANG_COLOR[lang], lw=2, elinewidth=1.2, capsize=3, marker="o", ms=5)
            label_end(ax, x.iloc[-1], g.skill.iloc[-1], LANG_NAME[lang], LANG_COLOR[lang])
        ax.axhline(1, color=INK_2, lw=1, ls=(0, (3, 3)))
        ax.axhline(0, color=INK_2, lw=1)
        ax.annotate("random guessing", (-0.25, 0), xytext=(0, 3), textcoords="offset points", fontsize=8, color=INK_2)
        ax.set_xticks(range(len(QUANTS)), QUANTS)
        ax.set_xlim(-0.3, len(QUANTS) - 0.1)
        ax.set_ylim(y_lo, 1.3)
        ax.set_title(model, loc="left")
        ax.set_xlabel("quantization  (lighter  →  heavier compression)")
    for ax in axes[0]:
        place_end_labels(ax)
    axes[0][0].set_ylabel("skill above chance kept (Q8_0 = 100%)\nbars: paired-bootstrap 95% CI")
    axes[0][0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    fig.suptitle("Reading comprehension: how much of the model's real skill survives compression",
                 x=0.01, ha="left", fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "skill_kept.png", dpi=160)
    plt.close(fig)


def chart_quality_vs_size(t, metas):
    if metas.empty:
        return
    avg = t.groupby(["model", "quant"]).acc.mean().reset_index().merge(metas[["model", "quant", "file_gb"]], on=["model", "quant"])
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for model, g in avg.groupby("model"):
        g = g.sort_values("file_gb")
        ax.plot(g.file_gb, g.acc, color=MODEL_COLOR[model], lw=2, marker="o", ms=6, label=model)
        for r in g.itertuples():
            ax.annotate(r.quant, (r.file_gb, r.acc), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8, color=INK_2)
    ax.set_xlabel("file size (GB)")
    ax.set_ylabel("mean accuracy, all 5 task-language sets")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Quality vs. file size", loc="left")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "quality_vs_size.png", dpi=160)
    plt.close(fig)


def chart_speed(s):
    if s.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8), squeeze=False)
    for ax, (test, label) in zip(axes[0], [("tg128", "Generation speed (tokens/s)"), ("pp512", "Prompt reading speed (tokens/s)")]):
        for model, g in s[(s.test == test) & (s.depth == 0)].groupby("model"):
            g = g.assign(qi=g.quant.map(QUANTS.index)).sort_values("qi")
            ax.plot(g.qi, g.tok_s, color=MODEL_COLOR[model], lw=2, marker="o", ms=5)
            label_end(ax, g.qi.iloc[-1], g.tok_s.iloc[-1], model, MODEL_COLOR[model])
        ax.set_ylabel("tokens / second")
        ax.set_xticks(range(len(QUANTS)), QUANTS)
        ax.set_xlim(-0.3, len(QUANTS) + 0.6)
        ax.set_ylim(bottom=0)
        ax.set_title(label + ", empty context", loc="left")
        place_end_labels(ax)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "speed.png", dpi=160)
    plt.close(fig)


def ci_range(lo, hi):
    """'a to b', with a '+' on the upper bound when the interval crosses zero."""
    return f"{lo:.0f} to {hi:+.0f}" if lo < 0 < hi else f"{lo:.0f} to {hi:.0f}"


def fmt_pct(x):
    return "–" if pd.isna(x) else f"{100 * x:.1f}%"


def token_tax(df):
    """Pilot token tax (superseded: the pilot's English/Yoruba rows are mostly not translations of each
    other; see results/confirm/token_tax.json). Passage-only counts come from scripts/token_tax.py;
    full-prompt counts (English instructions + chat template included) come from the quality runs."""
    path = RESULTS_DIR / "token_tax.json"
    passages = json.loads(path.read_text()) if path.exists() else {}
    ref = df[(df.quant == REFERENCE_QUANT) & (df.task == "belebele")]
    prompt = ref.groupby(["model", "lang"]).prompt_tokens.mean()
    rows = []
    for model in sorted(set(ref.model)):
        p = passages.get(model, {})
        rows.append({"model": model,
                     "eng_passage": p.get("eng_tokens_mean"), "yor_passage": p.get("yor_tokens_mean"),
                     "passage_ratio": p.get("ratio_of_totals"), "n_passages": p.get("n_passages"),
                     "eng_prompt": prompt[(model, "eng")], "yor_prompt": prompt[(model, "yor")],
                     "prompt_ratio": prompt[(model, "yor")] / prompt[(model, "eng")]})
    return pd.DataFrame(rows)


def write_summary(df, t, sk, gaps, metas, s):
    lines = ["# Results summary", ""]
    pv = paired_vs_reference(df)
    lines += ["## Change vs. Q8_0 on the same items (paired)", "",
              "Negative = worse than Q8_0. *lost/gained*: items Q8_0 got right and this quant got wrong, and vice versa. "
              "p: exact McNemar test (uses only the items where the two quants disagree). "
              f"Holm p: adjusted for all {len(pv)} tests in this table. "
              "▼ = significant after Holm correction; ▽ = p < 0.05 before correction only.", "",
              "| model | quant | task | lang | Δ accuracy | paired 95% CI | lost / gained | p | Holm p |", "|---|---|---|---|---|---|---|---|---|"]
    for r in pv.itertuples():
        mark = " ▼" if r.p_holm < 0.05 else (" ▽" if r.p < 0.05 else "")
        lines.append(f"| {r.model} | {r.quant} | {r.task} | {r.lang} | {100 * r.delta:+.1f}{mark} | "
                     f"{100 * r.delta_lo:+.1f} to {100 * r.delta_hi:+.1f} | {r.lost} / {r.gained} | {r.p:.4f} | {r.p_holm:.4f} |")
    lines += ["", "## Skill kept (share of above-chance skill at Q8_0 that survives), paired-bootstrap 95% CI", "",
              f"Resamples the item IDs {N_BOOT} times, using the same items for the quant and Q8_0. "
              "Negative = below chance. Intervals are wide when Q8_0 starts close to chance "
              "(Yoruba Belebele starts less than 20 points above it).", "",
              "| model | task | lang | " + " | ".join(QUANTS) + " |", "|---|---|---|" + "---|" * len(QUANTS)]
    for (model, task, lang), g in sk.groupby(["model", "task", "lang"]):
        cells = [f"{100 * r.skill:.0f}% ({ci_range(100 * r.skill_lo, 100 * r.skill_hi)})" for r in g.sort_values("qi").itertuples()]
        lines.append(f"| {model} | {task} | {lang} | " + " | ".join(cells) + " |")
    lines += ["", "## Yoruba minus English skill kept (Belebele), paired-bootstrap 95% CI", "",
              "Pilot only: languages were matched by row number, which pairs the same question only 42 of 200 times, "
              "so these intervals are not truly paired and are unreliable. The corrected, pre-registered result is in "
              "[`results/confirm/summary.md`](confirm/summary.md). Negative = Yoruba lost a larger share of its skill. "
              "*P(Yoruba worse)* is the share of resamples where the gap is below 0.", "",
              "| model | quant | gap | 95% CI | P(Yoruba worse) |", "|---|---|---|---|---|"]
    for r in gaps.itertuples():
        lines.append(f"| {r.model} | {r.quant} | {100 * r.gap:+.0f} pts | {100 * r.gap_lo:+.0f} to {100 * r.gap_hi:+.0f} | {r.share_yor_worse:.2f} |")
    lines.append("")
    lines += ["## Accuracy by config (95% CI)", "", "| model | quant | task | lang | acc | 95% CI | % of Q8_0 | sentiment macro-F1 |", "|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        f1 = "" if r.macro_f1 is None or pd.isna(r.macro_f1) else f"{r.macro_f1:.3f}"
        lines.append(f"| {r.model} | {r.quant} | {r.task} | {r.lang} | {fmt_pct(r.acc)} | {fmt_pct(r.ci_lo)}–{fmt_pct(r.ci_hi)} | {fmt_pct(r.retention)} | {f1} |")
    tok = token_tax(df)
    lines += ["", "## Token tax: superseded pilot count (passages not correctly paired)", "",
              "The pilot matched English and Yoruba by row number, so most of these \"pairs\" are different passages. "
              "The corrected counts, on 421 correctly paired passages, are in "
              "[`results/confirm/token_tax.json`](confirm/token_tax.json): Yoruba ÷ English = 2.41× (Gemma) and 2.64× (Qwen) "
              "for passages, 1.92× and 2.07× for the full prompt.", "",
              "Passage-only: each unique passage pair counted once, special tokens excluded. "
              "Full prompt: the whole request as sent, including the English instructions and chat template, averaged over the 200 items.", "",
              "| model | passages | English passage tokens | Yoruba passage tokens | Yoruba ÷ English (passages) | Yoruba ÷ English (full prompt) |",
              "|---|---|---|---|---|---|"]
    for r in tok.itertuples():
        lines.append(f"| {r.model} | {r.n_passages} | {r.eng_passage:.1f} | {r.yor_passage:.1f} | {r.passage_ratio:.2f}× | {r.prompt_ratio:.2f}× |")
    if not metas.empty:
        lines += ["", "## Memory", "", "| model | quant | file GB | GPU weights MiB | GPU KV MiB (16k ctx) | GPU total MiB |", "|---|---|---|---|---|---|"]
        for r in metas.assign(qi=metas.quant.map(QUANTS.index)).sort_values(["model", "qi"]).itertuples():
            lines.append(f"| {r.model} | {r.quant} | {r.file_gb} | {r.gpu_model_mib:.0f} | {r.kv_mib:.0f} | {r.gpu_total_mib:.0f} |")
    if not s.empty:
        lines += ["", "## Speed (llama-bench, median of 5)", "", "| model | quant | test | context depth | tok/s | ± |", "|---|---|---|---|---|---|"]
        for r in s.assign(qi=s.quant.map(QUANTS.index)).sort_values(["model", "qi", "test", "depth"]).itertuples():
            lines.append(f"| {r.model} | {r.quant} | {r.test} | {r.depth} | {r.tok_s:.1f} | {r.tok_s_std:.1f} |")
    (RESULTS_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    t.drop(columns="qi").merge(sk.drop(columns="qi"), on=["model", "quant", "task", "lang"]).to_json(
        RESULTS_DIR / "summary.json", orient="records", indent=1)
    gaps.to_json(RESULTS_DIR / "skill_gap.json", orient="records", indent=1)
    pv.drop(columns="qi").to_json(RESULTS_DIR / "paired.json", orient="records", indent=1)


def main():
    df, metas = load_quality()
    s = load_speed()
    if df.empty:
        print("no quality results yet")
        return
    t = score_table(df)
    chart_by_language(t, "belebele", "Reading comprehension (Belebele): same questions in English and Yoruba", "belebele_by_language.png")
    chart_by_language(t, "sentiment", "Sentiment of social posts: English, Pidgin, Yoruba", "sentiment_by_language.png")
    sk, gaps = skill_intervals(df)
    chart_skill_kept(sk)
    chart_quality_vs_size(t, metas)
    chart_speed(s)
    write_summary(df, t, sk, gaps, metas, s)
    print((RESULTS_DIR / "summary.md").read_text()[:3000])


if __name__ == "__main__":
    main()
