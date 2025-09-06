# systems/enemy_ai.py — inimigo humanoide simples
import pygame, random
from systems.stats import build_stats, RACES, CLASSES
from systems.combat import Fighter

COLORS = {
    'Guerreiro': (170,80,60), 'Arcanista': (100,80,160), 'Viajante':(70,140,120),
    'Arqueiro':(60,140,60), 'Sombra':(80,80,80), 'Trovador':(160,120,80), 'Guardião':(140,120,80)
}

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        race = random.choice(list(RACES.keys()))
        clazz = random.choice(list(CLASSES.keys()))
        self.gender = random.choice(['Masculino','Feminino','Não-binário'])
        self.race = race; self.clazz = clazz
        stats = build_stats(race, clazz)
        self.fighter = Fighter(stats)
        self.image = pygame.Surface((32,48), pygame.SRCALPHA)
        self.image.fill((*COLORS.get(clazz,(120,120,120)), 255))
        pygame.draw.rect(self.image, (0,0,0), (0,0,32,48), 1)
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 80
    def update(self, dt, player_pos, collidables):
        self.fighter.update(dt)
        # perseguir player
        px, py = player_pos
        dx = px - self.rect.centerx; dy = py - self.rect.centery
        dist2 = dx*dx + dy*dy
        if dist2 < 400**2:
            import math
            d = math.hypot(dx,dy)
            if d>1:
                vx, vy = dx/d, dy/d
                self.rect.x += int(vx*self.speed*dt)
                self.rect.y += int(vy*self.speed*dt)
