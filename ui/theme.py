# ui/theme.py
import pygame

COLORS = {
 'bg': (8, 10, 14),
 'menu_item': (200, 200, 200),
 'menu_sel': (255, 255, 210),
 'hint': (180, 180, 180),
 'heading': (236, 200, 120),
}
SPACING = {'menu_gap': 56}

# Paleta adicional para Criador V2
PALETTE = {
    'bg_deep': (12,16,24),
    'panel':   (18,20,28),
    'edge':    (70,90,120),
    'text_hi': (235,235,235),
    'text_md': (210,210,220),
    'accent':  (230,210,160),
    'accent2': (74,94,120),
}

# Parâmetros de animação para Criador V2
ANIM = {
    'step_fade_ms': 180,
    'step_slide_px': 10,
}

_FONT_CACHE: dict[int, pygame.font.Font] = {}

def get_font(size: int = 40) -> pygame.font.Font:
    if not pygame.font.get_init():
        pygame.font.init()
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.SysFont('serif', size)
    return _FONT_CACHE[size]
