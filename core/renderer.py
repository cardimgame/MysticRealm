# core/renderer.py
import pygame

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def clear(self, color=(16, 16, 24)):
        self.screen.fill(color)

    def draw_layers(self, *, ground=(), props=(), entities=(), fx=(), ui=()):
        for layer in (ground, props, entities, fx, ui):
            for item in layer:
                if callable(item):
                    item(self.screen)
                else:
                    surf, pos = item
                    self.screen.blit(surf, pos)
