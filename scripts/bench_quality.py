"""Run every eval item against every (model, quant) GGUF via llama-server.

For each config: start llama-server, record GPU memory from its log,
send all items (temperature 0, grammar-constrained to the valid labels), save
one line per item. Resumable: finished configs are skipped, and configs whose
GGUF hasn't downloaded yet are retried until --wait-for-downloads times out.

Usage: python scripts/bench_quality.py [--only MODEL] [--limit N] [--wait-for-downloads]
"""
import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from config import CTX_SIZE, DATA_DIR, RESULTS_DIR, SERVER_PORT, configs, gguf_path

PARALLEL = 4  # llama-server slots; batching several prompts is much faster on Metal
URL = f"http://127.0.0.1:{SERVER_PORT}"
OUT_DIR = RESULTS_DIR / "quality"


def grammar_for(choices):
    return "root ::= " + " | ".join(f'"{c}"' for c in choices)


def start_server(path: Path, log_path: Path):
    log = log_path.open("w")
    proc = subprocess.Popen(
        ["llama-server", "-m", str(path), "--port", str(SERVER_PORT),
         "-c", str(CTX_SIZE * PARALLEL), "-np", str(PARALLEL), "-ngl", "99",
         "--jinja", "--reasoning-budget", "0", "--no-webui", "-lv", "4"],
        stdout=log, stderr=subprocess.STDOUT,
    )
    for _ in range(300):
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server exited, see {log_path}")
        try:
            if requests.get(f"{URL}/health", timeout=1).status_code == 200:
                return proc
        except requests.ConnectionError:
            pass
        time.sleep(1)
    proc.kill()
    raise RuntimeError("llama-server did not become healthy")


def parse_memory(log_path: Path):
    """GPU (Metal) memory by kind, from the '... buffer size = X MiB' lines llama.cpp prints.

    CPU_Mapped model buffers are mmapped views of the same GGUF file as the GPU
    buffers, so they are recorded separately rather than added in (adding them
    double-counts). gpu_total_mib = weights + KV cache + compute scratch on the GPU.
    """
    mem = {"gpu_model_mib": 0.0, "cpu_mapped_mib": 0.0, "kv_mib": 0.0, "compute_mib": 0.0}
    for line in log_path.read_text(errors="ignore").splitlines():
        m = re.search(r"(\w+?)(?:_Mapped)? +(model|KV|compute) buffer size =\s*([\d.]+) MiB", line)
        if not m or not m.group(1).startswith("MTL"):
            if m and m.group(2) == "model":
                mem["cpu_mapped_mib"] += float(m.group(3))
            continue
        key = {"model": "gpu_model_mib", "KV": "kv_mib", "compute": "compute_mib"}[m.group(2)]
        mem[key] += float(m.group(3))
    mem["gpu_total_mib"] = mem["gpu_model_mib"] + mem["kv_mib"] + mem["compute_mib"]
    return mem


def ask(item):
    t0 = time.time()
    r = requests.post(f"{URL}/v1/chat/completions", timeout=600, json={
        "messages": [{"role": "user", "content": item["prompt"]}],
        "temperature": 0,
        "max_tokens": 8,
        "grammar": grammar_for(item["choices"]),
        "chat_template_kwargs": {"enable_thinking": False},
    })
    r.raise_for_status()
    body = r.json()
    pred = body["choices"][0]["message"]["content"].strip()
    return {
        "id": item["id"], "task": item["task"], "lang": item["lang"],
        "answer": item["answer"], "pred": pred, "correct": pred == item["answer"],
        "prompt_tokens": body["usage"]["prompt_tokens"], "seconds": round(time.time() - t0, 3),
    }


def run_config(model, quant, items):
    out_path = OUT_DIR / f"{model}__{quant}.jsonl"
    meta_path = OUT_DIR / f"{model}__{quant}.meta.json"
    log_path = OUT_DIR / f"{model}__{quant}.server.log"

    proc = start_server(gguf_path(model, quant), log_path)
    t0 = time.time()
    try:
        ask(items[0])  # warm-up, discarded
        with ThreadPoolExecutor(PARALLEL) as pool, out_path.with_suffix(".partial").open("w") as f:
            for n, row in enumerate(pool.map(ask, items), 1):
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                if n % 100 == 0:
                    print(f"  {model} {quant}: {n}/{len(items)}", flush=True)
    finally:
        proc.terminate()
        proc.wait()

    out_path.with_suffix(".partial").rename(out_path)
    meta = {
        "model": model, "quant": quant, "file": gguf_path(model, quant).name,
        "file_gb": round(gguf_path(model, quant).stat().st_size / 1e9, 3),
        "n_items": len(items), "wall_seconds": round(time.time() - t0, 1),
        "ctx_total": CTX_SIZE * PARALLEL,
        **parse_memory(log_path),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    acc = sum(r["correct"] for r in map(json.loads, out_path.open())) / len(items)
    print(f"DONE {model} {quant}: acc={acc:.3f} in {meta['wall_seconds']}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="run just this model")
    ap.add_argument("--limit", type=int, help="first N items only (smoke test; results go to a scratch dir)")
    ap.add_argument("--wait-for-downloads", action="store_true")
    args = ap.parse_args()

    global OUT_DIR
    items = [json.loads(line) for line in (DATA_DIR / "evals.jsonl").open()]
    if args.limit:
        # Spread the smoke test across every task/language.
        items = [it for k, it in enumerate(items) if k % (len(items) // args.limit) == 0][: args.limit]
        OUT_DIR = RESULTS_DIR / "smoke"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    todo = [(m, q) for m, q in configs() if not args.only or m == args.only]
    while todo:
        ready = [(m, q) for m, q in todo if gguf_path(m, q).exists()]
        for m, q in ready:
            todo.remove((m, q))
            if (OUT_DIR / f"{m}__{q}.meta.json").exists():
                print(f"skip {m} {q} (done)", flush=True)
                continue
            print(f"RUN {m} {q}", flush=True)
            run_config(m, q, items)
        if todo and not ready:
            if not args.wait_for_downloads:
                print(f"not downloaded yet, skipping: {todo}", flush=True)
                break
            time.sleep(30)
    print("ALL QUALITY RUNS COMPLETE", flush=True)


if __name__ == "__main__":
    main()
