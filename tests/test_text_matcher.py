from beisen_practice_plus.importer import parse_questions_js
from beisen_practice_plus.text_matcher import TextMatcher


def test_text_search_handles_punctuation_and_spacing():
    questions = parse_questions_js("tests/fixtures/questions.js")
    matcher = TextMatcher(questions)
    result = matcher.search("示例题，甲乙丙中选择正确项", limit=1)[0]
    assert result.question_id == "v-1"
    assert result.score > 0.90
