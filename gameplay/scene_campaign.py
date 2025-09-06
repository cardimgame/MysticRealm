
import pygame
from core.ui_fx import make_vignette, make_grain, tint
from core.settings import load_settings
from core.strings import t
from ui.theme import COLORS, SPACING, get_font
from ui.widgets import RightMenuList

class SceneCampaign:
    def __init__(self, mgr):
        self.mgr = mgr
        st = load_settings()
        self.lang = st.get('language','en-US')
        self.font = get_font(38)
        self._fx_size = None
        self.vignette = None
        self.grain = None
        self.menu = RightMenuList(self.font)
        self.sel = 0

    def handle(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.mgr.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % 4
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % 4
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._exec()
                elif e.key == pygame.K_ESCAPE:
                    from gameplay.scene_mainmenu import SceneMainMenu
                    self.mgr.switch_to(SceneMainMenu(self.mgr))

    def update(self, dt):
        self.menu.update(dt)

    def _exec(self):
        # 0 New Game, 1 Load Game, 2 Delete Game, 3 Back
        if self.sel == 0:
            from gameplay.char_create import SceneCharCreate
            self.mgr.switch_to(SceneCharCreate(self.mgr, on_complete=lambda profile: self._start_game(profile)))
        elif self.sel == 1:
            from gameplay.scene_save_slots import SceneSaveSlots
            self.mgr.switch_to(SceneSaveSlots(self.mgr, mode='load', on_loaded=self._start_loaded, on_back=lambda: self.mgr.switch_to(self)))
        elif self.sel == 2:
            from gameplay.scene_save_slots import SceneSaveSlots
            self.mgr.switch_to(SceneSaveSlots(self.mgr, mode='delete', on_back=lambda: self.mgr.switch_to(self)))
        else:
            from gameplay.scene_mainmenu import SceneMainMenu
            self.mgr.switch_to(SceneMainMenu(self.mgr))

    def _start_game(self, profile):
        from gameplay.scene_game import SceneGame
        self.mgr.switch_to(SceneGame(self.mgr, profile=profile))

    def _start_loaded(self, data):
        from gameplay.scene_game import SceneGame
        profile = data.get('profile', {})
        self.mgr.switch_to(SceneGame(self.mgr, profile=profile, loaded_state=data))

    def _ensure_fx(self, screen):
        size = screen.get_size()
        if self._fx_size != size:
            self._fx_size = size
            self.vignette = make_vignette(size, strength=0.75)
            self.grain = make_grain(size, intensity=22)

    def draw(self, screen):
        screen.fill(COLORS['bg'])
        self._ensure_fx(screen)
        tint(screen, color=(20, 28, 42), alpha=42)
        if self.vignette: screen.blit(self.vignette, (0,0))
        if self.grain: screen.blit(self.grain, (0,0))
        options = t('campaign.options', self.lang)
        self.menu.draw(screen, options, self.sel, x_frac=0.82, y_frac=0.32, gap=SPACING['menu_gap']-2)
