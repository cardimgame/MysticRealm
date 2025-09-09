# core/iso_math2.py
TILE_W = 128
TILE_H = 64

def grid_to_screen(ix:int, iy:int, origin=(0,0)):
    ox, oy = origin
    x = (iy - ix) * (TILE_W//2) + ox
    y = (iy + ix) * (TILE_H//2) + oy
    return x, y

def screen_to_grid(sx:float, sy:float, origin=(0,0)):
    ox, oy = origin
    x = sx - ox; y = sy - oy
    ix = (y/(TILE_H/2) - x/(TILE_W/2)) / 2.0
    iy = (y/(TILE_H/2) + x/(TILE_W/2)) / 2.0
    return int(round(ix)), int(round(iy))
