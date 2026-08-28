from beisen_practice_plus.importer import parse_questions_js


def test_parse_questions_js():
    questions = parse_questions_js("tests/fixtures/questions.js")
    assert len(questions) == 3
    assert questions[0].id == "v-1"
    assert questions[2].category == "graphic"
