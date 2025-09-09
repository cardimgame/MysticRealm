# gameplay/scene_save_slots.py — simple 3-slot UI for load/save/delete
import os, json
import pygame
from pathlib import Path
from core.config import SAVES_DIR
from core.strings import t
from core.settings import load_settings
from systems.save_load import list_saves, load_game, save_game, SLOTS

try:
    from ui.theme import get_font
except Exception:
    def get_font(size):
        return pygame.font.SysFont('georgia', size)

class SceneSaveSlots:
    def __init__(self, mgr, mode='load', on_loaded=None, on_saved=None, on_back=None):
        self.mgr = mgr
        self.mode = mode  # 'load' | 'save' | 'delete'
        self.on_loaded = on_loaded
        self.on_saved = on_saved
        self.on_back = on_back
        st = load_settings()
        self.lang = st.get('language','en-US')
        self.font = get_font(28)
        self.small = get_font(18)
        self.sel = 0
        self._meta = self._load_slots_meta()

    def _load_slots_meta(self):
        meta = []
        for p in SLOTS:
            if Path(p).exists():
                try:
                    data = json.loads(Path(p).read_text(encoding='utf-8'))
                except Exception:
                    data = None
                if data:
                    name = (data.get('profile', {}) or {}).get('name') or t('saves.available', self.lang)
                    meta.append({'exists': True, 'name': name, 'path': p})
                else:
                    meta.append({'exists': True, 'name': t('saves.available', self.lang), 'path': p})
            else:
                meta.append({'exists': False, 'name': t('saves.empty', self.lang), 'path': p})
        return meta

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    self.sel = (self.sel - 1) % 3
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.sel = (self.sel + 1) % 3
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.mode == 'load':
                        p = self._meta[self.sel]['path']
                        data = load_game(p)
                        if data and self.on_loaded:
                            self.on_loaded(data)
                    elif self.mode == 'save':
                        # try to get current SceneGame
                        from gameplay.scene_game import SceneGame
                        cur = self.mgr.current_scene
                        if isinstance(cur, SceneGame):
                            data = cur._build_save_data()
                            if save_game(self.sel, data) and self.on_saved:
                                self.on_saved(self.sel)
                    else:  # delete
                        # delete file if exists
                        p = Path(self._meta[self.sel]['path'])
                        if p.exists():
                            try: p.unlink()
                            except Exception: pass
                        # reload meta
                        self._meta = self._load_slots_meta()
                elif e.key == pygame.K_ESCAPE:
                    if self.on_back:
                        self.on_back()

    def update(self, dt):
        pass

    def draw(self, screen):
        w, h = screen.get_size()
        screen.fill((12,14,18))
        title_key = 'saves.title.save' if self.mode=='save' else ('saves.title.delete' if self.mode=='delete' else 'saves.title.load')
        title = self.font.render(t(title_key, self.lang), True, (235,235,235))
        screen.blit(title, (int(w*0.08), int(h*0.12)))
        hint = self.small.render(t('saves.hint', self.lang), True, (170,170,180))
        screen.blit(hint, (int(w*0.08), int(h*0.16)))

        # draw three panels
        pw, ph = int(w*0.22), int(h*0.28)
        gap = int(w*0.04)
        start_x = int(w*0.08);
        y = int(h*0.30)
        for i in range(3):
            x = start_x + i*(pw+gap)
            rect = pygame.Rect(x, y, pw, ph)
            sel = (i == self.sel)
            pygame.draw.rect(screen, (26,28,36), rect, border_radius=8)
            pygame.draw.rect(screen, (230,210,160) if sel else (90,90,120), rect, 2, border_radius=8)
            label = f"{t('saves.slot', self.lang)} {i+1}"
            screen.blit(self.small.render(label, True, (210,210,210)), (rect.x+12, rect.y+10))
            name = self._meta[i]['name']
            screen.blit(self.font.render(name, True, (240,220,160) if sel else (200,200,210)), (rect.x+12, rect.y+44))
