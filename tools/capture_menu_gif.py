import os, pygame
from core.settings import load_settings
from gameplay.scene_mainmenu import SceneMainMenu

def main():
    os.makedirs('captures', exist_ok=True)
    st = load_settings()
    w, h = st.get('resolution', [1280, 720])
    fps = 30; duration = 3.0
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()
    class DummyMgr:
        running = True
        def switch_to(self, scene): pass
    scene = SceneMainMenu(DummyMgr())
    t = 0.0; idx = 0
    while t < duration:
        dt = clock.tick(fps) / 1000.0; t += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
        scene.update(dt); scene.draw(screen)
        pygame.display.flip()
        pygame.image.save(screen, f"captures/menu_{idx:04d}.png"); idx += 1
    pygame.quit(); print(f"Captured {idx} frames in captures/")

if __name__ == '__main__':
    main()
