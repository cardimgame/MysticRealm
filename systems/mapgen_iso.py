# systems/mapgen_iso.py  (adicione abaixo do arquivo existente)
import random, math

def _carve_path(ground, a, b, token='path_01'):
    """Linha com jitter leve entre dois pontos (r,c) -> marca path no ground."""
    r0, c0 = a; r1, c1 = b
    r, c = r0, c0
    steps = max(abs(r1-r0), abs(c1-c0)) + 1
    for i in range(steps):
        t = 0 if steps<=1 else i/(steps-1)
        rr = int(round(r0 + (r1 - r0)*t + random.uniform(-0.2,0.2)))
        cc = int(round(c0 + (c1 - c0)*t + random.uniform(-0.2,0.2)))
        if 0 <= rr < len(ground) and 0 <= cc < len(ground[0]):
            ground[rr][cc] = token

def _ellipse_fill(ground, center, rx, ry, token):
    cr, cc = center
    rows, cols = len(ground), len(ground[0])
    for r in range(max(0, cr-ry-2), min(rows, cr+ry+3)):
        for c in range(max(0, cc-rx-2), min(cols, cc+rx+3)):
            x = (c - cc) / max(1.0, rx)
            y = (r - cr) / max(1.0, ry)
            if x*x + y*y <= 1.0:
                ground[r][c] = token

def _rect_centered(center, w, h):
    r0 = center[0] - h//2
    c0 = center[1] - w//2
    return (r0, c0, h, w)  # (top, left, height, width)

def _apply_mountain(ground, center, size):
    """Preenche uma caixa central com gradiente radial: snow->rocky->dirt."""
    rows, cols = len(ground), len(ground[0])
    mr, mc = center
    mh, mw = size
    r_top = max(0, mr - mh//2); r_bot = min(rows, mr + mh//2)
    c_left = max(0, mc - mw//2); c_right = min(cols, mc + mw//2)
    # raio para normalização
    rx = mw/2.0; ry = mh/2.0
    for r in range(r_top, r_bot):
        for c in range(c_left, c_right):
            x = (c - mc) / max(1.0, rx)
            y = (r - mr) / max(1.0, ry)
            d = math.sqrt(x*x + y*y)  # 0 centro → 1 borda
            # pequenas irregularidades
            d += random.uniform(-0.05, 0.05)
            if d <= 0.40:
                ground[r][c] = 'snow_01'
            elif d <= 0.70:
                ground[r][c] = 'rocky_01'
            elif d <= 0.85:
                ground[r][c] = 'dirt_01'
            # fora da borda, mantém o que já tinha

def generate_world(cols: int = 128, rows: int = 128, *, mountain_frac: float = 0.5, seed: int | None = None):
    """
    Mundo isométrico com:
    - Montanha central ocupando ~metade do mapa (fração do menor lado)
    - Lago + areia
    - Caminhos entre POIs
    Retorna: {'layers':[{'name':'ground','grid':...}], 'player_start':(r,c), 'pois':{...}}
    """
    rnd = random.Random(seed)
    rows = int(rows); cols = int(cols)
    # 1) base: grama
    ground = [['grass_01' for _ in range(cols)] for __ in range(rows)]

    # 2) lago (elipse) – lateral superior/esquerda
    lake_center = (rows//3, cols//3)
    rx, ry = max(6, cols//10), max(5, rows//10)
    _ellipse_fill(ground, lake_center, rx, ry, 'water_01')
    # faixa de areia ao redor (um pouco maior)
    _ellipse_fill(ground, lake_center, int(rx*1.15), int(ry*1.12), 'sand_01')

    # 3) montanha central (retângulo ~ metade do mapa)
    k = max(4, int(min(rows, cols) * mountain_frac))
    mh = min(rows-4, k)
    mw = min(cols-4, k)
    center = (rows//2, cols//2)
    _apply_mountain(ground, center, (mh, mw))
    mountain_bbox = _rect_centered(center, mw, mh)

    # 4) “vila” (solo): área de terra batida próxima à grama e longe do lago
    village_center = (rows - rows//4, cols//4*3)
    vh, vw = max(8, rows//10), max(10, cols//10)
    v_top = max(0, village_center[0] - vh//2)
    v_left = max(0, village_center[1] - vw//2)
    for r in range(v_top, min(rows, v_top+vh)):
        for c in range(v_left, min(cols, v_left+vw)):
            ground[r][c] = 'dirt_01'
    player_start = (village_center[0], village_center[1])

    # 5) “entradas” em encostas (para futura caverna/masmorra)
    # pontinhos nas laterais da montanha
    mr, mc = center
    cave_a = (mr, mc - mw//2 - 2)  # lado oeste (fora 2 tiles)
    cave_b = (mr + mh//4, mc + mw//2 + 2)  # lado leste-sul
    cave_entrances = [cave_a, cave_b]

    # 6) caminhos conectando pontos de interesse
    # vila -> montanha
    _carve_path(ground, player_start, (mr + mh//2, mc))
    # vila -> lago
    _carve_path(ground, player_start, lake_center)
    # lago -> montanha
    _carve_path(ground, lake_center, (mr, mc))
    # montanha -> caves
    for cv in cave_entrances:
        _carve_path(ground, (mr, mc), cv)

    layers = [{'name': 'ground', 'grid': ground}]
    pois = {
        'village_center': village_center,
        'mountain_bbox': mountain_bbox,  # (top, left, h, w)
        'lake_center': lake_center,
        'cave_entrances': cave_entrances,
    }
    return {'layers': layers, 'player_start': player_start, 'pois': pois}