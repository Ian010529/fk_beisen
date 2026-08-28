# 北森题库识别助手

一个 Manifest V3 Chrome 扩展 + 本地 Python 匹配服务。扩展从北森或科大讯飞人才评估页面提取当前题干、选项和题图，本地服务在 445 道题库中搜索并高亮匹配选项。

默认只提示和高亮，不会自动提交答案或切换题目。

## 识别流程

1. 优先读取页面 DOM 中的题干与选项。
2. 性格量表题默认使用 `Blunnny/FUCK_BEISEN` 的分类题库和默认答案，也可切换积极、平衡或随机策略，不依赖本地服务。
3. 能力题使用 RapidFuzz 对标准化后的题干和选项做模糊检索。
4. 图表/图形题读取页面原图，用 pHash 粗排图库，再用 ORB + SSIM 复核。
5. 根据题库答案文本重新匹配页面选项，不依赖页面 A/B/C/D 顺序。

进入全屏后无需点击浏览器工具栏，可使用页面悬浮面板或按 `Alt/⌥ + Shift + B` 识别当前题。开启“自动识别新题”后，切换题目约 0.5 秒会自动识别。
6. 只有达到置信度阈值时才高亮建议选项。

## 本地资源

默认直接使用同级 `beisen` 项目，不下载、不复制题库图片：

```text
my_project/
├── beisen/
│   ├── src/data/questions.js
│   └── public/question-bank/
└── fk_beisen/
```

也可以在启动命令中传入其他路径。

## 启动识别服务

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

beisen-practice serve \
  --bank ../beisen/src/data/questions.js \
  --image-dir ../beisen/public/question-bank
```

服务默认监听 `http://127.0.0.1:8765`。健康检查：

```bash
curl http://127.0.0.1:8765/health
```

macOS 也可以双击 `scripts/start_matcher.command` 后台启动，双击 `scripts/stop_matcher.command` 停止。服务不会由 Chrome 扩展自动启动。

## 加载 Chrome 扩展

1. 打开 `chrome://extensions`。
2. 开启“开发者模式”。
3. 点击“加载已解压的扩展程序”。
4. 选择 `fk_beisen` 目录。
5. 打开北森或科大讯飞人才评估页面。进入题目后会自动识别并高亮，右上角可关闭“自动识别新题”。

插件图标弹窗也可检查本地服务状态并触发识别。

扩展脚本会注入题目 iframe，因此页面进入全屏后仍能显示识别面板。题目内容变化后会等待 500ms 自动识别，同一题不会重复请求。

## CLI 工具

原有本地题库工具仍可使用：

```bash
beisen-practice search data/question_bank.json "题干文本" --limit 5
beisen-practice compare-images ./question.png ./bank-image.jpg
beisen-practice validate data/question_bank.json
```

## 测试

```bash
pytest -q
node --check background.js
node --check content.js
node --check popup.js
python -m json.tool manifest.json
```

## 来源与许可

- 扩展形态参考 [`1642778819-pixel/beisen-psychometric-helper`](https://github.com/1642778819-pixel/beisen-psychometric-helper)。该仓库 README 声明 MIT，但仓库未附独立 `LICENSE` 文件。
- 心理单选分类和形容词排序来自 MIT 许可的 [`Blunnny/FUCK_BEISEN`](https://github.com/Blunnny/FUCK_BEISEN)，版权声明见 `third_party/Blunnny-FUCK_BEISEN-LICENSE.txt`。
- DOM 截图/OCR 组织方式参考 [`ArtLjn/chaoxing-qa`](https://github.com/ArtLjn/chaoxing-qa)。
- 题库来自 [`Liqing-Lin/BeiSen_Practice`](https://github.com/Liqing-Lin/BeiSen_Practice)，本仓库不重新发布题库文本和图片。

本仓库代码按 [MIT License](LICENSE) 发布。请仅用于自己的本地练习、题库质量检查和研究。
