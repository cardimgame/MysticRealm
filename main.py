import sys
import os
sys.path.append(os.path.dirname(__file__))

import pygame
import core.map_iso2 as M2
from core.settings import load_settings, save_settings
from core.state_manager import StateManager
from gameplay.scene_start import SceneStart
from systems.audio import ensure_audio

def main():
    pygame.init()
    st = load_settings()
    size = tuple(st.get('resolution', [1280, 720]))
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    fps_cap = int(st.get('fps', 60))

    # Inicializa gerenciador de estado
    mgr = StateManager()
    mgr.switch_to(SceneStart(mgr))

    while mgr.running:
        dt = clock.tick(fps_cap) / 1000.0
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                mgr.running = False

        if mgr.current_scene:
            if hasattr(mgr.current_scene, 'handle'):
                mgr.current_scene.handle(events)
            if hasattr(mgr.current_scene, 'update'):
                mgr.current_scene.update(dt)
            if hasattr(mgr.current_scene, 'draw'):
                mgr.current_scene.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
