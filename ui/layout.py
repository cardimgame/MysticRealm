import pygame
from typing import List, Tuple

def pos_frac(screen: pygame.Surface, x_frac: float, y_frac: float) -> tuple[int, int]:
    sw, sh = screen.get_size()
    return int(sw * x_frac), int(sh * y_frac)

def stack_right(screen: pygame.Surface, n: int, *, start_y_frac: float = 0.32, gap_px: int = 54, right_x_frac: float = 0.82) -> List[Tuple[int, int]]:
    sw, sh = screen.get_size()
    x = int(sw * right_x_frac)
    y = int(sh * start_y_frac)
    return [(x, y + i * gap_px) for i in range(n)]

def safe_area(screen: pygame.Surface, margin_frac: float = 0.06) -> pygame.Rect:
    sw, sh = screen.get_size()
    m = int(min(sw, sh) * margin_frac)
    return pygame.Rect(m, m, sw - 2 * m, sh - 2 * m)
