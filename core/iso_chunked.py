# core/iso_chunked.py
from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Optional
from core.config import TILE_W, TILE_H

# Utilidade local: projeção 2:1 (mesmo que systems.iso_math)
def _grid_to_screen(ix: int, iy: int, origin: Tuple[int,int]) -> Tuple[int,int]:
    ox, oy = origin
    x = (iy - ix) * (TILE_W // 2) + ox
    y = (iy + ix) * (TILE_H // 2) + oy
    return x, y

@dataclass
class ChunkSpec:
    rows: int = 24
    cols: int = 24
    lru_max: int = 12

class IsoChunkedMap:
    """
    Renderer isométrico por CHUNKS com bake estático das camadas de chão.
    - Cada chunk gera 1 Surface do footprint isométrico (ground + overlays estáticas).
    - draw() blita só os chunks visíveis (culling por retângulo de câmera).
    - Props/entidades dinâmicas devem ser desenhadas por cima, fora deste bake.
    """
    def __init__(self, layers: List[Dict[str, Any]], tileset, origin: Tuple[int,int]=(0,0), spec: ChunkSpec=ChunkSpec()):
        assert layers and 'grid' in layers[0], 'layers inválidas'
        self.layers = layers
        self.tileset = tileset
        self.origin = origin
        self.spec = spec
        self.rows = len(layers[0]['grid'])
        self.cols = len(layers[0]['grid'][0]) if self.rows>0 else 0
        # Chunks em grid
        self.cr = (self.rows + spec.rows - 1) // spec.rows
        self.cc = (self.cols + spec.cols - 1) // spec.cols
        # Cache LRU de bakes
        self.cache: Dict[Tuple[int,int], pygame.Surface] = {}
        self.lru: List[Tuple[int,int]] = []

        # Origem (0,0) do grid em pixels mundiais para alinhar como seu IsoMap
        # Mesma lógica do tilemap_iso: desloca X para manter x>=0
        self.map_offset_x = (self.rows - 1) * (TILE_W // 2)
        self.map_offset_y = 0

    # --- Helpers chunk ---
    def chunk_grid_rect(self, cr: int, cc: int) -> Tuple[int,int,int,int]:
        """Retorna (r0, r1, c0, c1) inclusivo do sub-grid do chunk."""
        r0 = cr * self.spec.rows
        c0 = cc * self.spec.cols
        r1 = min(self.rows-1, r0 + self.spec.rows - 1)
        c1 = min(self.cols-1, c0 + self.spec.cols - 1)
        return r0, r1, c0, c1

    def chunk_world_rect(self, cr: int, cc: int) -> pygame.Rect:
        """Retorna o retângulo mundial em px que cobre o chunk."""
        r0, r1, c0, c1 = self.chunk_grid_rect(cr, cc)
        # canto superior esquerdo do chunk
        x0, y0 = _grid_to_screen(r0, c0, (self.map_offset_x, self.map_offset_y))
        # canto inferior direito do chunk (r1+1,c1) e (r1,c1+1) para pegar extremidades
        x1a, y1a = _grid_to_screen(r1+1, c1, (self.map_offset_x, self.map_offset_y))
        x1b, y1b = _grid_to_screen(r1, c1+1, (self.map_offset_x, self.map_offset_y))
        # bounding box
        left = min(x0, x1a, x1b)
        top  = min(y0, y1a, y1b)
        right= max(x0 + TILE_W, x1a + TILE_W, x1b + TILE_W)
        bottom=max(y0 + TILE_H, y1a + TILE_H, y1b + TILE_H)
        return pygame.Rect(left, top, right-left, bottom-top)

    def _lru_touch(self, key: Tuple[int,int]):
        if key in self.lru:
            self.lru.remove(key)
        self.lru.append(key)
        while len(self.lru) > self.spec.lru_max:
            old = self.lru.pop(0)
            if old in self.cache:
                del self.cache[old]

    def _bake_chunk(self, cr: int, cc: int) -> pygame.Surface:
        rect = self.chunk_world_rect(cr, cc)
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        r0, r1, c0, c1 = self.chunk_grid_rect(cr, cc)
        # desenha camadas na ordem
        for layer in self.layers:
            grid = layer['grid']
            # nota: tokens vazios ('') são pulados
            for r in range(r0, r1+1):
                for c in range(c0, c1+1):
                    token = grid[r][c]
                    if not token:
                        continue
                    img = self.tileset.get(token)
                    wx, wy = _grid_to_screen(r, c, (self.map_offset_x, self.map_offset_y))
                    # local dentro do chunk
                    lx = int(wx - rect.left)
                    ly = int(wy - rect.top)
                    surf.blit(img, (lx, ly))
        return surf

    def get_chunk(self, cr: int, cc: int) -> pygame.Surface:
        key = (cr, cc)
        if key not in self.cache:
            self.cache[key] = self._bake_chunk(cr, cc)
        self._lru_touch(key)
        return self.cache[key]

    # --- Culling por chunk ---
    def _camera_world_rect(self, camera) -> pygame.Rect:
        if hasattr(camera, 'zoom') and getattr(camera, 'zoom'):
            view_w = int(getattr(camera, 'screen_w', 0) / max(0.0001, float(getattr(camera, 'zoom', 1))))
            view_h = int(getattr(camera, 'screen_h', 0) / max(0.0001, float(getattr(camera, 'zoom', 1))))
            return pygame.Rect(int(getattr(camera, 'x', 0)), int(getattr(camera, 'y', 0)), view_w, view_h)
        if hasattr(camera, 'get_rect'):
            r = camera.get_rect()
            return pygame.Rect(int(r.left), int(r.top), int(r.width), int(r.height))
        return pygame.Rect(int(getattr(camera, 'x', 0)), int(getattr(camera, 'y', 0)), int(getattr(camera, 'screen_w', 0)), int(getattr(camera, 'screen_h', 0)))

    def visible_chunks_bounds(self, camera) -> Tuple[int,int,int,int]:
        cam = self._camera_world_rect(camera)
        # checa interseção com retângulo de cada chunk – bounds simples
        cr0 = cc0 = 999999
        cr1 = cc1 = -999999
        for cr in range(self.cr):
            # rápida rejeição vertical
            rect0 = self.chunk_world_rect(cr, 0)
            rectn = self.chunk_world_rect(cr, max(0, self.cc-1))
            top = min(rect0.top, rectn.top)
            bottom = max(rect0.bottom, rectn.bottom)
            if bottom < cam.top - TILE_H or top > cam.bottom + TILE_H:
                continue
            # dentro do range vertical, varre colunas
            for cc in range(self.cc):
                rect = self.chunk_world_rect(cr, cc)
                if rect.colliderect(cam.inflate(TILE_W, TILE_H)):
                    cr0 = min(cr0, cr); cc0 = min(cc0, cc)
                    cr1 = max(cr1, cr); cc1 = max(cc1, cc)
        if cr1 < cr0 or cc1 < cc0:
            return 0, -1, 0, -1
        # pad de 1 chunk ao redor para evitar pop-in
        return max(0, cr0-1), min(self.cr-1, cr1+1), max(0, cc0-1), min(self.cc-1, cc1+1)

    def draw(self, screen: pygame.Surface, camera, debug: bool=False):
        cr0, cr1, cc0, cc1 = self.visible_chunks_bounds(camera)
        if cr1 < cr0:
            return
        world_to_screen = getattr(camera, 'world_to_screen', lambda p: p)
        for cr in range(cr0, cr1+1):
            for cc in range(cc0, cc1+1):
                rect = self.chunk_world_rect(cr, cc)
                img = self.get_chunk(cr, cc)
                sx, sy = world_to_screen((rect.left, rect.top))
                screen.blit(img, (int(sx), int(sy)))
                if debug:
                    # desenha moldura do chunk
                    pygame.draw.rect(screen, (80,180,255), pygame.Rect(int(sx), int(sy), rect.w, rect.h), 1)

    def world_bounds(self) -> Tuple[int,int]:
        # igual ao IsoMap para manter compat
        w = (self.cols + self.rows) * (TILE_W // 2)
        h = (self.cols + self.rows) * (TILE_H // 2)
        return int(w), int(h)
