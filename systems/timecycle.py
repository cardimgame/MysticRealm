# systems/timecycle.py — ciclo de tempo, períodos e estações
from dataclasses import dataclass
from core.config import SECONDS_PER_GAME_DAY

DAY_PARTS = [
    ('madrugada', 0.00, 0.20),
    ('manhã',      0.20, 0.40),
    ('tarde',      0.40, 0.70),
    ('fim_tarde',  0.70, 0.85),
    ('noite',      0.85, 1.00),
]
SEASONS = ['primavera','verão','outono','inverno']

@dataclass
class GameTime:
    day: int = 1
    hour: float = 8.0  # começa de manhã
    season_idx: int = 0  # primavera

class TimeManager:
    def __init__(self):
        self.t = GameTime()
        self.accum = 0.0
    def update(self, dt_real_seconds: float):
        # 10 min reais = 1 dia => SECONDS_PER_GAME_DAY segundos reais = 24h in-game
        self.accum += dt_real_seconds
        day_frac_inc = self.accum / SECONDS_PER_GAME_DAY
        if day_frac_inc <= 0: return
        self.accum = 0.0
        hours_inc = day_frac_inc * 24.0
        self.t.hour += hours_inc
        while self.t.hour >= 24.0:
            self.t.hour -= 24.0
            self.t.day += 1
            if (self.t.day % 30) == 1:  # a cada 30 dias muda estação
                self.t.season_idx = (self.t.season_idx + 1) % len(SEASONS)
    def current_day_part(self) -> str:
        frac = self.t.hour / 24.0
        for name, a, b in DAY_PARTS:
            if a <= frac < b: return name
        return 'noite'
    def current_season(self) -> str:
        return SEASONS[self.t.season_idx]
    def ambient_tint(self):
        # retorna um multiplicador de cor (r,g,b,alpha) conforme parte do dia
        part = self.current_day_part()
        if part == 'madrugada': return (120,120,160,60)
        if part == 'manhã':     return (255,255,255,0)
        if part == 'tarde':     return (255,255,255,0)
        if part == 'fim_tarde': return (255,200,160,30)
        return (80,80,120,80)
