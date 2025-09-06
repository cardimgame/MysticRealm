# core/tilemap_iso.py
import os
import pygame
from core.config import TILE_W, TILE_H, ASSETS_DIR
from systems.iso_math import grid_to_screen

GROUND_DIRS = [ASSETS_DIR / 'ground']


class IsoTileSet:
    def __init__(self):
        self.cache: dict[str, pygame.Surface] = {}

    def _try_load_disk(self, token: str) -> pygame.Surface | None:
        """Tenta carregar token.png das pastas de ground."""
        for d in GROUND_DIRS:
            p = d / f"{token}.png"
            if p.exists():
                img = pygame.image.load(str(p))
                return img.convert_alpha() if img.get_alpha() else img.convert()
        return None

    def get(self, token: str) -> pygame.Surface:
        if token in self.cache:
            return self.cache[token]
        img = self._try_load_disk(token)
        if img is None:
            from systems.tile_factory import build_tile  # fallback procedural
            img = build_tile(token)
        self.cache[token] = img
        return img


class IsoMap:
    def __init__(self, layers: list[dict], tileset: IsoTileSet):
        self.layers = layers
        self.tileset = tileset
        self.rows = len(layers[0]['grid']) if layers else 0
        self.cols = len(layers[0]['grid'][0]) if self.rows > 0 else 0

        # OFFSET: garante mundo todo em coordenadas não-negativas (x>=0)
        # Em projeção losango comum, x_min ≈ -(rows-1)*(TILE_W/2).
        self.offset_x = (self.rows - 1) * (TILE_W // 2)
        self.offset_y = 0

    def world_bounds(self) -> tuple[int, int]:
        """Dimensão teórica do losango projetado (sem considerar zoom)."""
        w = (self.cols + self.rows) * (TILE_W // 2)
        h = (self.cols + self.rows) * (TILE_H // 2)
        return int(w), int(h)

    def _get_cam_rect_world(self, camera) -> pygame.Rect:
        """
        Retângulo da câmera em UNIDADES DE MUNDO.
        Se a câmera tem 'zoom', ajusta a largura/altura para world-space (screen/zoom).
        """
        if hasattr(camera, "zoom"):
            view_w = int(camera.screen_w / max(0.0001, float(camera.zoom)))
            view_h = int(camera.screen_h / max(0.0001, float(camera.zoom)))
            return pygame.Rect(int(camera.x), int(camera.y), view_w, view_h)
        return camera.get_rect() if hasattr(camera, "get_rect") else pygame.Rect(
            getattr(camera, "x", 0), getattr(camera, "y", 0),
            getattr(camera, "screen_w", 0), getattr(camera, "screen_h", 0)
        )

    def draw_visible(self, screen: pygame.Surface, camera):
        if not self.layers:
            return

        cam = self._get_cam_rect_world(camera)
        pad_x, pad_y = TILE_W, TILE_H
        view = cam.inflate(pad_x * 2, pad_y * 2)

        # Determina as células visíveis com offset aplicado
        visible_cells: list[tuple[int, int, int, int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = grid_to_screen(r, c)
                x += self.offset_x
                y += self.offset_y
                if (x + TILE_W > view.x and x < view.right and
                    y + TILE_H > view.y and y < view.bottom):
                    visible_cells.append((r, c, x, y))

        # Ordem de desenho (fundo->frente)
        visible_cells.sort(key=lambda t: (t[0] + t[1], t[0]))

        for layer in self.layers:
            grid = layer['grid']
            for r, c, x, y in visible_cells:
                token = grid[r][c]
                if not token:
                    continue
                img = self.tileset.get(token)
                screen.blit(img, camera.world_to_screen((x, y)))