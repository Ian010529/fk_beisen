import cv2
import numpy as np

from beisen_practice_plus.models import Question
from beisen_practice_plus.question_matcher import QuestionMatcher


def encode(image):
    ok, data = cv2.imencode(".png", image)
    assert ok
    return data.tobytes()


def test_matches_text_and_maps_answer_by_option_text(tmp_path):
    questions = [Question(
        id="v-1",
        stem="每个人在学习新事物时都会有恐惧畏难的心态",
        options={"A": "因噎废食", "B": "瞻前顾后", "C": "首鼠两端", "D": "视为畏途"},
        answer="D",
        category="verbal",
    )]
    matcher = QuestionMatcher(questions, tmp_path)
    result = matcher.match(
        "学习新事物时都会有恐惧、畏难心态",
        ["首鼠两端", "视为畏途", "因噎废食", "瞻前顾后"],
    )
    assert result is not None
    assert result["question_id"] == "v-1"
    assert result["page_option_index"] == 1
    assert result["answer_text"] == "视为畏途"


def test_matches_known_question_image(tmp_path):
    image = np.full((240, 360), 255, dtype=np.uint8)
    cv2.rectangle(image, (50, 30), (300, 200), 0, 5)
    cv2.circle(image, (170, 115), 45, 0, 4)
    cv2.imwrite(str(tmp_path / "graphic-1.png"), image)
    questions = [Question(
        id="g-1",
        stem="请选择正确图形",
        options={"A": "图一", "B": "图二", "C": "图三", "D": "图四"},
        answer="C",
        images=["graphic-1.png"],
        category="graphic",
    )]
    matcher = QuestionMatcher(questions, tmp_path)
    resized = cv2.resize(image, (540, 360), interpolation=cv2.INTER_CUBIC)
    result = matcher.match("", ["图一", "图二", "图三", "图四"], [encode(resized)])
    assert result is not None
    assert result["question_id"] == "g-1"
    assert result["method"] in {"image", "text+image"}
    assert result["page_option_index"] == 2
