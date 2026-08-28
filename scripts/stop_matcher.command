#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
SERVICE_LABEL="com.fk-beisen.matcher"
SERVICE_DOMAIN="gui/$(id -u)"

if ! launchctl print "$SERVICE_DOMAIN/$SERVICE_LABEL" >/dev/null 2>&1; then
  echo "识别服务未运行。"
  exit 0
fi

launchctl remove "$SERVICE_LABEL"
rm -f "$PROJECT_DIR/.matcher.pid"
echo "识别服务已停止。"
