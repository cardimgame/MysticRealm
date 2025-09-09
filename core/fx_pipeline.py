import pygame

class PostFX:
    """Cheap screen-space FX suitable for pygame Surfaces (CPU-bound).
    - Uses downsample + smoothscale up to simulate blur cheaply.
    - Rebuilds blur at ~30Hz to save CPU.
    """
    def __init__(self, quality: str = 'half'):
        self.size = None
        self.low = None
        self.blur = None
        self.acc = 0.0
        self.set_quality(quality)

    def set_quality(self, quality: str):
        factor = 2 if str(quality) == 'half' else 4
        self._div = factor

    def _ensure(self, size):
        if size != self.size:
            self.size = size
            w, h = size
            self.low = pygame.Surface((max(1, w//self._div), max(1, h//self._div))).convert_alpha()
            self.blur = pygame.Surface(size, pygame.SRCALPHA)

    def make_blur(self, screen: pygame.Surface, dt: float):
        self.acc += dt
        if self.acc < (1.0/30.0):
            return self.blur
        self.acc = 0.0
        self._ensure(screen.get_size())
        low = pygame.transform.smoothscale(screen, self.low.get_size())
        self.blur = pygame.transform.smoothscale(low, self.size)
        return self.blur

    def apply_bloom(self, screen: pygame.Surface, blur: pygame.Surface, amount: int = 70):
        if not blur: return
        veil = blur.copy(); veil.set_alpha(int(amount))
        screen.blit(veil, (0,0), special_flags=pygame.BLEND_RGBA_ADD)

    def apply_dof(self, screen: pygame.Surface, blur: pygame.Surface,
                  focus_y: float = 0.58, band: float = 0.24, alpha: int = 120):
        if not blur: return
        w, h = screen.get_size()
        y = int(h * focus_y)
        b = int(h * band * 0.5)
        top = pygame.Rect(0, 0, w, max(0, y - b))
        bot = pygame.Rect(0, min(h, y + b), w, h - (y + b))
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        if top.height: veil.blit(blur, top, area=top)
        if bot.height: veil.blit(blur, bot, area=bot)
        veil.set_alpha(int(alpha))
        screen.blit(veil, (0,0))
