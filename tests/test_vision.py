import cv2
import numpy as np

from beisen_practice_plus.vision import compare_arrays


def make_image():
    img = np.full((240, 360), 255, dtype=np.uint8)
    cv2.rectangle(img, (80, 50), (280, 190), 0, 4)
    cv2.circle(img, (180, 120), 42, 0, 4)
    cv2.line(img, (120, 120), (240, 120), 0, 3)
    return img


def test_visual_similarity_tolerates_resize_and_jpeg_like_blur():
    a = make_image()
    b = cv2.resize(a, (540, 360), interpolation=cv2.INTER_CUBIC)
    b = cv2.GaussianBlur(b, (3, 3), 0)
    result = compare_arrays(a, b)
    assert result.phash > 0.50
    assert result.orb > 0.70
    assert result.ssim > 0.90
    assert result.combined > 0.80
