# systems/tile_factory.py — FULL PLACEHOLDERS + DEBUG ICONS
"""
Placeholders isométricos (2:1) com supersampling 2× e ícones de debug.
Cobre TODOS os tokens de ground/overlay + dbg_*. Sem dependência de assets.
"""
import pygame, random, math
from functools import lru_cache
from core.config import TILE_W, TILE_H

# ---------- utils ----------
def _rhombus_points(w, h):
    return [(w//2, 0), (w, h//2), (w//2, h), (0, h//2)]

def _clamp(x, a=0, b=255): return max(a, min(b, int(x)))

def _rand(seed): return random.Random(seed)

# ---------- painters ----------
def _line_gradient(surf, pts, col_a, col_b):
    w, h = surf.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255,255,255,255), pts)
    temp = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h-1)
        r = int(col_a[0]*(1-t) + col_b[0]*t)
        g = int(col_a[1]*(1-t) + col_b[1]*t)
        b = int(col_a[2]*(1-t) + col_b[2]*t)
        pygame.draw.line(temp, (r,g,b,255), (0,y), (w,y))
    temp.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(temp, (0,0))

def _noise_specks(surf, pts, color=(255,255,255), density=0.012, alpha=28, seed=0):
    w,h = surf.get_size(); rnd = _rand(seed); n = int(w*h*density)
    for _ in range(n):
        x = rnd.randrange(0, w); y = rnd.randrange(0, h)
        if (abs(x - w/2)/(w/2 + 1e-5) + abs(y - h/2)/(h/2 + 1e-5)) <= 1.0:
            a = rnd.randint(max(8, alpha-10), alpha)
            surf.set_at((x,y), (*color, a))

def _edge_lines(surf, pts, col_light, col_dark):
    pygame.draw.lines(surf, col_dark, True, pts, 2)
    pygame.draw.line(surf, col_light, pts[0], pts[1], 2)
    pygame.draw.line(surf, col_light, pts[1], pts[2], 1)

def _foam_rim(surf, pts, color=(240,240,255), seed=0):
    w,h = surf.get_size(); rnd = _rand(seed)
    rim = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(rim, (*color, 0), pts)
    p = list(pts)
    for t in range(60, 140, 6):
        a = max(12, 200 - (t-60)*2)
        c = (_clamp(color[0]+rnd.randint(-6,6)), _clamp(color[1]+rnd.randint(-6,6)), _clamp(color[2]+rnd.randint(-6,6)), a)
        pygame.draw.polygon(rim, c, p, 1)
        p = [(x + rnd.randint(-1,1), y + rnd.randint(-1,1)) for (x,y) in p]
    surf.blit(rim, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

def _diagonal_band(surf, pts, color=(150,110,80), width_frac=0.58, alpha=230):
    w,h = surf.get_size(); band = pygame.Surface((w,h), pygame.SRCALPHA)
    cx, cy = w//2, h//2; hw = int((w*width_frac)//2)
    poly = [(cx-hw, 0), (w, cy-hw//2), (cx+hw, h), (0, cy+hw//2)]
    pygame.draw.polygon(band, (*color, alpha), poly)
    _noise_specks(band, None, color=(20,15,10), density=0.004, alpha=40, seed=1234)
    surf.blit(band, (0,0), special_flags=pygame.BLEND_RGBA_MIN)

def _snow_patch(surf, pts, color=(235,238,245)):
    w,h = surf.get_size(); snow = pygame.Surface((w,h), pygame.SRCALPHA)
    rect = pygame.Rect(0,0,int(w*0.82), int(h*0.72)); rect.center = (w//2, h//2)
    pygame.draw.ellipse(snow, (*color, 140), rect)
    for i in range(1,5): pygame.draw.ellipse(snow, (220,230,255, 90 - i*16), rect.inflate(i*2, i))
    surf.blit(snow, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

def _cracks(surf, pts, color=(40,80,120), n=3, seed=0):
    w,h = surf.get_size(); rnd = _rand(seed)
    for _ in range(n):
        x = rnd.randint(int(w*0.15), int(w*0.85))
        y = rnd.randint(int(h*0.15), int(h*0.85))
        ang = rnd.uniform(-math.pi/3, math.pi/3); ln = rnd.randint(int(w*0.35), int(w*0.65))
        dx = int(math.cos(ang)*ln); dy = int(math.sin(ang)*ln*0.6)
        pygame.draw.line(surf, (*color, 200), (x,y), (x+dx, y+dy), 2)

# ---------- render principal ----------
@lru_cache(maxsize=512)
def _render_token(token: str) -> pygame.Surface:
    w, h = TILE_W, TILE_H
    W, H = w*2, h*2
    surf = pygame.Surface((W,H), pygame.SRCALPHA)
    pts = _rhombus_points(W,H)

    t = (token or '').strip().lower()
    # --- ground ---
    if t == 'grass':
        _line_gradient(surf, pts, (66,128,66), (36,84,44)); _noise_specks(surf, pts, (90,150,90), 0.006, 28, 1)
        _edge_lines(surf, pts, (130,200,130), (18,28,18))
    elif t == 'sand':
        _line_gradient(surf, pts, (205,180,110), (170,140,90)); _noise_specks(surf, pts, (220,200,150), 0.006, 28, 2)
        _edge_lines(surf, pts, (230,210,150), (100,80,50))
    elif t == 'water':
        _line_gradient(surf, pts, (34,82,140), (10,36,88))
        spec = pygame.Surface((W,H), pygame.SRCALPHA)
        for y in range(H):
            a = int(80 * max(0.0, math.sin((y/H)*math.pi)))
            pygame.draw.line(spec, (200,220,255,a), (0,y), (W,y))
        spec.blit(surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(spec, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)
        _edge_lines(surf, pts, (180,200,230), (18,26,60))
    # --- overlays ---
    elif t == 'path':
        _diagonal_band(surf, pts, (140,110,85), 0.58, 220)
    elif t == 'shore':
        _foam_rim(surf, pts, (245,246,255), 7)
    elif t == 'snow_patch':
        _snow_patch(surf, pts, (235,240,252))
    elif t == 'grass_detail':
        for i in range(8):
            col = (120,180,120, 160); x = int(W*0.2) + i*int(W*0.08)
            pygame.draw.line(surf, col, (x, int(H*0.55)), (x-6, int(H*0.40)), 2)
    elif t == 'rock_crack':
        _cracks(surf, pts, (60,60,72), 2, 11)
    elif t == 'ice_crack':
        _cracks(surf, pts, (70,130,170), 3, 12)
    # --- debug icons ---
    elif t == 'dbg_city':
        _line_gradient(surf, pts, (60,60,68), (32,32,40))
        pygame.draw.polygon(surf, (255,210,100,240), [(W//2, int(H*0.18)), (int(W*0.82), H//2), (W//2, int(H*0.82)), (int(W*0.18), H//2)])
        pygame.draw.circle(surf, (255,250,200,255), (W//2, H//2), int(min(W,H)*0.10))
    elif t == 'dbg_village':
        _line_gradient(surf, pts, (60,68,60), (28,40,28))
        pygame.draw.circle(surf, (120,230,120,240), (W//2, H//2), int(min(W,H)*0.18))
    elif t == 'dbg_cave':
        _line_gradient(surf, pts, (40,50,70), (20,26,44))
        pygame.draw.ellipse(surf, (100,180,255,220), (int(W*0.28), int(H*0.38), int(W*0.44), int(H*0.28)))
    elif t == 'dbg_dungeon':
        _line_gradient(surf, pts, (66,50,86), (34,24,56))
        pygame.draw.rect(surf, (190,140,240,220), (int(W*0.28), int(H*0.32), int(W*0.44), int(H*0.36)), border_radius=10)
    else:
        # fallback neutro
        _line_gradient(surf, pts, (80,80,90), (40,40,48)); _edge_lines(surf, pts, (160,160,170), (20,20,24))

    # Clip final 2x e alpha fix no reduzido (evita halo entre tiles)
    mask2x = pygame.Surface((W,H), pygame.SRCALPHA)
    pygame.draw.polygon(mask2x, (255,255,255,255), pts)
    surf.blit(mask2x, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    out = pygame.transform.smoothscale(surf, (w,h))
    pts_small = _rhombus_points(w,h)
    alpha_fix = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(alpha_fix, (0,0,0,255), pts_small)
    out.blit(alpha_fix, (0,0), special_flags=pygame.BLEND_RGBA_MAX)
    return out

# API pública
def build_tile(token: str) -> pygame.Surface:
    token = (token or '').strip()
    return _render_token(token)
