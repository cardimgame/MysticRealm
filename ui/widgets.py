import math, pygame
from core.asset import load_image_strict
from ui.theme import COLORS
class RightMenuList:
    def __init__(self, font: pygame.font.Font, *, arrow_path='ui/selection_arrow.png'):
        self.font = font
        self._t = 0.0
        self.arrow_img = load_image_strict(arrow_path)
        self._arrow_cache = {}
    def update(self, dt: float):
        self._t += dt
    def _get_arrow_for_height(self, h: int):
        if not self.arrow_img:
            return None
        key = int(h)
        if key not in self._arrow_cache:
            w = int(h * 0.9)
            self._arrow_cache[key] = pygame.transform.smoothscale(self.arrow_img, (w, h))
        return self._arrow_cache[key]
    def draw(self, screen: pygame.Surface, options, selected: int, x_frac=0.82, y_frac=0.35, gap=56, color_sel=COLORS['menu_sel'], color_norm=COLORS['menu_item']):
        sw, sh = screen.get_size()
        x = int(sw * x_frac)
        y = int(sh * y_frac)
        bob = int(3 * math.sin(self._t * 5.0))
        for i, text in enumerate(options):
            col = color_sel if i == selected else color_norm
            surf = self.font.render(text, True, col)
            rect = surf.get_rect(topright=(x, y))
            screen.blit(surf, rect)
            if i == selected:
                ah = int(self.font.get_height() * 0.8)
                arrow = self._get_arrow_for_height(ah)
                if arrow:
                    arect = arrow.get_rect(midright=(rect.left - 14, rect.centery + bob))
                    screen.blit(arrow, arect)
                else:
                    mid = (rect.left - 12, rect.centery + bob)
                    pts = [(mid[0]-12, mid[1]-10), (mid[0]-12, mid[1]+10), (mid[0], mid[1])]
                    pygame.draw.polygon(screen, (240,220,160), pts)
            y += gap
