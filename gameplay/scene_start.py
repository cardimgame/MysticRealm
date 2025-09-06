# gameplay/scene_start.py — Start usa start_screen.png (FIT), sem dragons
import pygame
from core.asset import load_image_strict
from core.ui_fx import blit_fit, make_vignette, make_grain, tint

class SceneStart:
    def __init__(self, mgr):
        self.mgr = mgr
        self.img = load_image_strict('ui/start_screen.png')
        self._fx_size = None
        self.vignette = None
        self.grain = None

    def handle(self, events):
        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                from gameplay.scene_mainmenu import SceneMainMenu
                self.mgr.switch_to(SceneMainMenu(self.mgr))

    def update(self, dt):
        pass

    def _ensure_fx(self, screen):
        size = screen.get_size()
        if self._fx_size != size:
            self._fx_size = size
            self.vignette = make_vignette(size, strength=0.75)
            self.grain = make_grain(size, intensity=26)

    def draw(self, screen):
        if self.img:
            blit_fit(screen, self.img)
        else:
            screen.fill((8, 10, 14))
        self._ensure_fx(screen)
        tint(screen, color=(20,28,42), alpha=36)
        if self.vignette: screen.blit(self.vignette, (0,0))
        if self.grain: screen.blit(self.grain, (0,0))
