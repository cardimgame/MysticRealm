# gameplay/scene_game.py — jogo isométrico com câmera lookahead, hitbox e save slots (3)
import pygame, json
from typing import Optional
from core.config import SCREEN_SIZE, TILE_W, TILE_H
from core.tilemap_iso import IsoTileSet, IsoMap
from gameplay.player_iso import Player, set_map_offset
from systems.iso_math import grid_to_screen
from gameplay.inventory import Inventory
try:
    from core.camera_v2 import CameraV2 as CameraImpl
    _CAMERA_MODE = "v2"
except Exception:
    from core.camera import Camera as CameraImpl
    _CAMERA_MODE = "legacy"
try:
    from systems.mapgen_iso import generate_world as generate_iso_world
    _WORLD_GEN = "world"
except Exception:
    from systems.mapgen_iso import generate as generate_iso_world
    _WORLD_GEN = "classic"
from core.asset import missing_assets
from core.settings import load_settings
from core.strings import t
from ui.hud import draw_hud
from gameplay.enemies_iso import EnemiesIso
from gameplay.combat import draw_hitbox_debug

class SceneGame:
    def __init__(self, mgr, profile: Optional[dict] = None, loaded_state: Optional[dict] = None):
        self.mgr = mgr
        self.profile = profile or {}
        self.screen_w, self.screen_h = SCREEN_SIZE

        if loaded_state and "map" in loaded_state:
            data = loaded_state["map"]
            self.layers = data["layers"]
            start_r, start_c = loaded_state.get("player_rc", (data["player_start"][0], data["player_start"][1]))
            self.pois = loaded_state.get('pois', {})
            self._play_time = float(loaded_state.get('play_time', 0.0))
        else:
            if _WORLD_GEN == "world":
                data = generate_iso_world(cols=128, rows=128, mountain_frac=0.5, seed=2025)
            else:
                data = generate_iso_world(cols=64, rows=64)
            self.layers = data["layers"]
            start_r, start_c = data["player_start"]
            self.pois = data.get("pois", {})
            self._play_time = 0.0

        self.tileset = IsoTileSet()
        self.tilemap = IsoMap(self.layers, self.tileset)
        self.player = Player(start_r, start_c, profile=self.profile)
        set_map_offset(self.tilemap.offset_x, self.tilemap.offset_y)
        w, h = self.tilemap.world_bounds()
        self.camera = CameraImpl(self.screen_w, self.screen_h, w, h)
        if hasattr(self.camera, "set_profile"):
            self.camera.set_profile(zoom=1.25)
        px, py = grid_to_screen(self.player.r, self.player.c)
        px += self.tilemap.offset_x; py += self.tilemap.offset_y
        if hasattr(self.camera, "center_on"):
            self.camera.center_on((px + TILE_W // 2, py + TILE_H // 2))

        self.font = pygame.font.SysFont("consolas", 18)
        self.inv = Inventory()
        if loaded_state and "inventory" in loaded_state:
            self.inv.gold = loaded_state["inventory"].get("gold", 0)
            for k, v in loaded_state["inventory"].get("items", {}).items():
                self.inv.items[k] = v

        st = self.profile.get('stats', {}) or {}
        self.vitals_max = {'HP': st.get('HP', 60), 'MP': st.get('MP', 30), 'STA': st.get('STA', 30)}
        self.vitals = dict(self.vitals_max)

        self.paused = False
        self.st = load_settings()
        self.lang = self.st.get('language','en-US')
        self.pause_tabs = list(t('pause.tabs', self.lang))
        self.quest_hint = None
        self._show_inv = False

        self.enemies = EnemiesIso(tilemap=self.tilemap, pois=self.pois)

    def handle(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.mgr.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    return
            if self.paused:
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        idx = getattr(self, 'pause_sel', 0)
                        setattr(self, 'pause_sel', (idx - 1) % len(self.pause_tabs))
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        idx = getattr(self, 'pause_sel', 0)
                        setattr(self, 'pause_sel', (idx + 1) % len(self.pause_tabs))
                    elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self._save_quick({pygame.K_1:1, pygame.K_2:2, pygame.K_3:3}[e.key])
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._exec_pause()

    def _build_save_data(self, with_extras: bool=False) -> dict:
        loc = self._location_hint()
        data = {
            "profile": self.profile,
            "inventory": {"gold": self.inv.gold, "items": dict(self.inv.items)},
            "player_rc": (self.player.r, self.player.c),
            "map": {"layers": self.layers, "player_start": (int(self.player.r), int(self.player.c))},
        }
        if with_extras:
            data.update({
                "play_time": int(self._play_time),
                "location": loc,
                "pois": self.pois,
            })
        return data

    def _save_quick(self, slot:int):
        from core.config import SAVES_DIR
        path = SAVES_DIR / f"slot{int(slot)}.json"
        data = self._build_save_data(with_extras=True)
        try:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception:
            pass

    def _exec_pause(self):
        idx = getattr(self, 'pause_sel', 0)
        cur = self.pause_tabs[idx]
        if cur == t('pause.tabs', self.lang)[0]:
            self.paused = False
            return
        save_label = t('pause.tabs', self.lang)[3] if len(t('pause.tabs', self.lang))>3 else 'Save'
        if cur == save_label:
            from gameplay.scene_save_slots import SceneSaveSlots
            self.mgr.switch_to(SceneSaveSlots(self.mgr, mode='save',
                on_saved=lambda info: self.mgr.switch_to(self),
                on_back=lambda: self.mgr.switch_to(self)))
            return
        exit_label = t('pause.tabs', self.lang)[4] if len(t('pause.tabs', self.lang))>4 else 'Exit'
        if cur == exit_label:
            from gameplay.scene_mainmenu import SceneMainMenu
            self.mgr.switch_to(SceneMainMenu(self.mgr))
            return

    def _location_hint(self) -> str:
        r, c = int(self.player.r), int(self.player.c)
        if isinstance(self.pois.get('village_bbox'), (list, tuple)) and len(self.pois['village_bbox'])>=4:
            top,left,h,w = self.pois['village_bbox']
            if top <= r <= top+h and left <= c <= left+w:
                return t('poi.village', self.lang)
        caves = self.pois.get('cave_entrances') or []
        for (rr,cc) in caves:
            if (r-rr)**2 + (c-cc)**2 <= 25:
                return t('poi.cave', self.lang)
        if 'lake_bbox' in self.pois:
            top,left,h,w = self.pois['lake_bbox']
            if top <= r <= top+h and left <= c <= left+w:
                return t('poi.lake', self.lang)
        if 'mountain_bbox' in self.pois:
            top,left,h,w = self.pois['mountain_bbox']
            if top <= r <= top+h and left <= c <= left+w:
                return t('poi.peak', self.lang)
        return '—'

    def update(self, dt: float):
        if not self.paused:
            self._play_time += float(dt)
        self.player.update(dt)
        px, py = grid_to_screen(self.player.r, self.player.c)
        px += self.tilemap.offset_x; py += self.tilemap.offset_y
        focus = (px + TILE_W // 2, py + TILE_H // 2)
        vx_px = (self.player.vel_c - self.player.vel_r) * (TILE_W / 2.0)
        vy_px = (self.player.vel_c + self.player.vel_r) * (TILE_H / 2.0)
        if hasattr(self.camera, 'update'):
            self.camera.update(dt, focus_px=focus, vel_px=(vx_px, vy_px))
        elif hasattr(self.camera, 'follow'):
            fake = pygame.Rect(focus[0], focus[1], 1, 1)
            self.camera.follow(fake)
        self.enemies.update(dt, (self.player.r, self.player.c), self.tilemap.offset_x, self.tilemap.offset_y)
        if self.player.last_hitbox:
            for enemy in list(self.enemies.group.sprites()):
                if self.player.last_hitbox.colliderect(enemy.rect):
                    self.enemies.group.remove(enemy)
                    try:
                        self.inv.add_gold(1)
                    except Exception:
                        pass
                    if hasattr(self.camera, 'apply_shake'):
                        self.camera.apply_shake(6.0)

    def draw(self, screen: pygame.Surface):
        self.tilemap.draw(screen, self.camera)
        screen.blit(self.player.image, self.camera.world_to_screen(self.player.rect.topleft))
        self.enemies.draw_sorted(screen, self.camera)
        if self.player.last_hitbox:
            hr = self.player.last_hitbox.copy()
            hr.topleft = self.camera.world_to_screen(hr.topleft)
            draw_hitbox_debug(screen, hr)
        miss = missing_assets()
        if miss and self.st.get('show_missing', False):
            y = 8
            pane = pygame.Surface((self.screen_w, 84), pygame.SRCALPHA)
            pane.fill((0,0,0,160))
            screen.blit(pane, (0,0))
            screen.blit(self.font.render(t('debug.missing', self.lang), True, (255,220,160)), (12, y)); y += 22
            for p in miss[:2]:
                screen.blit(self.font.render('- ' + p, True, (220,220,220)), (12, y)); y += 20
            if len(miss) > 2:
                more = f"... +{len(miss)-2}"
                screen.blit(self.font.render(more, True, (200,200,200)), (12, y))
        try:
            draw_hud(screen, self)
        except Exception:
            pass
