# core/ui_fx.py — versão sem NumPy/surfarray (compatível com Pygame puro)
import pygame, random, math

def blit_fit(screen: pygame.Surface, img: pygame.Surface):
    """Ajusta a imagem à tela com letterbox/pillarbox (sem cortar)."""
    sw, sh = screen.get_size()
    iw, ih = img.get_size()
    if iw == 0 or ih == 0:
        return
    scale = min(sw/iw, sh/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    x = (sw - nw)//2
    y = (sh - nh)//2
    if (nw, nh) != (iw, ih):
        img = pygame.transform.smoothscale(img, (nw, nh))
    screen.blit(img, (x, y))

def blit_cover(screen: pygame.Surface, img: pygame.Surface):
    """Cobre 100% da tela mantendo proporção (corta excessos)."""
    sw, sh = screen.get_size()
    iw, ih = img.get_size()
    if iw == 0 or ih == 0:
        return
    scale = max(sw/iw, sh/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    x = (sw - nw)//2
    y = (sh - nh)//2
    if (nw, nh) != (iw, ih):
        img = pygame.transform.smoothscale(img, (nw, nh))
    screen.blit(img, (x, y))

def make_vignette(size, strength=0.65, color=(0,0,0)):
    """
    Vinheta sem NumPy:
    - Gera um gradiente radial pequeno (256x256) e faz smoothscale para o tamanho da tela.
    - Criado só quando a resolução muda.
    """
    w, h = size
    base_n = 256
    g = pygame.Surface((base_n, base_n), pygame.SRCALPHA)
    cx = cy = base_n / 2.0
    maxd = math.hypot(cx, cy)
    for y in range(base_n):
        dy = (y - cy)
        for x in range(base_n):
            dx = (x - cx)
            d = math.hypot(dx, dy) / maxd  # 0 centro -> 1 borda
            a = int(255 * max(0.0, min(1.0, (d ** 1.5) * strength)))
            if a > 0:
                g.set_at((x, y), (0, 0, 0, a))
    tint_surf = pygame.Surface((base_n, base_n), pygame.SRCALPHA)
    tint_surf.fill((*color, 255))
    g.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if (w, h) != (base_n, base_n):
        g = pygame.transform.smoothscale(g, (w, h))
    return g

def make_grain(size, intensity=24, seed=None):
    """Granulado leve aleatório."""
    w, h = size
    rnd = random.Random(seed)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    dots = max(1, int(w*h*0.01))
    for _ in range(dots):
        x = rnd.randrange(0, w); y = rnd.randrange(0, h)
        g = 120 + rnd.randrange(-intensity, intensity+1)
        a = 16 + rnd.randrange(0, 24)
        surf.set_at((x, y), (g, g, g, a))
    return surf

def tint(screen: pygame.Surface, color=(32, 42, 64), alpha=40):
    """Véu colorido simples por cima da tela."""
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((*color, int(alpha)))
    screen.blit(veil, (0, 0))

# FX opcional de “chama” para hotspots (não obrigatório)

def _make_flame_disc(radius=160, color=(255,140,40), alpha=140):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    cx = cy = radius
    for r in range(radius, 0, -1):
        a = int(alpha * (r / radius) ** 1.8)
        pygame.draw.circle(surf, (*color, a), (cx, cy), r)
    return surf

class FlameFX:
    def __init__(self, hotspots=None, radius=160):
        self.hotspots = list(hotspots or [])
        self.base = _make_flame_disc(radius)
        self.t = 0.0
    def update(self, dt: float):
        self.t += dt
    def draw(self, screen: pygame.Surface):
        sw, sh = screen.get_size()
        for i, (xf, yf) in enumerate(self.hotspots):
            ox = int(8 * math.sin(self.t*3.0 + i*0.7))
            oy = int(6 * math.sin(self.t*2.2 + i*1.3))
            scale = 1.0 + 0.06 * math.sin(self.t*5.0 + i*0.9)
            w = int(self.base.get_width() * scale)
            h = int(self.base.get_height() * scale)
            layer = pygame.transform.smoothscale(self.base, (w, h))
            rect = layer.get_rect(center=(int(sw*xf) + ox, int(sh*yf) + oy))
            screen.blit(layer, rect, special_flags=pygame.BLEND_ADD)
