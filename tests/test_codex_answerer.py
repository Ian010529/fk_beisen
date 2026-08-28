import json
import subprocess

from beisen_practice_plus.codex_answerer import CodexAnswerer


def test_codex_answerer_maps_structured_result(tmp_path):
    command = tmp_path / "codex"
    command.write_text("", encoding="utf-8")
    command.chmod(0o755)

    def fake_runner(args, **kwargs):
        output_path = args[args.index("--output-last-message") + 1]
        with open(output_path, "w", encoding="utf-8") as output:
            json.dump({"option_index": 1, "confidence": 0.9, "reason": "四加四等于八"}, output)
        assert kwargs["input"].endswith('["6", "8", "10"]')
        return subprocess.CompletedProcess(args, 0, "", "")

    result = CodexAnswerer(command, runner=fake_runner).answer("4 + 4 = ?", ["6", "8", "10"])

    assert result["method"] == "codex"
    assert result["page_option_index"] == 1
    assert result["page_option_text"] == "8"
