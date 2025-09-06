# core/input.py
import pygame

KEYMAP = {
    "up":    (pygame.K_w, pygame.K_UP),
    "down":  (pygame.K_s, pygame.K_DOWN),
    "left":  (pygame.K_a, pygame.K_LEFT),
    "right": (pygame.K_d, pygame.K_RIGHT),
    "confirm": (pygame.K_RETURN, pygame.K_SPACE),
    "back":  (pygame.K_ESCAPE,),
}

def actions_from_events(events):
    actions = set()
    for e in events:
        if e.type == pygame.KEYDOWN:
            for action, keys in KEYMAP.items():
                if e.key in keys:
                    actions.add(action)
    return actions

def axes_from_pressed():
    pressed = pygame.key.get_pressed()
    x = (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) - (pressed[pygame.K_a] or pressed[pygame.K_LEFT])
    y = (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) - (pressed[pygame.K_w] or pressed[pygame.K_UP])
    return x, y
