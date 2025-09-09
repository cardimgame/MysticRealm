import pygame
from core.asset import load_image_strict
from core.ui_fx import blit_fit, blit_cover, make_vignette, make_grain, tint
from core.settings import load_settings
from core.strings import t
from ui.theme import COLORS, SPACING, get_font
from ui.widgets import RightMenuList
from systems.save_load import has_save_any, list_saves, load_game

class SceneMainMenu:
    def __init__(self, mgr):
        self.mgr = mgr
        st = load_settings()
        self.lang = st.get('language','en-US')
        self.bg = load_image_strict('ui/main_menu.png') or load_image_strict('ui/dragons_bg.png')
        self.font = get_font(40)
        self._fx_size = None
        self.vignette = None
        self.grain = None
        self.options = self._build_options()
        self.sel = 0
        self._t = 0.0
        self.menu = RightMenuList(self.font)

    def _build_options(self):
        opts = list(t('main.options', self.lang))
        if has_save_any():
            opts = [t('main.continue', self.lang)] + opts
        return opts

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % len(self.options)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % len(self.options)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._exec()
            elif e.type == pygame.QUIT:
                self.mgr.running = False

    def _exec(self):
        cur = (self.options[self.sel] or '').lower()
        if cur == t('main.continue', self.lang).lower():
            saves = list_saves()
            if saves:
                data = load_game(saves[0])
                if data:
                    from gameplay.scene_game import SceneGame
                    profile = data.get('profile', {})
                    self.mgr.switch_to(SceneGame(self.mgr, profile=profile, loaded_state=data))
            return
        if cur.startswith(t('main.options', self.lang)[0].lower()):
            from gameplay.scene_campaign import SceneCampaign
            self.mgr.switch_to(SceneCampaign(self.mgr))
        elif cur.startswith(t('main.options', self.lang)[1].lower()):
            from gameplay.scene_settings import SceneSettings
            self.mgr.switch_to(SceneSettings(self.mgr, on_back=lambda: self.mgr.switch_to(self)))
        else:
            self.mgr.running = False

    def _ensure_fx(self, screen):
        size = screen.get_size()
        if self._fx_size != size:
            self._fx_size = size
            self.vignette = make_vignette(size, strength=0.75)
            self.grain = make_grain(size, intensity=24)

    def update(self, dt):
        self._t += dt
        self.menu.update(dt)
        st = load_settings(); new_lang = st.get('language','en-US')
        if new_lang != self.lang:
            self.lang = new_lang
            self.options = self._build_options()

    def on_resize(self, size):
        self._fx_size = None

    def draw(self, screen):
        st = load_settings()
        mode = st.get('scale_mode','fit')
        if self.bg:
            (blit_cover if mode == 'cover' else blit_fit)(screen, self.bg)
        else:
            screen.fill(COLORS['bg'])
        self._ensure_fx(screen)
        tint(screen, color=(20,28,42), alpha=38)
        if self.vignette: screen.blit(self.vignette, (0,0))
        if self.grain: screen.blit(self.grain, (0,0))
        self.menu.draw(screen, self.options, self.sel, x_frac=0.82, y_frac=0.35, gap=SPACING['menu_gap'])
