import json
import subprocess

from beisen_practice_plus.codex_answerer import CodexAnswerer


def test_codex_answerer_maps_structured_result(tmp_path):
    command = tmp_path / "codex"
    command.write_text("", encoding="utf-8")
    command.chmod(0o755)

    calls = []

    def fake_runner(args, **kwargs):
        calls.append(args)
        output_path = args[args.index("--output-last-message") + 1]
        image_path = args[args.index("--image") + 1]
        assert image_path.endswith("question-0.png")
        with open(output_path, "w", encoding="utf-8") as output:
            json.dump({"option_index": 1, "confidence": 0.9, "reason": "四加四等于八"}, output)
        assert kwargs["input"].endswith('["6", "8", "10"]')
        return subprocess.CompletedProcess(args, 0, "", "")

    answerer = CodexAnswerer(command, runner=fake_runner)
    question = ("4 + 4 = ?", ["6", "8", "10"], [b"\x89PNG\r\n\x1a\nimage"])
    result = answerer.answer(*question)

    assert result["method"] == "codex"
    assert result["page_option_index"] == 1
    assert result["page_option_text"] == "8"
    assert result["input_images"] == 1
    assert calls[0][calls[0].index("--model") + 1] == "gpt-5.6-luna"
    assert 'model_reasoning_effort="low"' in calls[0]

    assert answerer.answer(*question) == result
    assert len(calls) == 1
