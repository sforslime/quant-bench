#!/bin/sh
# Resumable download of the two Q8_0 files with checksum verification.
# (Faster and more reliable than hf_hub_download on a slow link.)
set -e
cd "$(dirname "$0")/../models"
get() {
  repo=$1; f=$2
  [ -f "$f" ] && { echo "have $f"; return; }
  echo "downloading $f"
  curl -sSL -C - --retry 20 --retry-all-errors -o "$f.part" "https://huggingface.co/$repo/resolve/main/$f"
  mv "$f.part" "$f"
  grep " $f\$" SHA256SUMS | shasum -a 256 -c -
}
get bartowski/Qwen_Qwen3.5-4B-GGUF Qwen_Qwen3.5-4B-Q8_0.gguf
get bartowski/google_gemma-4-E4B-it-GGUF google_gemma-4-E4B-it-Q8_0.gguf
echo "ALL DOWNLOADS COMPLETE"
