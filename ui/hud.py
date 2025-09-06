
# ui/hud.py — HUD with i18n for labels
import math, pygame
from ui.theme import get_font
from core.strings import t

BAR_W, BAR_H = 240, 12
BAR_GAP = 8

def _draw_bar(surface, x, y, w, h, value, max_value, color_fg=(200,60,60), color_bg=(40,40,50)):
    pygame.draw.rect(surface, color_bg, (x, y, w, h), border_radius=4)
    frac = 0.0 if max_value<=0 else max(0.0, min(1.0, float(value)/float(max_value)))
    fw = int(w * frac)
    if fw > 0:
        pygame.draw.rect(surface, color_fg, (x, y, fw, h), border_radius=4)
    pygame.draw.rect(surface, (20,20,26), (x, y, w, h), 1, border_radius=4)

def _compass(surface, rect, player_px, pois_world, camera):
    x, y, w, h = rect
    pygame.draw.rect(surface, (18,18,24), rect, border_radius=6)
    pygame.draw.rect(surface, (60,60,80), rect, 1, border_radius=6)
    cy = y + h//2
    pygame.draw.line(surface, (90,90,120), (x+8, cy), (x+w-8, cy), 1)
    for i, (wx, wy, label) in enumerate(pois_world or []):
        dx = wx - player_px[0]
        dy = wy - player_px[1]
        if dx == 0 and dy == 0:
            continue
        ang = math.atan2(dy, dx)  # -pi..pi
        tfrac = (ang + math.pi) / (2*math.pi)  # 0..1
        cx = x + int(tfrac * w)
        pygame.draw.line(surface, (240,220,160), (cx, y+4), (cx, y+h-4), 2)


def draw_hud(screen, *, lang: str, vitals, vitals_max, gold, compass_pois, player_px, camera, quest_hint: str | None = None):
    sw, sh = screen.get_size()
    font = get_font(20)
    panel = pygame.Surface((sw, 72), pygame.SRCALPHA)
    x0, y0 = 16, 12
    _draw_bar(panel, x0, y0, BAR_W, BAR_H, vitals.get('HP',0), vitals_max.get('HP',0), (200,60,60))
    _draw_bar(panel, x0, y0+BAR_H+BAR_GAP, BAR_W, BAR_H, vitals.get('STA',0), vitals_max.get('STA',0), (100,180,90))
    _draw_bar(panel, x0, y0+2*(BAR_H+BAR_GAP), BAR_W, BAR_H, vitals.get('MP',0), vitals_max.get('MP',0), (90,140,220))
    # Gold
    label_gold = t('hud.gold', lang)
    gsurf = font.render(f"{label_gold}: {int(gold)}", True, (230,230,230))
    panel.blit(gsurf, (x0, y0+3*(BAR_H+BAR_GAP)+6))
    # Compass (top center)
    cw = min(520, sw-360)
    ch = 18
    compass_rect = (sw//2 - cw//2, 10, cw, ch)
    _compass(panel, compass_rect, player_px, compass_pois, camera)
    # Quest hint (optional)
    if quest_hint:
        q = get_font(22).render(quest_hint, True, (240,220,160))
        panel.blit(q, q.get_rect(center=(sw//2, 48)))
    screen.blit(panel, (0,0))
