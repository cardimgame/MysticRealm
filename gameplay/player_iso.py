
# gameplay/player_iso.py — cardinais puros + flag de input tratado
import pygame
from core.config import PLAYER_SIZE, TILE_W, TILE_H, PLAYER_SPEED_TILES
from systems.iso_math import grid_to_screen
from gameplay.actor_sprites import build_actor_sprites
from gameplay.combat import Health, compute_facing_from_iso_vel, make_melee_hitbox, STRIKE_FRAME_INDEX

ANIM_FPS_WALK = 8
ANIM_FPS_RUN = 12
ATTACK_COOL = 0.35

MAP_OFFSET_X = 0
MAP_OFFSET_Y = 0

def set_map_offset(x: int, y: int):
    global MAP_OFFSET_X, MAP_OFFSET_Y
    MAP_OFFSET_X = int(x)
    MAP_OFFSET_Y = int(y)

class Player(pygame.sprite.Sprite):
    def __init__(self, start_r: int, start_c: int, profile: dict | None = None):
        super().__init__()
        self.r = float(start_r)
        self.c = float(start_c)
        self.base_speed = PLAYER_SPEED_TILES
        self.vel_r = 0.0
        self.vel_c = 0.0
        self.anim = build_actor_sprites(profile, size=(PLAYER_SIZE, PLAYER_SIZE))
        self.state = "idle"
        self.anim_t = 0.0
        self.anim_idx = 0
        self.attack_t = 0.0
        self.image = self.anim["idle"][0]
        self.rect = self.image.get_rect()
        self.update_rect()
        # Combat
        self.health = Health(hp=24, hp_max=24)
        self.damage = 6
        self.last_hitbox: pygame.Rect | None = None
        self.facing = pygame.Vector2(1, 0)

    def update_rect(self):
        sx, sy = grid_to_screen(self.r, self.c)
        sx += MAP_OFFSET_X
        sy += MAP_OFFSET_Y
        self.rect.midbottom = (sx + TILE_W // 2, sy + TILE_H)

    def _set_state(self, st: str):
        if st != self.state:
            self.state = st
            self.anim_t = 0.0
            self.anim_idx = 0

    def handle_input(self, dt: float, *, cardinais_puros: bool = False, screen_dir: int = 1):
        keys = pygame.key.get_pressed()
        dr = dc = 0.0
        if not cardinais_puros:
            # ISO clássico: teclas seguem eixos do grid isométrico
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dr += -1; dc += -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dr +=  1; dc +=  1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dr +=  1; dc += -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dr += -1; dc +=  1
        else:
            # Cardinais puros: intenção em TELA -> converter para (dr,dc)
            dx = dy = 0.0
            if keys[pygame.K_UP] or keys[pygame.K_w]:    dy -= 1.0
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dy += 1.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:  dx -= 1.0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1.0
            dx *= int(screen_dir)  # compensa flip horizontal do render
            mag = (dx*dx + dy*dy) ** 0.5
            if mag > 0:
                dx /= mag; dy /= mag
                hw = (TILE_W / 2.0)
                hh = (TILE_H / 2.0)
                dr = 0.5 * ((dy / hh) - (dx / hw))
                dc = 0.5 * ((dy / hh) + (dx / hw))

        speed = self.base_speed * (1.6 if keys[pygame.K_LSHIFT] else 1.0)
        if dr != 0.0 or dc != 0.0:
            mag = (dr*dr + dc*dc) ** 0.5
            dr /= mag; dc /= mag
            self.vel_r = dr * speed
            self.vel_c = dc * speed
            self._set_state("run" if keys[pygame.K_LSHIFT] else "walk")
        else:
            self.vel_r = self.vel_c = 0.0
            if self.attack_t <= 0:
                self._set_state("idle")

        # Attack
        if keys[pygame.K_j] and self.attack_t <= 0.0:
            self.attack_t = ATTACK_COOL
            self._set_state("attack")

    def take_damage(self, dmg: int):
        self.health.take(dmg)
        # TODO: feedback/flash de dano

    def update(self, dt: float, *, input_already_handled: bool = False):
        if not input_already_handled:
            # Mantém compatibilidade: se ninguém tratou input, tratamos aqui
            self.handle_input(dt)

        # Integra posição no grid
        self.r += self.vel_r * dt
        self.c += self.vel_c * dt
        self.update_rect()

        # Facing a partir da velocidade (fallback mantém última direção)
        v = compute_facing_from_iso_vel(self.vel_r, self.vel_c)
        if v.length_squared() > 0:
            self.facing = v

        # Reset do hitbox emitido
        self.last_hitbox = None

        # Animação & emissão de hitbox no ataque
        if self.state == "attack":
            self.attack_t -= dt
            fps = 12
            self.anim_t += dt
            if self.anim_t >= 1.0 / fps:
                self.anim_t -= 1.0 / fps
                self.anim_idx = min(self.anim_idx + 1, len(self.anim["attack"]) - 1)
            if self.anim_idx == STRIKE_FRAME_INDEX:
                self.last_hitbox = make_melee_hitbox(self.rect, self.facing, reach_px=70, width_px=56)
            if self.attack_t <= 0.0 and self.anim_idx >= len(self.anim["attack"]) - 1:
                self._set_state("walk" if (self.vel_r or self.vel_c) else "idle")
        else:
            fps = ANIM_FPS_RUN if self.state == "run" else (ANIM_FPS_WALK if self.state == "walk" else 6)
            frames = self.anim[self.state]
            self.anim_t += dt
            if self.anim_t >= 1.0 / fps:
                self.anim_t -= 1.0 / fps
                self.anim_idx = (self.anim_idx + 1) % len(frames)
            self.image = self.anim[self.state][self.anim_idx]
