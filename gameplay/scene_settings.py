
import pygame
from core.settings import load_settings, save_settings
from systems.audio import apply_settings
from core.strings import t
from ui.theme import COLORS, get_font

LANG_CODES = ['en-US','pt-BR']

class SceneSettings:
    def __init__(self, mgr, on_back=None):
        self.mgr = mgr
        self.on_back = on_back
        self.font_title = get_font(52)
        self.font = get_font(32)
        self.small = get_font(22)
        self.st = load_settings()
        self.lang = self.st.get('language','en-US')
        # items are ids; display uses t('settings.<id>')
        self.main_ids = ['resolution','fps','audio','mute','difficulty','controls','language','show_missing','back']
        self.sel = 0
        self.mode = 'main'  # main | resolution | fps | difficulty | audio | controls | language
        self.res_list = [(1280,720), (1600,900), (1920,1080)]
        self.fps_list = [30, 60]
        self.diff_list = ['easy','normal','hard']
        self.sub_index = 0

    def _apply_and_save(self):
        save_settings(self.st)
        try: apply_settings()
        except Exception: pass

    def handle(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN: 
                continue
            if self.mode == 'main':
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % len(self.main_ids)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % len(self.main_ids)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._enter_main()
                elif e.key == pygame.K_ESCAPE:
                    self._go_back()
            else:
                if e.key in (pygame.K_ESCAPE,):
                    self.mode = 'main'
                elif e.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s, pygame.K_RETURN, pygame.K_SPACE):
                    self._handle_submenu(e)

    def _enter_main(self):
        cur_id = self.main_ids[self.sel]
        if cur_id == 'resolution':
            self.mode = 'resolution'
            try:
                self.sub_index = max(0, self.res_list.index(tuple(self.st.get('resolution',(1280,720)))))
            except ValueError:
                self.sub_index = 0
        elif cur_id == 'fps':
            self.mode = 'fps'
            try:
                self.sub_index = max(0, self.fps_list.index(int(self.st.get('fps',60))))
            except ValueError:
                self.sub_index = 1
        elif cur_id == 'audio':
            self.mode = 'audio'
        elif cur_id == 'mute':
            self.st['mute'] = not self.st.get('mute', False)
            self._apply_and_save()
        elif cur_id == 'difficulty':
            self.mode = 'difficulty'
            curd = self.st.get('difficulty','normal')
            try:
                self.sub_index = max(0, self.diff_list.index(curd))
            except ValueError:
                self.sub_index = 1
        elif cur_id == 'controls':
            self.mode = 'controls'
        elif cur_id == 'show_missing':
            self.st['show_missing'] = not self.st.get('show_missing', False)
            self._apply_and_save()
        elif cur_id == 'language':
            self.mode = 'language'
            cur = self.st.get('language','en-US')
            try:
                self.sub_index = LANG_CODES.index(cur)
            except ValueError:
                self.sub_index = 0
        else:
            self._go_back()

    def _handle_submenu(self, e: pygame.event.Event):
        if self.mode == 'resolution':
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sub_index = (self.sub_index - 1) % len(self.res_list)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sub_index = (self.sub_index + 1) % len(self.res_list)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.st['resolution'] = list(self.res_list[self.sub_index])
                self._apply_and_save(); self.mode = 'main'
        elif self.mode == 'fps':
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sub_index = (self.sub_index - 1) % len(self.fps_list)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sub_index = (self.sub_index + 1) % len(self.fps_list)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.st['fps'] = int(self.fps_list[self.sub_index])
                self._apply_and_save(); self.mode = 'main'
        elif self.mode == 'difficulty':
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sub_index = (self.sub_index - 1) % len(self.diff_list)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sub_index = (self.sub_index + 1) % len(self.diff_list)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.st['difficulty'] = self.diff_list[self.sub_index]
                self._apply_and_save(); self.mode = 'main'
        elif self.mode == 'audio':
            vol = int(self.st.get('volume',100))
            if e.key in (pygame.K_UP, pygame.K_w): vol = min(100, vol + 1)
            elif e.key in (pygame.K_DOWN, pygame.K_s): vol = max(0, vol - 1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE): self.mode = 'main'; return
            self.st['volume'] = vol; self._apply_and_save()
        elif self.mode == 'controls':
            if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE): self.mode = 'main'
        elif self.mode == 'language':
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sub_index = (self.sub_index - 1) % len(LANG_CODES)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sub_index = (self.sub_index + 1) % len(LANG_CODES)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.st['language'] = LANG_CODES[self.sub_index]
                self.lang = self.st['language']
                self._apply_and_save(); self.mode = 'main'

    def _go_back(self):
        if self.on_back: self.on_back()

    def draw(self, screen):
        screen.fill((12, 14, 18))
        # title
        screen.blit(self.font_title.render(t('settings.title', self.lang), True, COLORS['heading']), (48, 36))
        if self.mode == 'main':
            y = 160
            for i, sid in enumerate(self.main_ids):
                col = (255,255,210) if i == self.sel else (200,200,200)
                name = t('settings.'+sid, self.lang)
                val = ''
                if sid == 'resolution': val = f"{tuple(self.st.get('resolution',(1280,720)))}"
                elif sid == 'fps': val = f"{self.st.get('fps',60)}"
                elif sid == 'audio': val = f"{self.st.get('volume',100)}%"
                elif sid == 'mute': val = 'On' if self.st.get('mute',False) else 'Off'
                elif sid == 'difficulty': val = self.st.get('difficulty','normal')
                elif sid == 'language':
                    cur = self.st.get('language','en-US')
                    names = t('settings.lang.values', self.lang)
                    idx = LANG_CODES.index(cur) if cur in LANG_CODES else 0
                    val = names[idx]
                text = f"{name}" + (f" — {val}" if val else "")
                screen.blit(self.font.render(text, True, col), (72, y)); y += 44
        else:
            y = 160
            title_map = {
                'resolution': 'settings.resolution','fps':'settings.fps','difficulty':'settings.difficulty','audio':'settings.audio','controls':'settings.controls','language':'settings.language'
            }
            screen.blit(self.font.render(t(title_map.get(self.mode,'settings.title'), self.lang), True, (230,230,230)), (72, 120))
            if self.mode == 'resolution':
                for i, opt in enumerate(self.res_list):
                    col = (255,255,210) if i == self.sub_index else (200,200,200)
                    screen.blit(self.font.render(f"{opt}", True, col), (92, y)); y += 42
            elif self.mode == 'fps':
                for i, opt in enumerate(self.fps_list):
                    col = (255,255,210) if i == self.sub_index else (200,200,200)
                    screen.blit(self.font.render(str(opt), True, col), (92, y)); y += 42
            elif self.mode == 'difficulty':
                for i, opt in enumerate(self.diff_list):
                    col = (255,255,210) if i == self.sub_index else (200,200,200)
                    screen.blit(self.font.render(opt.title(), True, col), (92, y)); y += 42
            elif self.mode == 'audio':
                vol = self.st.get('volume',100)
                msg = f"Volume: {vol}% (↑/↓ adjust, ENTER ok)"
                screen.blit(self.font.render(msg, True, (220,220,220)), (72, y))
            elif self.mode == 'controls':
                msg = "Controls: remap (soon). ENTER/ESC back."
                screen.blit(self.font.render(msg, True, (220,220,220)), (72, y))
            elif self.mode == 'language':
                names = t('settings.lang.values', self.lang)
                for i, code in enumerate(LANG_CODES):
                    label = names[i] if i < len(names) else code
                    col = (255,255,210) if i == self.sub_index else (200,200,200)
                    screen.blit(self.font.render(label, True, col), (92, y)); y += 42
