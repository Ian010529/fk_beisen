from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity


@dataclass(slots=True)
class ImageSimilarity:
    phash: float
    orb: float
    ssim: float
    combined: float


def load_gray(path: str | Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Unable to read image: {path}")
    return img


def crop_content(gray: np.ndarray, threshold: int = 248, pad: int = 4) -> np.ndarray:
    """Crop near-white margins without assuming exact source dimensions."""
    mask = gray < threshold
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        return gray.copy()
    x0, x1 = max(0, xs.min() - pad), min(gray.shape[1], xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(gray.shape[0], ys.max() + pad + 1)
    return gray[y0:y1, x0:x1]


def letterbox(gray: np.ndarray, size: int = 512) -> np.ndarray:
    h, w = gray.shape[:2]
    if h <= 0 or w <= 0:
        raise ValueError("Empty image")
    scale = min(size / w, size / h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    resized = cv2.resize(gray, (nw, nh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    canvas = np.full((size, size), 255, dtype=np.uint8)
    x = (size - nw) // 2
    y = (size - nh) // 2
    canvas[y : y + nh, x : x + nw] = resized
    return canvas


def preprocess(gray: np.ndarray, size: int = 512) -> np.ndarray:
    gray = crop_content(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return letterbox(gray, size=size)


def phash_bits(gray: np.ndarray, hash_size: int = 16, highfreq_factor: int = 4) -> np.ndarray:
    """Perceptual hash implemented with DCT; unlike SHA/MD5 it tolerates re-encoding."""
    side = hash_size * highfreq_factor
    small = cv2.resize(gray, (side, side), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(small))[:hash_size, :hash_size]
    values = dct.flatten()
    median = np.median(values[1:]) if values.size > 1 else values[0]
    return values > median


def phash_similarity(a: np.ndarray, b: np.ndarray) -> float:
    ha, hb = phash_bits(a), phash_bits(b)
    return 1.0 - float(np.count_nonzero(ha != hb)) / float(ha.size)


def orb_similarity(a: np.ndarray, b: np.ndarray) -> float:
    orb = cv2.ORB_create(nfeatures=1800, fastThreshold=8)
    kpa, desa = orb.detectAndCompute(a, None)
    kpb, desb = orb.detectAndCompute(b, None)
    if desa is None or desb is None or not kpa or not kpb:
        return 0.0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs = matcher.knnMatch(desa, desb, k=2)
    good = []
    for pair in pairs:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.78 * n.distance:
            good.append(m)
    denom = max(1, min(len(kpa), len(kpb)))
    return min(1.0, len(good) / denom * 2.5)


def ssim_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        b = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
    score = float(structural_similarity(a, b, data_range=255))
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def compare_arrays(a: np.ndarray, b: np.ndarray) -> ImageSimilarity:
    pa, pb = preprocess(a), preprocess(b)
    p = phash_similarity(pa, pb)
    o = orb_similarity(pa, pb)
    s = ssim_similarity(pa, pb)
    # pHash is a broad recall signal; ORB and SSIM confirm structure.
    combined = 0.30 * p + 0.40 * o + 0.30 * s
    return ImageSimilarity(p, o, s, combined)


def compare_files(a: str | Path, b: str | Path) -> ImageSimilarity:
    return compare_arrays(load_gray(a), load_gray(b))
