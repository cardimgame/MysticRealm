# systems/npc.py — NPCs e lojista
import pygame
from systems.items import ITEMS
from systems.inventory import Inventory

class Shopkeeper(pygame.sprite.Sprite):
    def __init__(self, x, y, stock=None):
        super().__init__()
        self.image = pygame.Surface((32,48), pygame.SRCALPHA)
        self.image.fill((200,170,90))
        pygame.draw.rect(self.image, (0,0,0), (0,0,32,48), 1)
        self.rect = self.image.get_rect(topleft=(x,y))
        self.stock = stock or {'potion_hp':5,'potion_sta':5,'potion_mp':5}
        self.prices = {k: 10 for k in self.stock}

    def open_shop(self, player_inventory: Inventory):
        # compra simples pela primeira opção disponível
        for item_id, qty in list(self.stock.items()):
            price = self.prices.get(item_id, 10)
            if player_inventory.can_afford(price) and qty>0:
                # auto-compra 1 item (placeholder de UI)
                player_inventory.spend(price)
                player_inventory.add(item_id, 1)
                self.stock[item_id] -= 1
                return f'Comprou {item_id} por {price} gold.'
        return 'Loja sem transação.'
