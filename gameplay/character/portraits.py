# gameplay/character/portraits.py
from __future__ import annotations
import pygame
from typing import Tuple
from core.asset import load_image_strict

# Cache simples por (race|gender|WxH)
_CACHE: dict[str, pygame.Surface] = {}

def _key(race_key: str, gender: str, size: Tuple[int,int]) -> str:
    return f"{race_key}|{gender}|{size[0]}x{size[1]}"

def _normalize_gender(g: str) -> str:
    g = (g or '').strip().lower()
    if g.startswith('f'): return 'feminino'
    return 'masculino'

# --- Placeholder estilizado (sem import recursivo) ---

def _accent_from_stats(race_key: str) -> Tuple[int,int,int,int]:
    """Escolhe um tom sutil baseado no atributo dominante da raça."""
    try:
        from gameplay.character import schema
        r = schema.race_info(race_key)
        STR,DEX,INT,CON = r.attrs.get('STR',0), r.attrs.get('DEX',0), r.attrs.get('INT',0), r.attrs.get('CON',0)
        dom = max([('STR',STR),('DEX',DEX),('INT',INT),('CON',CON)], key=lambda x: x[1])[0]
        if dom == 'STR': base = (179, 90, 90)
        elif dom == 'DEX': base = (79, 122, 90)
        elif dom == 'INT': base = (81, 108, 153)
        else: base = (122, 106, 79)
        return (*base, 28)  # alpha baixo
    except Exception:
        return (0,0,0,0)

def _make_placeholder(size: Tuple[int,int], race_key: str = '', gender: str = '') -> pygame.Surface:
    W, H = size
    surf = pygame.Surface((W,H), pygame.SRCALPHA)
    # Fundo: gradiente radial escuro
    bg = pygame.Surface((W,H), pygame.SRCALPHA)
    cx, cy = W//2, H//2
    maxr = int(((W*W + H*H) ** 0.5) // 2)
    for r in range(maxr, 0, -4):
        a = min(220, int(60 + (maxr - r) * 0.20))
        col = (26, 34, 48, a)
        pygame.draw.circle(bg, col, (cx, cy), r)
    surf.blit(bg, (0,0))

    # Véu cromático sutil
    acc = _accent_from_stats(race_key)
    if acc[3] > 0:
        veil = pygame.Surface((W,H), pygame.SRCALPHA)
        veil.fill(acc)
        surf.blit(veil, (0,0), special_flags=pygame.BLEND_RGBA_ADD)

    # Silhueta / busto
    head_r = int(min(W,H) * 0.18)
    body_w = int(min(W,H) * 0.42)
    body_h = int(min(W,H) * 0.30)

    cx, cy = W//2, int(H*0.56)
    body = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
    pygame.draw.rect(body, (168,178,192), (0,0, body_w, body_h), border_radius=14)
    body_rect = body.get_rect(center=(cx, cy+6))
    surf.blit(body, body_rect)
    pygame.draw.circle(surf, (186,196,210), (cx, cy - head_r - 18), head_r)

    # Rim light frio
    rim = pygame.Surface((W,H), pygame.SRCALPHA)
    pygame.draw.circle(rim, (168,192,255,110), (cx, cy - head_r - 18), head_r+2, 3)
    pygame.draw.rect(rim, (168,192,255,90), (body_rect.x-2, body_rect.y-2, body_rect.w+4, body_rect.h+4), 3, border_radius=16)
    surf.blit(rim, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # Moldura / sombra interna
    pygame.draw.rect(surf, (74,94,120), surf.get_rect(), 2, border_radius=10)
    inner = pygame.Surface((W-8, H-8), pygame.SRCALPHA)
    pygame.draw.rect(inner, (0,0,0,36), inner.get_rect(), 0, border_radius=8)
    surf.blit(inner, (4,4))
    return surf

# --- Loader principal ---

def get_portrait(race_key: str, gender_label: str, max_size: Tuple[int,int]) -> pygame.Surface:
    """
    Retorna um Surface **EXATAMENTE** do tamanho max_size, com o retrato "fit" dentro.
    Se não houver asset, gera placeholder estilizado.
    Arquivo esperado: assets/player/{race_slug}_{genero}.png
    Ex.: assets/player/planicius_masculino.png
    """
    W, H = max_size
    gslug = _normalize_gender(gender_label)
    rslug = (race_key or '').lower()
    rel = f"player/{rslug}_{gslug}.png"
    cache_k = _key(rslug, gslug, max_size)
    if cache_k in _CACHE:
        return _CACHE[cache_k]

    # container final com moldura, sempre W x H
    container = pygame.Surface((W, H), pygame.SRCALPHA)
    frame_rect = container.get_rect()

    img = load_image_strict(rel)
    if img is None:
        ph = _make_placeholder((W, H), race_key, gender_label)
        container.blit(ph, (0,0))
        _CACHE[cache_k] = container
        return container

    iw, ih = img.get_size()
    # Fit com pequeno padding para não colar na borda
    pad = 10
    inner_w, inner_h = max(1, W - pad*2), max(1, H - pad*2)
    scale = min(inner_w / iw, inner_h / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    if (new_w, new_h) != (iw, ih):
        img = pygame.transform.smoothscale(img, (new_w, new_h))
    rect = img.get_rect(center=frame_rect.center)
    container.blit(img, rect)

    # Moldura
    pygame.draw.rect(container, (74,94,120), frame_rect, 2, border_radius=8)

    _CACHE[cache_k] = container
    return container
