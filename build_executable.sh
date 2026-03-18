#!/usr/bin/env bash
set -euo pipefail

# Build a single-file executable archive (python zipapp) using shiv.
# Requires: python, pip, shiv, and a working internet connection to download dependencies.
#
# The output is written to dist/inbound-tms-diagram.pyz.

mkdir -p dist

python -m shiv \
  --output-file dist/inbound-tms-diagram.pyz \
  --entry-point inbound_tms_diagram_app:main \
  .

cat <<'EOF'
Built dist/inbound-tms-diagram.pyz.
Run it via:
  python dist/inbound-tms-diagram.pyz
EOF
