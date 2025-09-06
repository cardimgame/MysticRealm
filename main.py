
import pygame, sys
from core.config import SCREEN_SIZE, FPS
from core.state_manager import StateManager
from gameplay.scene_start import SceneStart
from systems.audio import ensure_audio

# main.py – exemplo
import pygame
from core.settings import load_settings, save_settings
from core.state_manager import StateManager
from gameplay.scene_start import SceneStart

def main():
    pygame.init()
    st = load_settings()
    size = tuple(st.get('resolution', [1280,720]))
    screen = pygame.display.set_mode(size)  # ideal: pygame.RESIZABLE se quiser
    clock = pygame.time.Clock()
    fps_cap = int(st.get('fps', 60))

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
