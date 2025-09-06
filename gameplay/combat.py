# gameplay/combat.py — shared combat helpers (player & enemy)
import pygame
from dataclasses import dataclass

STRIKE_FRAME_INDEX = 1  # attack frame that emits damage (0-based)

@dataclass
class Health:
    hp: int = 20
    hp_max: int = 20

    def take(self, dmg: int) -> int:
        dmg = int(max(0, dmg))
        self.hp = max(0, self.hp - dmg)
        return dmg

    @property
    def alive(self) -> bool:
        return self.hp > 0


def compute_facing_from_iso_vel(vel_r: float, vel_c: float) -> pygame.Vector2:
    """Converts iso grid (r,c) velocity to screen-space facing (dx,dy).
    r decreases up-left, increases down-right; c decreases up-right, increases down-left.
    We'll map to approximate screen pixel directions.
    """
    # Convert grid velocity into approximate screen delta in pixels (not scaled by tile size here)
    dx = (vel_c - vel_r) * 1.0
    dy = (vel_c + vel_r) * 1.0
    v = pygame.Vector2(dx, dy)
    if v.length_squared() == 0:
        return pygame.Vector2(1, 0)  # default facing right-ish
    v = v.normalize()
    return v


def make_melee_hitbox(attacker_rect: pygame.Rect, facing: pygame.Vector2,
                       reach_px: int = 56, width_px: int = 50) -> pygame.Rect:
    """Simple axis-aligned rectangle projected in the facing direction from attacker's rect.
    Facing is a normalized screen-space vector.
    """
    fx, fy = facing.x, facing.y
    # Project point from attacker center
    cx, cy = attacker_rect.center
    hx = int(cx + fx * reach_px)
    hy = int(cy + fy * reach_px)
    # Build a box centered at (hx,hy)
    w = width_px
    h = int(width_px * 0.8)
    return pygame.Rect(hx - w//2, hy - h//2, w, h)


def draw_hitbox_debug(screen: pygame.Surface, rect: pygame.Rect, color=(255,80,80)):
    if rect is None:
        return
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*color, 60))
    screen.blit(s, (rect.x, rect.y))
    pygame.draw.rect(screen, (*color, 220), rect, 2)
