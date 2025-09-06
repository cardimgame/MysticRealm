
import pygame
from core.config import TILE_W, TILE_H

COLORS = {
    'GRASS': (62, 130, 68),
    'DIRT': (110, 84, 60),
    'WATER': (40, 100, 180),
    'SNOW': (225, 232, 240),
    'PATH': (160, 140, 100),
}

_outline = (0, 0, 0, 80)

def _diamond(color: tuple[int,int,int], alpha: int = 255) -> pygame.Surface:
    surf = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    cx, cy = TILE_W // 2, TILE_H // 2
    pts = [(cx, 0), (TILE_W - 1, cy), (cx, TILE_H - 1), (0, cy)]
    col = (*color, alpha)
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _outline, pts, 1)
    return surf

_cache: dict[str, pygame.Surface] = {}

def build_tile(token: str, tile_size: int | None = None) -> pygame.Surface:
    key = token
    if key in _cache:
        return _cache[key]
    low = token.lower()
    if low.startswith('grass'):
        img = _diamond(COLORS['GRASS'])
    elif low.startswith('dirt'):
        img = _diamond(COLORS['DIRT'])
    elif low.startswith('water') or low.startswith('wather'):
        img = _diamond(COLORS['WATER'])
    elif low.startswith('snow'):
        img = _diamond(COLORS['SNOW'])
    elif low.startswith('path'):
        img = _diamond(COLORS['PATH'])
    else:
        img = _diamond((150, 150, 150))
    _cache[key] = img
    return img
