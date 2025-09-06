# systems/weather.py — clima dependente de estação/parte do dia
import os, pygame, random

class Weather:
    def __init__(self, kind='rain', intensity=0.6, screen_size=(1280,720)):
        self.kind = kind
        self.intensity = max(0.0, min(1.0, float(intensity)))
        self.screen_w, self.screen_h = screen_size
        self.offset = 0.0; self.speed = 240
        self._frames = []; self._frame_idx = 0
        self._frame_timer = 0.0; self._frame_duration = 1.0/12.0
        self._load_assets()
    def resize(self, size):
        self.screen_w, self.screen_h = size
    def _load_assets(self):
        base = os.path.join('assets','weather')
        name = 'rain.png' if self.kind == 'rain' else 'snow.png'
        path = os.path.join(base, name)
        self._frames.clear()
        if os.path.exists(path):
            sheet = pygame.image.load(path); sheet = sheet.convert_alpha() if sheet.get_alpha() else sheet.convert()
            w,h=sheet.get_size(); sliced=False
            for n in range(8,1,-1):
                if w % n == 0:
                    fw=w//n; 
                    if fw>=8:
                        for i in range(n): self._frames.append(sheet.subsurface((i*fw,0,fw,h)))
                        sliced=True; break
            if not sliced: self._frames.append(sheet)
        else:
            surf = pygame.Surface((64,64), pygame.SRCALPHA)
            color = (180,180,255,120) if self.kind=='rain' else (255,255,255,120)
            for x in range(64): surf.set_at((x,(x*7)%64), color)
            self._frames.append(surf)
    def update(self, dt: float=0.0, season: str=None, day_part: str=None):
        if season:
            if season == 'inverno': self.kind='snow'
            elif season in ('primavera','outono','verão'): self.kind='rain'
        if len(self._frames)>1:
            self._frame_timer += dt
            if self._frame_timer >= self._frame_duration:
                self._frame_timer -= self._frame_duration
                self._frame_idx = (self._frame_idx + 1) % len(self._frames)
        self.offset = (self.offset + self.speed * dt) % 1024
    def draw(self, screen: pygame.Surface):
        if self.intensity <= 0.01: return
        frame = self._frames[self._frame_idx]
        fw,fh = frame.get_size(); ox=int(self.offset)%fw; oy=int(self.offset*0.6)%fh
        for y in range(-fh, self.screen_h+fh, fh):
            for x in range(-fw, self.screen_w+fw, fw):
                screen.blit(frame, (x-ox, y-oy))
        veil = pygame.Surface((self.screen_w,self.screen_h), pygame.SRCALPHA)
        veil.fill((0,0,0,int(40*self.intensity)))
        screen.blit(veil,(0,0))
