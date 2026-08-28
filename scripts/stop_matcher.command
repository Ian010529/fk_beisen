#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
PID_FILE="$PROJECT_DIR/.matcher.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "识别服务未运行。"
  exit 0
fi

SERVICE_PID="$(<"$PID_FILE")"
if kill -0 "$SERVICE_PID" 2>/dev/null; then
  kill "$SERVICE_PID"
  echo "识别服务已停止（PID $SERVICE_PID）"
else
  echo "识别服务进程不存在。"
fi

rm -f "$PID_FILE"
