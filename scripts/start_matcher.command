#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
PID_FILE="$PROJECT_DIR/.matcher.pid"
LOG_FILE="$PROJECT_DIR/.matcher.log"

cd "$PROJECT_DIR"

if [[ -f "$PID_FILE" ]]; then
  RUNNING_PID="$(<"$PID_FILE")"
  if kill -0 "$RUNNING_PID" 2>/dev/null; then
    echo "识别服务已运行（PID $RUNNING_PID）"
    exit 0
  fi
fi

if [[ ! -x .venv/bin/beisen-practice ]]; then
  echo "未找到项目虚拟环境，请先按 README 安装依赖。"
  exit 1
fi

nohup .venv/bin/beisen-practice serve \
  --bank ../beisen/src/data/questions.js \
  --image-dir ../beisen/public/question-bank \
  >"$LOG_FILE" 2>&1 &

SERVICE_PID=$!
echo "$SERVICE_PID" >"$PID_FILE"
sleep 1

if kill -0 "$SERVICE_PID" 2>/dev/null; then
  echo "识别服务已启动：http://127.0.0.1:8765（PID $SERVICE_PID）"
else
  echo "启动失败，请查看 $LOG_FILE"
  exit 1
fi
