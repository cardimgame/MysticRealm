# gameplay/player_sprites.py — placeholder animado por classe
import pygame

def _make_frame(color_body=(60,140,255), color_cape=(200,180,60), step=0, size=(32,48)):
    w,h = size
    surf = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(surf, color_body, (8,14,16,22), border_radius=4)
    pygame.draw.circle(surf, (230,210,180), (w//2, 10), 8)
    cape_y = 18 + (step%2)*1
    pygame.draw.polygon(surf, color_cape, [(6,cape_y),(w-6,cape_y),(w-10,h-6),(10,h-6)])
    leg_off = (step%2)*2
    pygame.draw.rect(surf, (40,40,50), (10, 36+leg_off, 4, 10))
    pygame.draw.rect(surf, (40,40,50), (18, 36+(2-leg_off), 4, 10))
    return surf

CLASS_COLORS = {
    'Guerreiro': ((90,150,200),(180,60,50)),
    'Mago': ((120,90,200),(50,180,220)),
    'Ladino': ((90,120,90),(120,120,120)),
    'Arqueiro': ((90,120,60),(120,180,90)),
    'Assassino': ((80,80,80),(200,40,40)),
    'Bardo': ((150,100,150),(220,180,80)),
    'Paladino': ((200,200,220),(200,170,60)),
}

def build_profile_sprites(profile: dict|None, size=(32,48)):
    clazz = (profile or {}).get('clazz', 'Guerreiro')
    body, cape = CLASS_COLORS.get(clazz, ((60,140,255),(200,180,60)))
    walk = [_make_frame(body, cape, step=i, size=size) for i in range(4)]
    idle = [walk[0]]
    return {'idle': idle, 'walk': walk}
