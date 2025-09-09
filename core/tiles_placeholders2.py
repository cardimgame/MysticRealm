# core/tiles_placeholders2.py
import pygame
from functools import lru_cache
from core.iso_math2 import TILE_W, TILE_H

DEBUG_LABELS = True  # coloque False quando não quiser textos grandes

COLORS = {
    'grass': ((66,128,66),(36,84,44)),
    'sand':  ((205,180,110),(170,140,90)),
    'water': ((34,82,140),(10,36,88)),
    'shore': ((240,240,255),(200,210,230)),
    'path':  ((140,110,85),(110,80,60)),
    'snow':  ((235,240,252),(218,228,245)),
    'snow_patch': ((235,240,252),(218,228,245)),
    'rock_crack': ((70,70,84),(40,40,52)),
    'ice_crack':  ((90,150,200),(60,110,160)),
    'dbg_city': ((60,60,68),(32,32,40)),
    'dbg_village': ((60,68,60),(28,40,28)),
    'dbg_cave': ((40,50,70),(20,26,44)),
    'dbg_dungeon': ((66,50,86),(34,24,56)),
}

@lru_cache(maxsize=256)
def _build(token:str)->pygame.Surface:
    t = (token or 'grass').lower()
    a,b = COLORS.get(t, COLORS['grass'])
    w,h=TILE_W,TILE_H; W,H=w*2,h*2
    surf = pygame.Surface((W,H), pygame.SRCALPHA)
    # gradiente simples
    for y in range(H):
        f = y/max(1,H-1)
        col = (int(a[0]*(1-f)+b[0]*f), int(a[1]*(1-f)+b[1]*f), int(a[2]*(1-f)+b[2]*f),255)
        pygame.draw.line(surf,col,(0,y),(W,y))
    # recorta em losango
    mask = pygame.Surface((W,H), pygame.SRCALPHA)
    pts = [(W//2,0),(W,H//2),(W//2,H),(0,H//2)]
    pygame.draw.polygon(mask,(255,255,255,255),pts)
    surf.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
    # detalhes simples por tipo
    if t=='water':
        for y in range(0,H,6):
            pygame.draw.line(surf,(200,220,255,60),(0,y),(W,y))
    if t=='shore':
        pygame.draw.polygon(surf,(255,255,255,60),pts,3)
    if t=='path':
        import math
        for i in range(-int(W*0.6), int(W*0.6), 12):
            x = W//2 + i; y = int(H*0.15 + (i+W*0.6)*0.3)
            pygame.draw.line(surf,(90,70,50,130),(x-8,y),(x+8,y),3)
    # labels
    if DEBUG_LABELS:
        try:
            font = pygame.font.SysFont('consolas,monospace', int(H*0.28))
        except:
            font = pygame.font.Font(None, int(H*0.28))
        txt = font.render((t[:8]).upper(), True, (0,0,0))
        surf.blit(txt, txt.get_rect(center=(W//2,H//2)))
    # downscale + alpha max
    out = pygame.transform.smoothscale(surf,(w,h))
    mask2 = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(mask2,(0,0,0,255),[(w//2,0),(w,h//2),(w//2,h),(0,h//2)])
    out.blit(mask2,(0,0),special_flags=pygame.BLEND_RGBA_MAX)
    return out


def build_tile(token:str)->pygame.Surface:
    return _build(token)
