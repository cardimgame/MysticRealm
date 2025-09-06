
from dataclasses import dataclass

@dataclass
class Fighter:
    HP: int; STA: int; MP: int; STR: int; DEX: int; INT: int
    atk_cool: float = 0.0
    def alive(self) -> bool: return self.HP > 0
    def update(self, dt: float):
        if self.atk_cool > 0: self.atk_cool = max(0.0, self.atk_cool - dt)
    def try_attack(self, target: 'Fighter', style: str = 'melee') -> tuple[bool,int]:
        if self.atk_cool > 0: return False, 0
        dmg = 3
        if style == 'melee': dmg += self.STR // 2
        elif style == 'ranged': dmg += self.DEX // 2
        elif style == 'magic' and self.MP >= 5:
            dmg += self.INT // 2 + 3; self.MP -= 5
        target.HP = max(0, target.HP - dmg)
        self.atk_cool = 0.6
        return True, dmg
