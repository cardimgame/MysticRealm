# systems/dungeon.py — masmorra simples em grade
import random

def generate_dungeon(origin_col, origin_row, cols=12, rows=12):
    grid = [['rocky_01' for _ in range(cols)] for __ in range(rows)]
    # cavar alguns corredores e salas
    def carve_room(x,y,w,h):
        for r in range(y, min(rows, y+h)):
            for c in range(x, min(cols, x+w)):
                grid[r][c] = 'dirt_01'
    for _ in range(6):
        rw = random.randint(3,5); rh = random.randint(3,5)
        rx = random.randint(1, cols-rw-1); ry = random.randint(1, rows-rh-1)
        carve_room(rx, ry, rw, rh)
    # return absolute positions (in tile coords)
    return {
        'name':'dungeon',
        'grid': grid,
        'origin': (origin_col, origin_row)
    }
