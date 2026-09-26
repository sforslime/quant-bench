"""Shared settings for every script: which models, which quants, which eval items."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# Both from one quantizer (bartowski) so the quant recipe is the same across files.
MODELS = {
    "gemma4-e4b": {
        "repo": "bartowski/google_gemma-4-E4B-it-GGUF",
        "pattern": "google_gemma-4-E4B-it-{quant}.gguf",
    },
    "qwen3.5-4b": {
        "repo": "bartowski/Qwen_Qwen3.5-4B-GGUF",
        "pattern": "Qwen_Qwen3.5-4B-{quant}.gguf",
    },
}

# Ordered from lightest to heaviest compression. Q8_0 is the quality reference.
QUANTS = ["Q8_0", "Q6_K", "Q4_K_M", "Q3_K_M", "Q2_K"]
REFERENCE_QUANT = "Q8_0"

N_ITEMS = 200  # per task x language
SEED = 42

SERVER_PORT = 8091
CTX_SIZE = 4096


def gguf_path(model: str, quant: str) -> Path:
    return MODELS_DIR / MODELS[model]["pattern"].format(quant=quant)


def configs():
    """Every (model, quant) pair, in run order."""
    for model in MODELS:
        for quant in QUANTS:
            yield model, quant
