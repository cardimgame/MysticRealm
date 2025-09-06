
from core.config import TILE_W, TILE_H

def grid_to_screen(r: float, c: float) -> tuple[int, int]:
    x = int((c - r) * (TILE_W // 2))
    y = int((c + r) * (TILE_H // 2))
    return x, y

def screen_to_grid(x: float, y: float) -> tuple[float, float]:
    r = (y / (TILE_H / 2) - x / (TILE_W / 2)) / 2
    c = (y / (TILE_H / 2) + x / (TILE_W / 2)) / 2
    return r, c
