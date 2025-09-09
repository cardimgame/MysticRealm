
# systems/prop_factory.py
"""
Placeholders de PROPS (árvores, rochas, placa etc.)
Desenhados em Pygame (sem assets) com sombras e highlights.

Integrar na cena:
    from core import props as core_props
    from systems.prop_factory import build_prop
    core_props.load_prop_image = build_prop
"""
import pygame, random, math
from functools import lru_cache

@lru_cache(maxsize=256)
def build_prop(key: str) -> pygame.Surface:
    k = (key or '').lower()
    if k.startswith('tree'):   return _tree(k)
    if k.startswith('rock'):   return _rock(k)
    if 'sign' in k:            return _sign(k)
    if 'bush' in k:            return _bush(k)
    return _generic(k)

def _surface(w, h):
    return pygame.Surface((w,h), pygame.SRCALPHA)

def _shadow_base(surf, cx, cy, w, h, a=72):
    sh = _surface(w, h)
    pygame.draw.ellipse(sh, (0,0,0,a), (0,0,w,h))
    surf.blit(sh, (cx-w//2, cy-h//2))

def _tree(k):
    w,h = 64, 92
    surf = _surface(w,h)
    # sombra
    _shadow_base(surf, w//2, h-14, int(w*0.52), int(h*0.16), a=64)
    # tronco
    pygame.draw.rect(surf, (110,80,55), (w//2-6, h-42, 12, 32), border_radius=4)
    # copa (triângulos empilhados)
    top = h-48
    colors = [(34,92,74), (38,112,90), (28,78,68)]
    widths = [52, 44, 34]
    for i,(c,wd) in enumerate(zip(colors, widths)):
        tri = [(w//2, top-18*i), (w//2+wd//2, top+10-18*i), (w//2-wd//2, top+10-18*i)]
        pygame.draw.polygon(surf, c, tri)
        pygame.draw.polygon(surf, (20,30,28), tri, 1)
    # brilho
    pygame.draw.circle(surf, (200,230,210,40), (w//2+8, top-30), 18)
    return surf

def _rock(k):
    w,h = 60, 52
    surf = _surface(w,h)
    _shadow_base(surf, w//2, h-8, int(w*0.60), int(h*0.32), a=58)
    poly = [(8,h-14),(18,8),(w-12,12),(w-6,h-18),(w//2,h-4)]
    pygame.draw.polygon(surf, (120,120,130), poly)
    pygame.draw.polygon(surf, (40,40,48), poly, 1)
    # highlights
    pygame.draw.line(surf, (200,200,210), (18,12), (w-18,14), 2)
    return surf

def _sign(k):
    w,h = 50, 64
    surf = _surface(w,h)
    _shadow_base(surf, w//2, h-10, int(w*0.52), int(h*0.22))
    # poste
    pygame.draw.rect(surf, (110,80,55), (w//2-4, 18, 8, h-28), border_radius=2)
    # placa
    rect = pygame.Rect(0,0, 40, 18); rect.midtop = (w//2, 16)
    pygame.draw.rect(surf, (160,120,70), rect, border_radius=3)
    pygame.draw.rect(surf, (60,40,28), rect, 1, border_radius=3)
    return surf

def _bush(k):
    w,h = 56, 44
    surf = _surface(w,h)
    _shadow_base(surf, w//2, h-6, int(w*0.60), int(h*0.34))
    for i in range(5):
        pygame.draw.circle(surf, (34+10*i, 120+5*i, 70+3*i), (10+i*10, h-16), 12)
    pygame.draw.circle(surf, (200,230,210,40), (w-10, h-22), 10)
    return surf

def _generic(k):
    w,h = 48, 48
    surf = _surface(w,h)
    _shadow_base(surf, w//2, h-8, int(w*0.52), int(h*0.28))
    pygame.draw.rect(surf, (80,90,110), (8,8,w-16,h-16), border_radius=6)
    pygame.draw.rect(surf, (30,34,48), (8,8,w-16,h-16), 1, border_radius=6)
    return surf
