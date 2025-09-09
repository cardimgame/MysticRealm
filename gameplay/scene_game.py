
# gameplay/scene_game.py — CameraV2.update + foco/zoom dinâmicos + flip opcional
import pygame
from typing import Optional
from core.config import SCREEN_SIZE, TILE_W, TILE_H
from core.camera_v2 import CameraV2
from core.map_iso2 import IsoTileSet2 as IsoTileSet, IsoMap2 as IsoMap
from core.iso_math2 import grid_to_screen, screen_to_grid
from gameplay.player_iso import Player, set_map_offset
from gameplay.enemies_iso import EnemiesIso
from gameplay.combat import draw_hitbox_debug
from core.asset import missing_assets
from core.strings import t
from core.ui_fx import tint
from core.props import PropsManager
from systems.prop_factory import build_prop as _build_prop
from core import props as _core_props
from systems.mapgen_caelari import generate as generate_layers
from core.settings import load_settings
from systems.depth_group import DepthGroup
from systems.overlap_zone import OverlapZone
from core.fx_pipeline import PostFX

_core_props.load_prop_image = _build_prop

class SceneGame:
    def __init__(self, mgr, profile: Optional[dict] = None, loaded_state: Optional[dict] = None):
        self.mgr = mgr
        self.w, self.h = SCREEN_SIZE
        st = load_settings()
        self.lang = st.get('language', 'en-US')
        # FX leves — desabilitados por padrão
        self.fx_enabled_bloom = False
        self.fx_enabled_dof = False
        self.postfx = PostFX(st.get('fx_quality','half'))
        # MAPA 128x128
        result = generate_layers(rows=128, cols=128, seed=2025)
        if len(result) == 4:
            layers, pois, start_rc, props_rc = result
        else:
            layers, pois, start_rc = result
            props_rc = []
        self.tileset = IsoTileSet()
        self.tilemap = IsoMap(layers, self.tileset)
        set_map_offset(self.tilemap.offset_x, self.tilemap.offset_y)
        world_w, world_h = self.tilemap.world_bounds()
        # Camera ISO estável com framing tipo OT2
        self.camera = CameraV2(self.w, self.h, world_w, world_h, zoom=1.10)
        self.cam_anchor = (0.50, 0.62)  # player pouco abaixo do centro
        # Orientação visual (1 normal, -1 flip horizontal)
        self.orient = 1

        self.entities = DepthGroup()
        self.player = Player(start_rc[0], start_rc[1], profile or {})
        self.entities.add(self.player)
        self.enemies = EnemiesIso(tilemap=self.tilemap, pois=pois)
        for e in self.enemies.group.sprites():
            self.entities.add(e)
        self.props_mgr = PropsManager()
        for p in props_rc:
            r, c = int(p.get('r',0)), int(p.get('c',0))
            x, y = grid_to_screen(r, c)
            x += self.tilemap.offset_x
            y += self.tilemap.offset_y
            self.props_mgr.add_prop(p.get('key','unknown'), x, y-6, bool(p.get('collidable', True)))
        self.overlaps: list[OverlapZone] = []
        self.paused = False
        self.pause_tabs = list(t('pause.tabs', self.lang))
        self.pause_sel = 0
        self.font = pygame.font.SysFont('consolas', 18)
        self._last_dt = 0.0
        if loaded_state:
            pr = loaded_state.get('player_rc')
            if pr and isinstance(pr, (list, tuple)) and len(pr) == 2:
                self.player.r, self.player.c = float(pr[0]), float(pr[1])
                self.player.update(0.0)
        # Render target opaco (sem alpha) para evitar ghosting
        self._rt_size = None
        self._rt = None
        self._bg_color = (10, 12, 18)

    # --- helpers ---
    def _ensure_rt(self):
        vw = max(1, int(self.w / max(0.0001, float(self.camera.zoom))))
        vh = max(1, int(self.h / max(0.0001, float(self.camera.zoom))))
        size = (vw, vh)
        if self._rt_size != size:
            self._rt_size = size
            self._rt = pygame.Surface(size).convert()

    def _set_zoom(self, z: float):
        z = max(0.85, min(1.50, float(z)))
        self.camera.set_profile(zoom=z)
        self._rt_size = None

    # --- input / pause ---
    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    return
                if e.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self._set_zoom(self.camera.zoom + 0.06)
                elif e.key in (pygame.K_MINUS, pygame.K_UNDERSCORE, pygame.K_KP_MINUS):
                    self._set_zoom(self.camera.zoom - 0.06)
                elif e.key == pygame.K_q:
                    # Alterna orientação visual (flip horizontal)
                    self.orient = -1 if self.orient == 1 else 1
            if self.paused and e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.pause_sel = (self.pause_sel - 1) % len(self.pause_tabs)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_sel = (self.pause_sel + 1) % len(self.pause_tabs)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._exec_pause()
                    return

    def _exec_pause(self):
        cur = (self.pause_tabs[self.pause_sel] or '').lower()
        if 'continue' in cur or 'continuar' in cur:
            self.paused = False
        elif 'settings' in cur or 'configura' in cur:
            from gameplay.scene_settings import SceneSettings
            self.mgr.switch_to(SceneSettings(self.mgr, on_back=lambda: self.mgr.switch_to(self)))
        elif 'save' in cur or 'salvar' in cur:
            from gameplay.scene_save_slots import SceneSaveSlots
            self.mgr.switch_to(SceneSaveSlots(self.mgr, mode='save', on_saved=lambda _ : self.mgr.switch_to(self), on_back=lambda: self.mgr.switch_to(self)))
        else:
            from gameplay.scene_mainmenu import SceneMainMenu
            self.mgr.switch_to(SceneMainMenu(self.mgr))

    # --- update ---
    def update(self, dt: float):
        self._last_dt = dt
        if self.paused:
            return
        # 1) Input com cardinais puros + compensação do flip
        self.player.handle_input(dt, cardinais_puros=True, screen_dir=getattr(self, 'orient', 1))
        # 2) Atualiza player (sem retratar input)
        self.player.update(dt, input_already_handled=True)

        # 3) foco automático no inimigo mais próximo (se houver)
        near = None; d2_best = 1e12
        px, py = self.player.rect.center
        for e in self.enemies.group.sprites():
            ex, ey = e.rect.center
            dx, dy = (ex - px), (ey - py)
            d2 = dx*dx + dy*dy
            if d2 < d2_best:
                d2_best = d2; near = e
        if near and d2_best < (600*600):
            w = max(0.0, 1.0 - (d2_best ** 0.5) / 600.0)
            alpha = 0.35 + 0.25 * w
            fx = px * (1.0 - alpha) + near.rect.centerx * alpha
            fy = py * (1.0 - alpha) + near.rect.centery * alpha
        else:
            fx, fy = px, py

        # 4) âncora convertida para MUNDO (compensa zoom)
        ax = (self.w * self.cam_anchor[0]) / max(1e-6, self.camera.zoom)
        ay = (self.h * self.cam_anchor[1]) / max(1e-6, self.camera.zoom)
        focus_world = (fx - ax, fy - ay)

        # 5) velocidade do player em px de MUNDO (para lookahead)
        vx_px = (self.player.vel_c - self.player.vel_r) * (TILE_W / 2.0)
        vy_px = (self.player.vel_c + self.player.vel_r) * (TILE_H / 2.0)

        # 6) atualiza câmera nativa (deadzone + lookahead)
        self.camera.update(dt, focus_px=focus_world, vel_px=(vx_px, vy_px))

        # 7) atualiza inimigos e sistemas dependentes
        ox, oy = self.tilemap.offset_x, self.tilemap.offset_y
        self.enemies.update(dt, player_rc=(self.player.r, self.player.c), ox=ox, oy=oy)
        for e in self.enemies.group.sprites():
            self.entities.mark_dirty(e)
        for z in self.overlaps:
            z.apply(self.player, self.entities)
            for e in self.enemies.group.sprites():
                z.apply(e, self.entities)

        # 8) zoom dinâmico (abre em combate, fecha em exploração)
        base = 1.12
        if near and d2_best < (520*520):
            z_target = 0.98
        else:
            z_target = base
        z = self.camera.zoom + (z_target - self.camera.zoom) * 0.08
        self.camera.set_profile(zoom=z)

    # --- draw ---
    def draw(self, screen: pygame.Surface):
        # 0) limpa tela principal e RT
        screen.fill(self._bg_color)
        self._ensure_rt()
        rt = self._rt
        rt.fill(self._bg_color)

        # 1) desenha o mundo (zoom 1.0 na RT)
        world_w, world_h = self.tilemap.world_bounds()
        cam_draw = CameraV2(rt.get_width(), rt.get_height(), world_w, world_h, zoom=1.0)
        cam_draw.x = self.camera.x
        cam_draw.y = self.camera.y
        self.tilemap.draw_visible(rt, cam_draw)
        self.props_mgr.draw(rt, cam_draw, sort_by_y=True)
        cam_rect = pygame.Rect(int(self.camera.x), int(self.camera.y), rt.get_width(), rt.get_height()).inflate(320, 240)
        self.entities.draw_sorted(rt, cam_draw, clip_rect=cam_rect)
        draw_hitbox_debug(rt, self.player.last_hitbox)

        # 2) upscale para tela (visual zoom) e possível flip
        if (rt.get_width(), rt.get_height()) != (self.w, self.h):
            scaled = pygame.transform.smoothscale(rt, (self.w, self.h))
            final = pygame.transform.flip(scaled, True, False) if getattr(self, 'orient', 1) == -1 else scaled
            screen.blit(final, (0, 0))
        else:
            final = pygame.transform.flip(rt, True, False) if getattr(self, 'orient', 1) == -1 else rt
            screen.blit(final, (0, 0))
        # 3) overlays leves (opcionais)
        # (Bloom/DOF desabilitados por padrão para evitar qualquer rastro)
