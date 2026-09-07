#!/bin/bash
# One-shot run: photo input folder -> generated albums -> HTML preview.
# Usage: ./run.sh [INPUT_DIR] [OUTPUT_DIR]
set -e

INPUT=${1:-./photos}
OUTPUT=${2:-./output}

mkdir -p "$OUTPUT"
pip install -r requirements.txt

python src/main.py --input "$INPUT" --albums 3 --pages 12 \
  --ratio 16:9 --dpi 300 --style-mode auto --style-strength balanced \
  --output "$OUTPUT"

open "$OUTPUT/index.html"
