# gameplay/player.py — crisp 128x128; uses existing asset if present
import pygame
from core.config import PLAYER_SIZE, PLAYER_SPEED
from core.asset import load_scaled

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Try preferred asset: assets/player/player_128.png; else scale player.png to 128; else crisp placeholder
        img = load_scaled('player/player_128.png', (PLAYER_SIZE, PLAYER_SIZE), smooth=False)
        if img is None:
            img = load_scaled('player/player.png', (PLAYER_SIZE, PLAYER_SIZE), smooth=False)
        if img is None:
            img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(img, (60,140,220), (16,32,PLAYER_SIZE-32,PLAYER_SIZE-48), border_radius=12)
            pygame.draw.circle(img, (230,210,180), (PLAYER_SIZE//2, 32), 24)
        self.image = img
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = float(PLAYER_SPEED)
        self.vel = pygame.Vector2(0,0)
    def handle_input(self):
        k=pygame.key.get_pressed()
        self.vel.update(0,0)
        if k[pygame.K_UP] or k[pygame.K_w]: self.vel.y = -1
        if k[pygame.K_DOWN] or k[pygame.K_s]: self.vel.y =  1
        if k[pygame.K_LEFT] or k[pygame.K_a]: self.vel.x = -1
        if k[pygame.K_RIGHT] or k[pygame.K_d]: self.vel.x =  1
        if self.vel.length_squared()>0: self.vel = self.vel.normalize()
    def update(self, dt):
        self.handle_input()
        self.rect.x += int(self.vel.x * self.speed * dt)
        self.rect.y += int(self.vel.y * self.speed * dt)
