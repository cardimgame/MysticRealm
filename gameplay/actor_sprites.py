# gameplay/actor_sprites.py
from __future__ import annotations
import pygame, math, hashlib
from typing import Dict, List, Tuple, Optional

# Tamanho padrão do player (ajuste conforme seu jogo)
PLAYER_SIZE: Tuple[int,int] = (64, 96)

# Paletas por classe (aceita rótulos PT/EN; usa slug lower para casar melhor)
_CLASS_ACCENT = {
    'bravador': (190, 70, 70),    # melee pesado
    'sombra': (120, 120, 140),    # furtivo
    'arcanista': (90, 120, 200),  # magia
    'sentinela': (100, 180, 120), # arqueiro/estratégico
    'guardião': (200, 180, 100),
    'guardiao': (200, 180, 100),
    'ladrivante': (140, 100, 160),
    # EN (se vier do Excel em inglês no futuro)
    'warrior': (190, 70, 70),
    'shade': (120, 120, 140),
    'arcanist': (90, 120, 200),
    'sentinel': (100, 180, 120),
    'guardian': (200, 180, 100),
    'rogue': (140, 100, 160),
}

# Cálculo de cor base pela raça para variar um pouco entre perfis
_DEF_BODIES = [(88, 98, 122), (96, 108, 134), (102, 112, 128), (92, 102, 120)]


def _slug(s: str) -> str:
    return (s or '').strip().lower()


def _race_body_color(race_label: str) -> Tuple[int,int,int]:
    if not race_label:
        return _DEF_BODIES[0]
    h = hashlib.md5(race_label.encode('utf-8')).digest()[0]
    return _DEF_BODIES[h % len(_DEF_BODIES)]


def _class_accent(clazz_label: str) -> Tuple[int,int,int]:
    c = _CLASS_ACCENT.get(_slug(clazz_label))
    if c:
        return c
    # fallback baseado no hash
    h = hashlib.md5((clazz_label or '').encode('utf-8')).digest()[1]
    return (120 + h % 80, 90 + (h//3) % 80, 90 + (h//5) % 80)


def _make_frame(size: Tuple[int,int], phase: float, body: Tuple[int,int,int], accent: Tuple[int,int,int]) -> pygame.Surface:
    """Desenha um busto humanoide estilizado com pequenas variações por fase.
    phase: 0..1 (usado para idle/walk/run)
    """
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # sombra no chão (elipse)
    sh_w = int(w*0.55)
    sh_h = int(h*0.08)
    pygame.draw.ellipse(surf, (0,0,0,80), (w//2 - sh_w//2, h - sh_h - 2, sh_w, sh_h))

    # corpo
    # leve oscilação vertical
    oscill = int(math.sin(phase*2*math.pi) * (h*0.01))

    torso_w = int(w*0.36)
    torso_h = int(h*0.38)
    torso_r = 10
    torso_rect = pygame.Rect(0,0,torso_w,torso_h)
    torso_rect.center = (w//2, int(h*0.60) + oscill)
    pygame.draw.rect(surf, body, torso_rect, border_radius=torso_r)

    # cabeça
    head_r = int(min(w,h) * 0.17)
    head_c = (w//2, int(h*0.36) + oscill)
    pygame.draw.circle(surf, tuple(min(255, c+14) for c in body), head_c, head_r)

    # ombreiras/acento
    pad_w = int(w*0.22)
    pad_h = int(h*0.10)
    pad_r = 8
    left = pygame.Rect(0,0,pad_w,pad_h); left.center = (w//2 - torso_w//2 + pad_w//2, torso_rect.top + pad_h//2)
    right= pygame.Rect(0,0,pad_w,pad_h); right.center= (w//2 + torso_w//2 - pad_w//2, torso_rect.top + pad_h//2)
    pygame.draw.rect(surf, accent, left, border_radius=pad_r)
    pygame.draw.rect(surf, accent, right, border_radius=pad_r)

    # cinto acento
    belt = pygame.Rect(torso_rect.left+4, torso_rect.centery-4, torso_rect.width-8, 8)
    pygame.draw.rect(surf, tuple(max(0, c-10) for c in accent), belt, border_radius=6)

    return surf


def _make_anim(size: Tuple[int,int], frames: int, speed: float, body: Tuple[int,int,int], accent: Tuple[int,int,int]) -> List[pygame.Surface]:
    """Gera uma animação simples variando o phase."""
    anim = []
    for i in range(frames):
        phase = (i / max(1, frames-1)) * speed
        anim.append(_make_frame(size, phase, body, accent))
    return anim


def build_actor_sprites(profile: Dict, size: Tuple[int,int] = PLAYER_SIZE, anim_frames: int = 8) -> Dict[str, List[pygame.Surface]]:
    """
    Gera um dicionário com animações do ator a partir do profile do criador V2.
    Retorna chaves comuns: 'idle', 'walk', 'run', 'attack'.

    profile esperado (exemplo):
    {
      'name': '...', 'gender': 'Masculino',
      'race': 'Planicius', 'clazz': 'Sombra', 'sign': 'Vulkhar',
      'skills': ['Arco','Furtividade'], 'stats': {...}
    }
    """
    race_label = profile.get('race', '')
    clazz_label = profile.get('clazz', '')
    body = _race_body_color(race_label)
    accent = _class_accent(clazz_label)

    idle = _make_anim(size, anim_frames, speed=0.6, body=body, accent=accent)
    walk = _make_anim(size, anim_frames, speed=1.2, body=body, accent=accent)
    run  = _make_anim(size, anim_frames, speed=1.8, body=body, accent=accent)
    # ataque: usa as mesmas bases mas com um "flash" de acento no frame central
    attack = []
    mid = anim_frames//2
    for i in range(anim_frames):
        frame = _make_frame(size, i/anim_frames, body, accent)
        if i == mid:
            glow = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(glow, (*accent, 80), (size[0]//2, int(size[1]*0.45)), int(min(size)*0.20))
            frame.blit(glow, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)
        attack.append(frame)

    return {
        'idle': idle,
        'walk': walk,
        'run': run,
        'attack': attack,
    }
