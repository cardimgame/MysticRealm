# gameplay/game_scene.py — integrates camera, tilemap, player; shows missing assets overlay
import pygame
from core.config import SCREEN_SIZE, TILE_SIZE
from core.camera import Camera
from core.tilemap import TileSet, TileMap
from systems.mapgen import generate
from gameplay.player import Player
from core.asset import missing_assets

class GameScene:
    def __init__(self):
        self.w, self.h = SCREEN_SIZE
        self.camera = Camera(self.w, self.h)
        grid = generate(cols=64, rows=64)
        self.tileset = TileSet()
        self.tilemap = TileMap(grid, self.tileset)
        # start near lake/grass boundary
        self.player = Player(int(self.w*0.5), int(self.h*0.5))
        self.font = pygame.font.SysFont('consolas', 18)
    def handle(self, events):
        pass
    def update(self, dt):
        self.player.update(dt)
        self.camera.follow(self.player)
    def draw(self, screen):
        self.tilemap.draw(screen, self.camera)
        screen.blit(self.player.image, self.camera.world_to_screen(self.player.rect.topleft))
        # missing assets overlay
        miss = missing_assets()
        if miss:
            y = 8
            pane = pygame.Surface((self.w, 80), pygame.SRCALPHA)
            pane.fill((0,0,0,160))
            screen.blit(pane, (0,0))
            screen.blit(self.font.render('ATENÇÃO: assets ausentes (usando placeholders):', True, (255,220,160)), (12,y)); y+=22
            for p in miss[:2]:
                screen.blit(self.font.render('- '+p, True, (220,220,220)), (12,y)); y+=20
            if len(miss)>2:
                screen.blit(self.font.render(f'... +{len(miss)-2} arquivos', True, (200,200,200)), (12,y))
