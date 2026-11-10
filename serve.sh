#!/usr/bin/env bash
# Local preview: http://localhost:8080
set -euo pipefail
cd "$(dirname "$0")"
python3 -m http.server 8080 --directory web_export
