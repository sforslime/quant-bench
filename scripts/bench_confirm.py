"""Confirmatory run (PREREG.md): every data/confirm.jsonl item against each model at
Q8_0, Q4_K_M and Q3_K_M, with exactly the server settings, request and grammar of
bench_quality.py (imported from it, not copied).

Writes results/confirm/<model>__<quant>.jsonl in the results/quality/ format, plus
"pair" (the shared English row number, used to pair the two languages).

Resumable at the item level: each answer is appended and flushed to a .partial
file as it arrives; on restart, items already in it are skipped. A config is
finished when its .meta.json exists.

Usage: python scripts/bench_confirm.py
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bench_quality import PARALLEL, ask, parse_memory, start_server

from config import CTX_SIZE, DATA_DIR, MODELS, RESULTS_DIR, gguf_path

QUANTS = ["Q8_0", "Q4_K_M", "Q3_K_M"]
OUT_DIR = RESULTS_DIR / "confirm"


def load_done(partial: Path):
    """Rows already answered. A torn last line (crash mid-write) is dropped and rewritten."""
    if not partial.exists():
        return []
    rows = []
    for line in partial.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            break
    partial.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    return rows


def run_config(model, quant, items):
    out_path = OUT_DIR / f"{model}__{quant}.jsonl"
    partial = out_path.with_suffix(".partial")
    meta_path = OUT_DIR / f"{model}__{quant}.meta.json"
    log_path = OUT_DIR / f"{model}__{quant}.server.log"

    done = {r["id"] for r in load_done(partial)}
    todo = [it for it in items if it["id"] not in done]
    print(f"RUN {model} {quant}: {len(done)} already done, {len(todo)} to go", flush=True)

    t0 = time.time()
    if todo:
        proc = start_server(gguf_path(model, quant), log_path)
        try:
            ask(todo[0])  # warm-up, discarded
            with ThreadPoolExecutor(PARALLEL) as pool, partial.open("a") as f:
                for n, (it, row) in enumerate(zip(todo, pool.map(ask, todo)), 1):
                    f.write(json.dumps({**row, "pair": it["pair"]}, ensure_ascii=False) + "\n")
                    f.flush()
                    if n % 100 == 0:
                        print(f"  {model} {quant}: {len(done) + n}/{len(items)}", flush=True)
        finally:
            proc.terminate()
            proc.wait()

    # Write in item order, whatever order resumes left the partial file in.
    by_id = {r["id"]: r for r in load_done(partial)}
    assert set(by_id) == {it["id"] for it in items}, "missing items; re-run to resume"
    out_path.write_text("".join(json.dumps(by_id[it["id"]], ensure_ascii=False) + "\n" for it in items))
    partial.unlink()
    meta = {
        "model": model, "quant": quant, "file": gguf_path(model, quant).name,
        "file_gb": round(gguf_path(model, quant).stat().st_size / 1e9, 3),
        "n_items": len(items), "wall_seconds_last_session": round(time.time() - t0, 1),
        "resumed": bool(done), "ctx_total": CTX_SIZE * PARALLEL,
        **(parse_memory(log_path) if log_path.exists() else {}),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"DONE {model} {quant} in {meta['wall_seconds_last_session']}s", flush=True)


def main():
    items = [json.loads(line) for line in (DATA_DIR / "confirm.jsonl").open()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        for quant in QUANTS:
            if (OUT_DIR / f"{model}__{quant}.meta.json").exists():
                print(f"skip {model} {quant} (done)", flush=True)
                continue
            run_config(model, quant, items)
    print("ALL CONFIRM RUNS COMPLETE", flush=True)


if __name__ == "__main__":
    main()
