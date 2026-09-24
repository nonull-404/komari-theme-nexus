#!/usr/bin/env bash
# 构建并发布 Komari Nexus 主题到 O1 面板
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
rm -f komari-theme-nexus-build-*.zip
bun run build
ZIP=$(ls -t komari-theme-nexus-build-*.zip | head -1)
python3 scripts/deploy-nexus.py "$ZIP" "$@"
