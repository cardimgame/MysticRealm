# core/camera_v2.py
import math, pygame

class CameraV2:
    def __init__(self, screen_w, screen_h, world_w, world_h, *, zoom=1.0):
        self.screen_w, self.screen_h = int(screen_w), int(screen_h)
        self.world_w, self.world_h = int(world_w), int(world_h)
        self.x = 0.0
        self.y = 0.0
        self.zoom = float(zoom)
        # Parâmetros padrão (Exploração):
        self.dead_frac = (0.38, 0.30)  # fração da tela (w,h)
        self.lookahead_t = 0.25        # segundos de antecipação
        self.smooth = 0.12             # amortecimento (0.10~0.16)
        # Shake (opcional)
        self.shake_amp = 0.0
        self.shake_t = 0.0
        self.shake_decay = 4.0

    def set_profile(self, *, dead_frac=None, lookahead_t=None, smooth=None, zoom=None):
        if dead_frac is not None: self.dead_frac = dead_frac
        if lookahead_t is not None: self.lookahead_t = lookahead_t
        if smooth is not None: self.smooth = smooth
        if zoom is not None: self.zoom = zoom

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.screen_w, self.screen_h)

    def world_to_screen(self, pos):
        wx, wy = float(pos[0]), float(pos[1])
        sx = int((wx - self.x) * self.zoom)
        sy = int((wy - self.y) * self.zoom)
        return sx, sy

    def center_on(self, world_pt):
        cx, cy = world_pt
        self.x = cx - (self.screen_w / (2*self.zoom))
        self.y = cy - (self.screen_h / (2*self.zoom))
        self._clamp()

    def apply_shake(self, power: float = 8.0):
        self.shake_amp = max(self.shake_amp, power)
        self.shake_t = 0.0

    def update(self, dt: float, *, focus_px, vel_px):
        # 1) foco com lookahead
        fx, fy = focus_px
        vx, vy = vel_px
        fx += vx * self.lookahead_t
        fy += vy * self.lookahead_t

        # 2) deadzone central
        dz_w = self.screen_w * self.dead_frac[0]
        dz_h = self.screen_h * self.dead_frac[1]
        dz = pygame.Rect(
            int(self.x + (self.screen_w - dz_w)/2),
            int(self.y + (self.screen_h - dz_h)/2),
            int(dz_w), int(dz_h)
        )
        dest_x, dest_y = self.x, self.y
        if fx < dz.left:   dest_x -= (dz.left - fx)
        if fx > dz.right:  dest_x += (fx - dz.right)
        if fy < dz.top:    dest_y -= (dz.top - fy)
        if fy > dz.bottom: dest_y += (fy - dz.bottom)

        # 3) suavização exponencial (lerp amortecido)
        self.x += (dest_x - self.x) * self.smooth
        self.y += (dest_y - self.y) * self.smooth

        # 4) shake (decay)
        if self.shake_amp > 0.01:
            self.shake_t += dt
            amp = self.shake_amp * math.exp(-self.shake_decay * self.shake_t)
            ox = math.sin(self.shake_t*62.0) * amp
            oy = math.cos(self.shake_t*50.0) * amp
            self.x += ox; self.y += oy
            if amp < 0.1: self.shake_amp = 0.0

        # 5) limites
        self._clamp()

    def _clamp(self):
        view_w = self.screen_w / self.zoom
        view_h = self.screen_h / self.zoom
        max_x = max(0.0, self.world_w - view_w)
        max_y = max(0.0, self.world_h - view_h)
        self.x = min(max(0.0, self.x), max_x)
        self.y = min(max(0.0, self.y), max_y)

    def on_resize(self, w: int, h: int):
        self.screen_w, self.screen_h = int(w), int(h)
        self._clamp()