
import pygame, random
from systems.iso_math import grid_to_screen
from core.config import TILE_W, TILE_H

class EnemyIso(pygame.sprite.Sprite):
    def __init__(self, r, c, color=(170,80,60)):
        super().__init__()
        self.r = float(r)
        self.c = float(c)
        self.image = pygame.Surface((TILE_W, TILE_H*2), pygame.SRCALPHA)
        # Simple placeholder humanoid
        body = pygame.Surface((24, 36), pygame.SRCALPHA)
        body.fill((*color, 255))
        self.image.blit(body, (TILE_W//2 - 12, TILE_H))
        self.rect = self.image.get_rect()
        self.speed_tiles = 2.4  # tiles per second
        self.vel_r = 0.0
        self.vel_c = 0.0

    def update_rect(self, ox, oy):
        x, y = grid_to_screen(self.r, self.c)
        x += ox; y += oy
        self.rect.midbottom = (x + TILE_W//2, y + TILE_H)

    def update_ai(self, dt, target_rc):
        tr, tc = target_rc
        dr = tr - self.r
        dc = tc - self.c
        d2 = dr*dr + dc*dc
        if d2 < 900:  # within 30 tiles radius
            import math
            d = math.sqrt(d2)
            if d > 0.001:
                self.vel_r = (dr/d) * self.speed_tiles
                self.vel_c = (dc/d) * self.speed_tiles
            else:
                self.vel_r = self.vel_c = 0.0
        else:
            # idle wander
            if random.random() < 0.01:
                self.vel_r = random.uniform(-0.3, 0.3)
                self.vel_c = random.uniform(-0.3, 0.3)
        self.r += self.vel_r * dt
        self.c += self.vel_c * dt

class EnemiesIso:
    def __init__(self, *, tilemap, pois: dict | None, rng_seed=2025):
        self.tilemap = tilemap
        self.pois = pois or {}
        self.group = pygame.sprite.Group()
        self.rng = random.Random(rng_seed)
        self._spawn_from_pois()

    def _spawn_from_pois(self):
        # Spawn near caves and mountain
        if 'cave_entrances' in self.pois:
            for (r,c) in self.pois['cave_entrances']:
                for i in range(2):
                    rr = r + self.rng.randint(-3,3)
                    cc = c + self.rng.randint(-3,3)
                    self.group.add(EnemyIso(rr, cc, color=(170,80,60)))
        if 'mountain_bbox' in self.pois:
            top,left,h,w = self.pois['mountain_bbox']
            for i in range(4):
                rr = top + self.rng.randint(0, max(1,h-1))
                cc = left + self.rng.randint(0, max(1,w-1))
                self.group.add(EnemyIso(rr, cc, color=(100,60,140)))

    def update(self, dt, player_rc, ox, oy):
        for e in self.group.sprites():
            e.update_ai(dt, player_rc)
            e.update_rect(ox, oy)

    def draw_sorted(self, screen, camera):
        # sort by rect.bottom for pseudo-Z
        sprites = sorted(self.group.sprites(), key=lambda s: s.rect.bottom)
        for s in sprites:
            screen.blit(s.image, camera.world_to_screen(s.rect.topleft))
