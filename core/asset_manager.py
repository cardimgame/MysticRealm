from typing import Optional
import pygame
from core.asset import load_image_strict

PATHS = {
    'ui.dragons_bg': 'ui/dragons_bg.png',
    'ui.main_bg': 'ui/main_menu.png',
    'ui.selection_arrow': 'ui/selection_arrow.png',
    'ui.selection_player': 'ui/selection_player.png',
}

_cache: dict[str, pygame.Surface] = {}

def get(key: str) -> Optional[pygame.Surface]:
    if key in _cache:
        return _cache[key]
    rel = PATHS.get(key)
    if not rel:
        return None
    img = load_image_strict(rel)
    if img is not None:
        _cache[key] = img
    return img
