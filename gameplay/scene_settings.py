import pygame
from core.settings import load_settings, save_settings
from core.strings import t

RES_LIST = [(1280,720), (1600,900), (1920,1080)]
LANG_LIST = ['en-US','pt-BR']

class SceneSettings:
    def __init__(self, mgr, on_back=None):
        self.mgr = mgr
        self.on_back = on_back
        st = load_settings()
        self.lang = st.get('language','en-US')
        self.font = pygame.font.SysFont('consolas', 24)
        self.small = pygame.font.SysFont('consolas', 18)
        try:
            self.res_idx = RES_LIST.index(tuple(st.get('resolution', [1280,720])))
        except ValueError:
            self.res_idx = 0
        self.scale_mode = st.get('scale_mode','fit')
        self.fx_bloom = bool(st.get('fx_bloom', True))
        self.fx_dof = bool(st.get('fx_dof', True))
        self.fx_quality = st.get('fx_quality','half')
        try:
            self.lang_idx = LANG_LIST.index(self.lang)
        except ValueError:
            self.lang_idx = 0
        # Reintroduce Language option
        self.items = ['resolution', 'scale_mode', 'language', 'fx_bloom', 'fx_dof', 'fx_quality', 'back']
        self.sel = 0

    def _apply_resolution(self):
        st = load_settings()
        w, h = RES_LIST[self.res_idx]
        st['resolution'] = [w, h]
        save_settings(st)
        flags = pygame.RESIZABLE
        pygame.display.set_mode((w, h), flags)
        cur = self.mgr.current_scene
        if cur and hasattr(cur, 'on_resize'):
            cur.on_resize((w, h))

    def _toggle_scale_mode(self):
        st = load_settings()
        self.scale_mode = 'cover' if self.scale_mode == 'fit' else 'fit'
        st['scale_mode'] = self.scale_mode
        save_settings(st)

    def _toggle_fx(self, key):
        st = load_settings()
        if key == 'fx_bloom':
            self.fx_bloom = not self.fx_bloom
            st['fx_bloom'] = self.fx_bloom
        elif key == 'fx_dof':
            self.fx_dof = not self.fx_dof
            st['fx_dof'] = self.fx_dof
        elif key == 'fx_quality':
            self.fx_quality = 'quarter' if self.fx_quality == 'half' else 'half'
            st['fx_quality'] = self.fx_quality
        save_settings(st)

    def _toggle_language(self, step):
        self.lang_idx = (self.lang_idx + step) % len(LANG_LIST)
        new_lang = LANG_LIST[self.lang_idx]
        st = load_settings(); st['language'] = new_lang; save_settings(st)
        self.lang = new_lang  # update local for immediate labels

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % len(self.items)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % len(self.items)
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    it = self.items[self.sel]
                    if it == 'resolution':
                        self.res_idx = (self.res_idx - 1) % len(RES_LIST)
                        self._apply_resolution()
                    elif it == 'scale_mode':
                        self._toggle_scale_mode()
                    elif it == 'language':
                        self._toggle_language(-1)
                    elif it in ('fx_bloom','fx_dof','fx_quality'):
                        self._toggle_fx(it)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    it = self.items[self.sel]
                    if it == 'resolution':
                        self.res_idx = (self.res_idx + 1) % len(RES_LIST)
                        self._apply_resolution()
                    elif it == 'scale_mode':
                        self._toggle_scale_mode()
                    elif it == 'language':
                        self._toggle_language(+1)
                    elif it in ('fx_bloom','fx_dof','fx_quality'):
                        self._toggle_fx(it)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.items[self.sel] == 'back' and self.on_back:
                        self.on_back()
                elif e.key == pygame.K_ESCAPE:
                    if self.on_back:
                        self.on_back()

    def update(self, dt):
        pass

    def draw(self, screen):
        w, h = screen.get_size()
        screen.fill((14,16,22))
        title = self.font.render(t('settings.title', self.lang), True, (235,235,235))
        screen.blit(title, (int(w*0.08), int(h*0.12)))
        y = int(h*0.24)
        # resolution
        res_txt = f"{t('settings.resolution', self.lang)}: {RES_LIST[self.res_idx][0]}x{RES_LIST[self.res_idx][1]}"
        col = (240,220,160) if self.items[self.sel]=='resolution' else (210,210,215)
        screen.blit(self.font.render(res_txt, True, col), (int(w*0.10), y)); y += 40
        # scale mode
        vals = t('settings.scale_mode.values', self.lang)
        mode_label = vals[0] if self.scale_mode=='fit' else vals[1]
        sm_txt = f"{t('settings.scale_mode', self.lang)}: {mode_label}"
        col = (240,220,160) if self.items[self.sel]=='scale_mode' else (210,210,215)
        screen.blit(self.font.render(sm_txt, True, col), (int(w*0.10), y)); y += 40
        # language
        langs = t('settings.lang.values', self.lang)
        lang_label = langs[self.lang_idx]
        lx = f"{t('settings.language', self.lang)}: {lang_label}"
        col = (240,220,160) if self.items[self.sel]=='language' else (210,210,215)
        screen.blit(self.font.render(lx, True, col), (int(w*0.10), y)); y += 40
        # FX bloom
        bx = t('settings.fx_bloom', self.lang) + f": {'ON' if self.fx_bloom else 'OFF'}"
        col = (240,220,160) if self.items[self.sel]=='fx_bloom' else (210,210,215)
        screen.blit(self.font.render(bx, True, col), (int(w*0.10), y)); y += 34
        # FX dof
        dx = t('settings.fx_dof', self.lang) + f": {'ON' if self.fx_dof else 'OFF'}"
        col = (240,220,160) if self.items[self.sel]=='fx_dof' else (210,210,215)
        screen.blit(self.font.render(dx, True, col), (int(w*0.10), y)); y += 34
        # FX quality
        qvals = t('settings.fx_quality.values', self.lang)
        label = qvals[0] if self.fx_quality=='half' else qvals[1]
        qx = f"{t('settings.fx_quality', self.lang)}: {label}"
        col = (240,220,160) if self.items[self.sel]=='fx_quality' else (210,210,215)
        screen.blit(self.font.render(qx, True, col), (int(w*0.10), y)); y += 40
        # back
        col = (240,220,160) if self.items[self.sel]=='back' else (210,210,215)
        screen.blit(self.font.render(t('settings.back', self.lang), True, col), (int(w*0.10), y))
