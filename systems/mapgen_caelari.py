# systems/mapgen_caelari.py
from typing import List, Dict, Tuple

def _mk(rows, cols, fill=''):
    return [[fill for _ in range(cols)] for _ in range(rows)]

def generate(side='W', rows=256, cols=256, seed=22051):
    """Gera camadas com tokens (placeholders). side='W' ou 'E'."""
    import random, math
    rng = random.Random(seed)
    GRASS='grass'; SAND='sand'; WATER='water'; PATH='path'; SHORE='shore'; SNOW='snow'
    ground = _mk(rows, cols, GRASS)

    # WEST: costa em C nas ~32 colunas
    if side.upper().startswith('W'):
        cx, cy = rows//2, 20
        def insideC(r,c):
            # duas elipses menos um buraco central para formar um C
            from math import pow
            def elp(x,y,cx,cy,rx,ry):
                return ((x-cy)**2)/max(1,rx*rx) + ((y-cx)**2)/max(1,ry*ry) <= 1.0
            E1 = elp(c,r,cx,cy,int(cols*0.16),int(rows*0.42))
            E2 = elp(c,r,cx-8,cy+8,int(cols*0.18),int(rows*0.36))
            H  = elp(c,r,cx,cy+10,int(cols*0.10),int(rows*0.22))
            return (E1 or E2) and not H and c<32
        for r in range(rows):
            for c in range(cols):
                if insideC(r,c): ground[r][c]=WATER
        # ring de areia
        for r in range(rows):
            for c in range(0,34):
                if ground[r][c]==GRASS:
                    near=False
                    for dr in (-1,0,1):
                        for dc in (-1,0,1):
                            rr,cc=r+dr,c+dc
                            if 0<=rr<rows and 0<=cc<cols and ground[rr][cc]==WATER:
                                near=True;break
                    if near: ground[r][c]=SAND
    else:
        # EAST: um pouco de areia aleatória perto do oeste
        for r in range(rows):
            for c in range(2,10):
                if rng.random()<0.03 and ground[r][c]==GRASS:
                    ground[r][c]=SAND

    # PATH meandro até o funil leste
    overlay_path = _mk(rows, cols, '')
    pr, pc = max(2, rows//2 - 10), 4
    gate_cs = cols-14
    steps = rows*6
    while steps>0 and pc<gate_cs:
        steps-=1
        if 0<=pr<rows and 0<=pc<cols and ground[pr][pc]!=WATER:
            overlay_path[pr][pc]=PATH
        if rng.random()<0.90: pc+=1
        if rng.random()<0.45: pr+=rng.choice((-1,1))
        pr=max(1,min(rows-2,pr))
    for r in range(rows//2-2, rows//2+3):
        for c in range(gate_cs, cols-1):
            if ground[r][c]!=WATER: overlay_path[r][c]=PATH

    # SHORE espuma
    overlay_shore = _mk(rows, cols, '')
    for r in range(rows):
        for c in range(cols):
            if ground[r][c] in (GRASS,SAND):
                near=False
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        rr,cc=r+dr,c+dc
                        if 0<=rr<rows and 0<=cc<cols and ground[rr][cc]==WATER:
                            near=True;break
                if near: overlay_shore[r][c]=SHORE

    # NEVE ao norte-leste
    overlay_snow = _mk(rows, cols, '')
    band_top = int(rows*0.40)
    for r in range(band_top):
        for c in range(int(cols*0.48), cols):
            if ground[r][c]!=WATER and rng.random()<0.24:
                overlay_snow[r][c]=SNOW

    # DEBUG overlay (cidade/vilas/pois)
    overlay_debug = _mk(rows, cols, '')
    city_r, city_c = rows//2, int(cols*0.30)
    overlay_debug[city_r][city_c] = 'dbg_city'
    villages = [
        (rows//2 + 10, int(cols*0.18)),
        (rows//2 - 6,  int(cols*0.46)),
        (rows//2 + 12, int(cols*0.62)),
        (band_top//2 + 6, int(cols*0.70)),
    ]
    for (vr,vc) in villages: overlay_debug[vr][vc]='dbg_village'
    overlay_debug[int(rows*0.22)][int(cols*0.80)]='dbg_cave'
    overlay_debug[int(rows*0.12)][int(cols*0.86)]='dbg_dungeon'

    layers = [
        {'name':'ground','grid':ground},
        {'name':'overlay_path','grid':overlay_path},
        {'name':'overlay_shore','grid':overlay_shore},
        {'name':'overlay_snow','grid':overlay_snow},
        {'name':'overlay_debug','grid':overlay_debug},
    ]
    return layers
