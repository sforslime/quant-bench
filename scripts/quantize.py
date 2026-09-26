"""Make the lower quants from each model's Q8_0 with llama-quantize.

Plain K-quants (no importance matrix), the same recipe for every model.
Q8_0 is near-lossless, so requantizing from it adds very little error.
Usage: python scripts/quantize.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import MODELS, QUANTS, REFERENCE_QUANT, gguf_path

for model in MODELS:
    src = gguf_path(model, REFERENCE_QUANT)
    if not src.exists():
        print(f"skip {model}: {src.name} not downloaded yet", flush=True)
        continue
    for quant in QUANTS:
        dst = gguf_path(model, quant)
        if quant == REFERENCE_QUANT or dst.exists():
            continue
        print(f"quantize {model} -> {quant}", flush=True)
        tmp = dst.with_suffix(".tmp")
        subprocess.run(["llama-quantize", "--allow-requantize", str(src), str(tmp), quant],
                       check=True, capture_output=True)
        tmp.rename(dst)
print("QUANTIZE DONE", flush=True)
