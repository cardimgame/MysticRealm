import pygame, random
from systems.iso_math import grid_to_screen
from core.config import TILE_W, TILE_H, PLAYER_SIZE
from gameplay.actor_sprites import build_actor_sprites

class EnemyIso(pygame.sprite.Sprite):
    def __init__(self, r, c, color=(170,80,60)):
        super().__init__()
        self.r = float(r)
        self.c = float(c)
        profile = {'race': 'Humano', 'gender': 'Masculino', 'clazz': 'Sombra'}
        self.anim = build_actor_sprites(profile, size=(PLAYER_SIZE, PLAYER_SIZE))
        self.state = 'idle'; self.anim_t = 0.0; self.anim_idx = 0
        self.image = self.anim['idle'][0]
        self.rect = self.image.get_rect()
        self.speed_tiles = 2.0
        self.vel_r = 0.0
        self.vel_c = 0.0
        self.heading = pygame.Vector2(1, 0)

    def update_rect(self, ox, oy):
        x, y = grid_to_screen(self.r, self.c)
        x += ox; y += oy
        self.rect.midbottom = (x + TILE_W//2, y + TILE_H)

    def _screen_vec_from_iso(self, dr, dc):
        dx = (dc - dr); dy = (dc + dr)
        v = pygame.Vector2(dx, dy)
        if v.length_squared() > 0: v = v.normalize()
        return v

    def update_ai(self, dt, target_rc):
        tr, tc = target_rc
        dr = tr - self.r
        dc = tc - self.c
        d2 = dr*dr + dc*dc
        if d2 > 900:
            if random.random() < 0.01:
                self.vel_r = random.uniform(-0.3, 0.3)
                self.vel_c = random.uniform(-0.3, 0.3)
            self.r += self.vel_r * dt
            self.c += self.vel_c * dt
            self.state = 'walk' if (self.vel_r or self.vel_c) else 'idle'
            return
        to_player = self._screen_vec_from_iso(dr, dc)
        if (self.vel_r or self.vel_c):
            self.heading = self._screen_vec_from_iso(self.vel_r, self.vel_c)
        dot = self.heading.dot(to_player)
        COS_HALF_FOV = 0.5
        if dot >= COS_HALF_FOV:
            dist = (d2) ** 0.5
            if dist > 0.001:
                self.vel_r = (dr / dist) * self.speed_tiles
                self.vel_c = (dc / dist) * self.speed_tiles
            self.state = 'run'
        else:
            if random.random() < 0.02:
                self.vel_r = random.uniform(-0.2, 0.2)
                self.vel_c = random.uniform(-0.2, 0.2)
            self.state = 'walk' if (self.vel_r or self.vel_c) else 'idle'
        self.r += self.vel_r * dt
        self.c += self.vel_c * dt
        fps = 12 if self.state == 'run' else (8 if self.state == 'walk' else 6)
        self.anim_t += dt
        if self.anim_t >= 1.0 / fps:
            self.anim_t -= 1.0 / fps
            frames = self.anim.get(self.state, self.anim['idle'])
            self.anim_idx = (self.anim_idx + 1) % len(frames)
            self.image = frames[self.anim_idx]

class EnemiesIso:
    def __init__(self, *, tilemap, pois: dict | None, rng_seed=2025):
        self.tilemap = tilemap
        self.pois = pois or {}
        self.group = pygame.sprite.Group()
        self.rng = random.Random(rng_seed)
        self._spawn_from_pois()

    def _spawn_from_pois(self):
        if 'cave_entrances' in self.pois:
            for (r,c) in self.pois['cave_entrances']:
                for _ in range(2):
                    rr = r + self.rng.randint(-3,3)
                    cc = c + self.rng.randint(-3,3)
                    self.group.add(EnemyIso(rr, cc, color=(170,80,60)))
        if 'mountain_bbox' in self.pois:
            top,left,h,w = self.pois['mountain_bbox']
            for _ in range(4):
                rr = top + self.rng.randint(0, max(1,h-1))
                cc = left + self.rng.randint(0, max(1,w-1))
                self.group.add(EnemyIso(rr, cc, color=(100,60,140)))

    def update(self, dt, player_rc, ox, oy):
        for e in self.group.sprites():
            e.update_ai(dt, player_rc)
            e.update_rect(ox, oy)
