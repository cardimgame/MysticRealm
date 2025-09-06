
# gameplay/scene_save_slots.py — Menu de 3 Save Slots (Skyrim-like) + hover arrow visual
import os, json, time, math
import pygame
from core.config import SAVES_DIR, SCREEN_SIZE
from core.strings import t
from core.settings import load_settings
from gameplay.actor_sprites import build_actor_sprites

try:
    from ui.theme import get_font
except Exception:
    def get_font(size):
        return pygame.font.SysFont('georgia', size)

SLOT_FILES = [SAVES_DIR / 'slot1.json', SAVES_DIR / 'slot2.json', SAVES_DIR / 'slot3.json']

# --- Visual helper: minimal hover arrow (tipo Skyrim), sem tocar na lógica ---
def draw_hover_arrow(screen: pygame.Surface, center: tuple, *, size: int = 14,
                     color=(240,220,160), pulse=True):
    """Desenha um pequeno cursor em forma de seta (>) com leve brilho/pulso.
    Somente visual (sem alterar navegação/estados). """
    cx, cy = center
    s = float(size)
    if pulse:
        t = pygame.time.get_ticks() * 0.001
        s *= (1.0 + 0.06*math.sin(t*6.0))
    s1 = int(s)
    s2 = int(s*0.6)
    # Triângulo apontando para a direita
    pts = [(cx, cy), (cx - s1, cy - s2), (cx - s1, cy + s2)]
    # Glow leve
    glow = pygame.Surface((int(s1*2), int(s1*2)), pygame.SRCALPHA)
    gx, gy = int(s1), int(s1)
    off_pts = [(p[0]-cx+gx, p[1]-cy+gy) for p in pts]
    for _, a in ((2,70),(1,110)):
        pygame.draw.polygon(glow, (*color, a), off_pts)
        screen.blit(glow, (cx-gx, cy-gy), special_flags=pygame.BLEND_ADD)
    # Corpo da seta
    pygame.draw.polygon(screen, color, pts)
    pygame.draw.polygon(screen, (20,20,28), pts, 1)

class SceneSaveSlots:
    def __init__(self, mgr, mode='load', on_loaded=None, on_saved=None, on_back=None):
        self.mgr = mgr
        self.mode = mode  # 'load' | 'save' | 'delete'
        self.on_loaded = on_loaded
        self.on_saved = on_saved
        self.on_back = on_back
        st = load_settings()
        self.lang = st.get('language','en-US')
        self.font_big = get_font(38)
        self.font = get_font(24)
        self.small = get_font(18)
        self.sel = 0
        self.preview_cache = [None, None, None]  # surfaces do avatar
        self._load_slots_meta()

    def _load_slots_meta(self):
        self.slots = []
        for path in SLOT_FILES:
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding='utf-8'))
                except Exception:
                    data = None
                if data:
                    profile = data.get('profile', {})
                    name = profile.get('name', '—')
                    clazz = profile.get('clazz', 'Guerreiro')
                    race = profile.get('race','Humano')
                    clazz_label = t(f'class.{clazz}.name', self.lang)
                    play_s = int(data.get('play_time', 0))
                    h, m = play_s//3600, (play_s%3600)//60
                    ptime = (f"{h}h {m}m" if h>0 else f"{m}m") if play_s>0 else '—'
                    loc = data.get('location','—')
                    ts = time.localtime(path.stat().st_mtime)
                    when = time.strftime('%Y-%m-%d %H:%M', ts)
                    self.slots.append({
                        'exists': True,
                        'file': path,
                        'profile': profile,
                        'name': name,
                        'clazz': clazz,
                        'race': race,
                        'clazz_label': clazz_label,
                        'play_time_str': ptime,
                        'location': loc,
                        'when': when,
                        'data': data,
                    })
                else:
                    self.slots.append({'exists': False, 'file': path})
            else:
                self.slots.append({'exists': False, 'file': path})

    def handle(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.mgr.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % 3
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % 3
                elif e.key in (pygame.K_ESCAPE,):
                    if self.on_back:
                        self.on_back()
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm_action()

    def _confirm_action(self):
        slot = self.slots[self.sel]
        path = slot['file']
        # Ações por modo
        if self.mode == 'load':
            if slot.get('exists') and self.on_loaded:
                self.on_loaded(slot['data'])
        elif self.mode == 'save':
            try:
                from gameplay.scene_game import SceneGame
                if isinstance(self.mgr.current_scene, SceneGame):
                    data = self.mgr.current_scene._build_save_data(with_extras=True)
                    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
                    if self.on_saved:
                        self.on_saved({'slot': self.sel+1, 'path': str(path)})
                    self._load_slots_meta()
            except Exception:
                pass
        else:  # delete
            if slot.get('exists'):
                try:
                    os.remove(path)
                    self._load_slots_meta()
                except Exception:
                    pass

    def _avatar(self, idx):
        if self.preview_cache[idx] is not None:
            return self.preview_cache[idx]
        slot = self.slots[idx]
        surf = pygame.Surface((128,128), pygame.SRCALPHA)
        if slot.get('exists'):
            try:
                anim = build_actor_sprites(slot['profile'], size=(128,128))
                surf.blit(anim['idle'][0], (0,0))
            except Exception:
                pygame.draw.rect(surf, (80,120,180), (16,24,96,96), border_radius=12)
        else:
            pygame.draw.rect(surf, (60,60,70), (16,24,96,96), border_radius=12)
        self.preview_cache[idx] = surf
        return surf

    def draw(self, screen: pygame.Surface):
        w,h = SCREEN_SIZE
        screen.fill((12,14,20))
        veil = pygame.Surface((w,h), pygame.SRCALPHA)
        veil.fill((0,0,0,120))
        screen.blit(veil, (0,0))

        title_key = {'load':'saves.title.load','save':'saves.title.save','delete':'saves.title.delete'}.get(self.mode,'saves.title.load')
        head = self.font_big.render(t(title_key, self.lang), True, (230,230,230))
        screen.blit(head, head.get_rect(topleft=(int(w*0.10), int(h*0.12))))

        hint = self.small.render(t('saves.hint', self.lang), True, (180,180,180))
        screen.blit(hint, (int(w*0.10), int(h*0.86)))

        right_x = int(w * 0.84)
        card_w = int(w * 0.62)
        card_h = int(h * 0.18)
        gap = int(h * 0.04)
        top = int(h * 0.24)

        for i in range(3):
            y = top + i*(card_h + gap)
            rect = pygame.Rect(right_x - card_w, y, card_w, card_h)
            pygame.draw.rect(screen, (18,20,28), rect, border_radius=8)
            pygame.draw.rect(screen, (70,80,100) if i==self.sel else (40,48,64), rect, 2, border_radius=8)

            slot = self.slots[i]
            label = f"{t('saves.slot', self.lang)} {i+1}"
            lbl = self.font.render(label, True, (200,200,215))
            screen.blit(lbl, (rect.x + 14, rect.y + 12))

            av = self._avatar(i)
            screen.blit(av, (rect.x + 16, rect.y + 34))

            tx = rect.x + 16 + 128 + 16
            ty = rect.y + 36
            if slot.get('exists'):
                name = slot['name']
                clazz = slot['clazz_label']
                loc = slot['location']
                ptime = slot['play_time_str']
                when = slot['when']
                lines = [f"{name} — {clazz}", f"Play: {ptime}", f"Loc: {loc}", f"{when}"]
                col = (230,230,230)
            else:
                lines = [t('saves.available', self.lang), t('saves.empty', self.lang)]
                col = (190,190,200)
            for ln in lines:
                s = self.font.render(ln, True, col)
                screen.blit(s, (tx, ty)); ty += 30

            # Cursor seta (apenas no selecionado)
            if i == self.sel:
                cx = rect.x - 24
                cy = rect.centery
                draw_hover_arrow(screen, (cx, cy), size=16, color=(240,220,160), pulse=True)
