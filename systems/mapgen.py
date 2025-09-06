# systems/mapgen.py — safe topdown biomes; returns tokens only (no assets)
import random
from math import hypot

def generate(cols=64, rows=64, seed=2025):
    rng = random.Random(seed)
    lake_c = (int(cols*0.30), int(rows*0.60))
    mount_c = (int(cols*0.75), int(rows*0.25))
    grid = [['' for _ in range(cols)] for __ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            dl = hypot(c-lake_c[0], r-lake_c[1])
            dm = hypot(c-mount_c[0], r-mount_c[1])
            if dl < 4.0:
                token = 'water_01'
            elif dl < 6.0:
                token = 'sand_01'
            else:
                h = dm - dl
                if h < -8:
                    token = 'grass_01'
                elif h < 6:
                    token = 'grass_01' if rng.random()<0.9 else 'path_01'
                elif h < 12:
                    token = 'rocky_01'
                else:
                    token = 'snow_01'
            grid[r][c] = token
    # light smoothing
    def smooth(g):
        rows=len(g); cols=len(g[0])
        out=[row[:] for row in g]
        for r in range(rows):
            for c in range(cols):
                cnt={}
                for rr in range(max(0,r-1), min(rows,r+2)):
                    for cc in range(max(0,c-1), min(cols,c+2)):
                        t=g[rr][cc]; cnt[t]=cnt.get(t,0)+1
                out[r][c] = max(cnt, key=cnt.get)
        return out
    grid = smooth(grid)
    return grid
