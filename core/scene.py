
# core/scene.py — Cena base com draw corrigido para usar world_to_screen
import pygame
from .props import PropsManager

class Scene:
    def __init__(self, manager, screen_size=(1280,720)):
        self.manager = manager
        self.screen_width, self.screen_height = screen_size
        self.props_manager = PropsManager()
        self.player = None
        self.camera = None
        self.weather = None

    def on_resize(self, new_size):
        self.screen_width, self.screen_height = new_size

    def handle_events(self, events):
        pass

    def update(self, dt):
        if self.weather:
            try:
                self.weather.update(dt)
            except TypeError:
                self.weather.update()

    def draw(self, screen: pygame.Surface):
        if self.camera:
            self.props_manager.draw(screen, self.camera)
        if self.player and self.camera:
            # Converter coordenadas de mundo para a tela via câmera
            screen.blit(self.player.image,
                        self.camera.world_to_screen(self.player.rect.topleft))
        if self.weather:
            self.weather.draw(screen)
