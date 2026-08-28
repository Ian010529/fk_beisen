from beisen_practice_plus.importer import parse_questions_js
from beisen_practice_plus.validator import validate_questions


def test_validator_detects_bad_answer_and_conflict():
    questions = parse_questions_js("tests/fixtures/questions.js")
    issues = validate_questions(questions)
    codes = {i.code for i in issues if i.question_id == "g-1"}
    assert "invalid_answer" in codes
    assert "answer_analysis_conflict" in codes
