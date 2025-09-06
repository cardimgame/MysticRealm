import pygame
COLORS = {
    'bg': (8, 10, 14),
    'menu_item': (200, 200, 200),
    'menu_sel': (255, 255, 210),
    'hint': (180, 180, 180),
    'heading': (236, 200, 120),
}
SPACING = {'menu_gap': 56}
_FONT_CACHE: dict[int, pygame.font.Font] = {}

def get_font(size: int = 40) -> pygame.font.Font:
    if not pygame.font.get_init():
        pygame.font.init()
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.SysFont('serif', size)
    return _FONT_CACHE[size]
