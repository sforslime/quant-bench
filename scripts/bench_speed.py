"""Speed sweep with llama-bench: prompt processing (pp512) and generation (tg128),
at an empty context and at 4k tokens already in context. 5 repetitions each.

Run this with nothing else heavy going on (no downloads, no quality runs).
Usage: python scripts/bench_speed.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RESULTS_DIR, configs, gguf_path

out_path = RESULTS_DIR / "speed.jsonl"
done = set()
if out_path.exists():
    done = {(r["model"], r["quant"]) for r in map(json.loads, out_path.open())}

for model, quant in configs():
    path = gguf_path(model, quant)
    if (model, quant) in done or not path.exists():
        print(f"skip {model} {quant}", flush=True)
        continue
    print(f"bench {model} {quant}", flush=True)
    proc = subprocess.run(
        ["llama-bench", "-m", str(path), "-p", "512", "-n", "128", "-d", "0,4096",
         "-r", "5", "-ngl", "99", "-o", "jsonl"],
        capture_output=True, text=True, check=True,
    )
    with out_path.open("a") as f:
        for line in proc.stdout.splitlines():
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            f.write(json.dumps({
                "model": model, "quant": quant,
                "test": "pp512" if r["n_prompt"] else "tg128",
                "depth": r.get("n_depth", 0),
                "tok_s": r["avg_ts"], "tok_s_std": r["stddev_ts"],
                "build": r.get("build_commit"), "gpu": r.get("gpu_info"),
            }) + "\n")
print("SPEED DONE", flush=True)
