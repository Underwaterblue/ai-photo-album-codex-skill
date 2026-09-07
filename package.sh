#!/bin/bash
# Package the project into ai-photo-album-codex-skill.zip.
# Local photo/output data and build artifacts are excluded.
set -e

NAME="ai-photo-album-codex-skill"
rm -f "${NAME}.zip"

zip -r "${NAME}.zip" . \
  -x "photos/*" \
  -x "output/*" \
  -x "temp_blurred/*" \
  -x "*/__pycache__/*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x ".env" \
  -x ".DS_Store" \
  -x "*.zip"

echo "Packaged -> ${NAME}.zip"
