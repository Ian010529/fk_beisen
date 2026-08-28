#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
SERVICE_LABEL="com.fk-beisen.matcher"
SERVICE_DOMAIN="gui/$(id -u)"
BANK_PATH="$PROJECT_DIR/../beisen/src/data/questions.js"
IMAGE_PATH="$PROJECT_DIR/../beisen/public/question-bank"

cd "$PROJECT_DIR"

if launchctl print "$SERVICE_DOMAIN/$SERVICE_LABEL" >/dev/null 2>&1; then
  if curl -fsS --max-time 1 http://127.0.0.1:8765/health >/dev/null 2>&1; then
    echo "识别服务已运行：http://127.0.0.1:8765"
    exit 0
  fi
  launchctl remove "$SERVICE_LABEL"
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "未找到项目虚拟环境，请先按 README 安装依赖。"
  exit 1
fi

SERVER_COMMAND="cd ${(q)PROJECT_DIR} && exec ${(q)PROJECT_DIR}/.venv/bin/python -m beisen_practice_plus.cli serve --bank ${(q)BANK_PATH} --image-dir ${(q)IMAGE_PATH} --host 127.0.0.1 --port 8765"
launchctl submit -l "$SERVICE_LABEL" -- /bin/zsh -c "$SERVER_COMMAND"

for _ in {1..30}; do
  if curl -fsS --max-time 1 http://127.0.0.1:8765/health >/dev/null 2>&1; then
    echo "识别服务已启动：http://127.0.0.1:8765"
    exit 0
  fi
  sleep 0.1
done

echo "识别服务启动超时。"
exit 1
