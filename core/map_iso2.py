# core/map_iso2.py
import pygame
from typing import Any
from core.iso_math2 import TILE_W, TILE_H, grid_to_screen
from core.tiles_placeholders2 import build_tile

class IsoTileSet2:
    """Ignora assets do disco; usa somente build_tile()"""
    def __init__(self):
        self.cache = {}
        print('[IsoTileSet2] placeholders only (no disk).')
    def get(self, token:str)->pygame.Surface:
        if token in self.cache: return self.cache[token]
        img = build_tile(token)
        self.cache[token]=img
        if len(self.cache)<=12:
            print('[IsoTileSet2] token', token)
        return img

class IsoMap2:
    def __init__(self, layers:list[dict[str,Any]], tileset:IsoTileSet2, origin=(0,0)):
        self.layers = layers
        self.tileset = tileset
        self.rows = len(layers[0]['grid']) if layers else 0
        self.cols = len(layers[0]['grid'][0]) if self.rows>0 else 0
        # Alinhamento igual ao seu esquema (x>=0)
        self.offset = ((self.rows-1)*(TILE_W//2), 0)
        self.origin = origin
    def world_bounds(self):
        w = (self.cols + self.rows) * (TILE_W//2)
        h = (self.cols + self.rows) * (TILE_H//2)
        return w,h
    def draw(self, screen:pygame.Surface, camera=None):
        # desenha tudo (simples); para 256x256 funciona bem com culling futuro
        ox, oy = self.offset
        for layer in self.layers:
            G = layer['grid']
            for r in range(self.rows):
                row = G[r]
                for c in range(self.cols):
                    t = row[c]
                    if not t: continue
                    x,y = grid_to_screen(r,c,(ox,oy))
                    if camera and hasattr(camera,'world_to_screen'):
                        x,y = camera.world_to_screen((x,y))
                    screen.blit(self.tileset.get(t),(int(x),int(y)))
