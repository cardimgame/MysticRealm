
from collections import Counter

class Inventory:
    def __init__(self):
        self.items = Counter()
        self.gold = 0
    def add(self, item: str, qty: int = 1): self.items[item] += qty
    def remove(self, item: str, qty: int = 1) -> bool:
        if self.items[item] >= qty:
            self.items[item] -= qty
            if self.items[item] <= 0:
                del self.items[item]
            return True
        return False
    def add_gold(self, amount: int): self.gold += amount
    def spend_gold(self, amount: int) -> bool:
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    def as_lines(self) -> list[str]:
        lines = [f"Ouro: {self.gold}"]
        for k, v in self.items.items():
            lines.append(f"{k} x{v}")
        return lines
