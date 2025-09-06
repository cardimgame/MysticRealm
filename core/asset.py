
import pygame
from pygame import Surface
from typing import List, Tuple
from core.config import ASSETS_DIR

_missing: List[str] = []
_cache: dict[str, Surface] = {}

def _mark_missing(path: str):
    if path not in _missing:
        _missing.append(path)

def missing_assets() -> List[str]:
    return list(_missing)

def load_image_strict(rel_path: str) -> Surface | None:
    path = ASSETS_DIR / rel_path
    if not path.exists():
        _mark_missing(str(path))
        return None
    img = pygame.image.load(str(path))
    return img.convert_alpha() if img.get_alpha() else img.convert()

def load_scaled(rel_path: str, size: Tuple[int, int], smooth: bool = False) -> Surface | None:
    key = f"{rel_path}|{size}|{'s' if smooth else 'n'}"
    if key in _cache:
        return _cache[key]
    img = load_image_strict(rel_path)
    if img is None:
        return None
    if img.get_size() == size:
        _cache[key] = img
        return img
    out = pygame.transform.smoothscale(img, size) if smooth else pygame.transform.scale(img, size)
    _cache[key] = out
    return out
