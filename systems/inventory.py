# systems/inventory.py — inventário simples com ouro
from typing import Dict, List

class Inventory:
    def __init__(self):
        self.gold = 0
        self.items: Dict[str, int] = {}
        self.equipped: Dict[str, str] = {}  # slot->item_id
    def add(self, item_id: str, qty: int=1):
        self.items[item_id] = self.items.get(item_id,0) + qty
    def remove(self, item_id: str, qty: int=1):
        if self.items.get(item_id,0) >= qty:
            self.items[item_id] -= qty
            if self.items[item_id] <= 0: self.items.pop(item_id, None)
            return True
        return False
    def can_afford(self, amount: int) -> bool: return self.gold >= amount
    def spend(self, amount: int) -> bool:
        if self.gold >= amount: self.gold -= amount; return True
        return False
    def earn(self, amount: int): self.gold += amount
