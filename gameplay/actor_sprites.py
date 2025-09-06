from typing import Optional
# gameplay/actor_sprites.py — FINAL FIX: normalização de path no Windows (\ -> /)
import os
import pygame
from typing import Dict, List, Tuple, Optional
from core.asset import load_scaled
from core.config import PLAYER_SIZE

CLASS_COLORS = {
    'Guerreiro': ((90, 150, 200), (180, 60, 50)),
    'Arqueiro': ((90, 120, 60), (120, 180, 90)),
    'Arcanista': ((120, 90, 200), (50, 180, 220)),
    'Viajante': ((90, 120, 90), (120, 120, 120)),
    'Sombra': ((80, 80, 80), (200, 40, 40)),
    'Guardiã(o)': ((200, 200, 220), (200, 170, 60)),
}

SKIN_BY_RACE = {
    'Humano': (226, 200, 170),
    'Elfo': (210, 195, 160),
    'Anão': (198, 170, 140),
    'Orc': (130, 170, 120),
}

def _try_load_strip(base_dir: str, state: str, size: Tuple[int, int], max_frames=8) -> List[pygame.Surface]:
    frames: List[pygame.Surface] = []
    for i in range(max_frames):
        rel = os.path.join(base_dir, f"{state}_{i}.png")
        rel_norm = rel.replace('\\', '/')
        surf = load_scaled(rel_norm, size, smooth=True)
        if surf is not None:
            frames.append(surf)
        else:
            break
    return frames


def _make_placeholder_frame(step: int, size=(PLAYER_SIZE, PLAYER_SIZE),
                            body=(60, 140, 255), accent=(200, 180, 60), skin=(230, 210, 180)) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    shadow_w, shadow_h = int(w * 0.5), int(h * 0.18)
    sh = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 60), (0, 0, shadow_w, shadow_h))
    surf.blit(sh, (w // 2 - shadow_w // 2, h - shadow_h - 8))
    pygame.draw.rect(surf, body, (w // 2 - 20, h // 2 - 10, 40, 48), border_radius=10)
    head_off = 1 if (step % 2) == 0 else 0
    pygame.draw.circle(surf, skin, (w // 2, h // 2 - 22 - head_off), 12)
    cape_y = h // 2 - 2 + (step % 2)
    pygame.draw.polygon(surf, accent, [
        (w // 2 - 24, cape_y), (w // 2 + 24, cape_y), (w // 2 + 16, h - 18), (w // 2 - 16, h - 18)
    ])
    arm_off = 4 if (step % 2) == 0 else -4
    pygame.draw.rect(surf, (40, 40, 50), (w // 2 - 30, h // 2 - 6 + arm_off, 10, 26), border_radius=4)
    pygame.draw.rect(surf, (40, 40, 50), (w // 2 + 20, h // 2 - 6 - arm_off, 10, 26), border_radius=4)
    leg_off = 4 if (step % 2) == 0 else -2
    pygame.draw.rect(surf, (40, 40, 50), (w // 2 - 8, h // 2 + 26 + leg_off, 8, 14), border_radius=3)
    pygame.draw.rect(surf, (40, 40, 50), (w // 2 + 2, h // 2 + 26 - leg_off, 8, 14), border_radius=3)
    return surf


def _build_placeholder_anim(clazz: str, race: str, size=(PLAYER_SIZE, PLAYER_SIZE)) -> Dict[str, List[pygame.Surface]]:
    body, accent = CLASS_COLORS.get(clazz, ((60, 140, 255), (200, 180, 60)))
    skin = SKIN_BY_RACE.get(race, (230, 210, 180))
    walk = [_make_placeholder_frame(i, size, body, accent, skin) for i in range(4)]
    run = [_make_placeholder_frame(i, size, body, accent, skin) for i in range(4)]
    attack = []
    for i in range(4):
        f = _make_placeholder_frame(i, size, body, accent, skin)
        pygame.draw.rect(f, (200, 60, 60), (f.get_width() // 2 + 18, f.get_height() // 2 - 18, 12, 36), border_radius=5)
        attack.append(f)
    return {'idle': [walk[0]], 'walk': walk, 'run': run, 'attack': attack}


def build_actor_sprites(profile: Optional[dict], size=(PLAYER_SIZE, PLAYER_SIZE)) -> Dict[str, List[pygame.Surface]]:
    profile = profile or {}
    race = profile.get('race', 'Humano')
    gender = profile.get('gender', 'Masculino')
    clazz = profile.get('clazz', 'Guerreiro')
    base = f"actors/{race}/{gender}/{clazz}".replace('\\', '/')
    states = ['idle', 'walk', 'run', 'attack']
    anim: Dict[str, List[pygame.Surface]] = {}
    found_any = False
    for st in states:
        frames = _try_load_strip(base, st, size, max_frames=8)
        if frames:
            anim[st] = frames
            found_any = True
    if not found_any:
        return _build_placeholder_anim(clazz, race, size)
    if 'idle' not in anim:
        anim['idle'] = [anim.get('walk', [])[0] if anim.get('walk') else _build_placeholder_anim(clazz, race, size)['idle'][0]]
    if 'walk' not in anim:
        anim['walk'] = anim['idle']
    if 'run' not in anim:
        anim['run'] = anim['walk']
    if 'attack' not in anim:
        anim['attack'] = anim['walk']
    return anim
