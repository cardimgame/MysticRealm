
from __future__ import annotations
import os, pygame
from typing import Optional, List, Dict

ASSETS_ROOT = os.path.join('assets','tiles')
PREFIX_TO_SUBDIR: Dict[str, str] = {
    'tree_': os.path.join(ASSETS_ROOT,'trees'),
    'rock_': os.path.join(ASSETS_ROOT,'props'),
    'log_': os.path.join(ASSETS_ROOT,'props'),
    'bush_': os.path.join(ASSETS_ROOT,'props'),
    'flower_': os.path.join(ASSETS_ROOT,'props'),
    'fence_': os.path.join(ASSETS_ROOT,'props'),
    'sign_': os.path.join(ASSETS_ROOT,'props'),
    'house_': os.path.join(ASSETS_ROOT,'village'),
}
_IMAGE_CACHE: Dict[str, 'pygame.Surface'] = {}

def _guess_subdir_for_key(key: str) -> Optional[str]:
    k = key.lower()
    for p, sub in PREFIX_TO_SUBDIR.items():
        if k.startswith(p): return sub
    return None

def load_prop_image(key: str) -> 'pygame.Surface':
    if key in _IMAGE_CACHE: return _IMAGE_CACHE[key]
    sub = _guess_subdir_for_key(key)
    surf = None
    if sub:
        for ext in ('.png','.jpg','.jpeg'):
            path = os.path.join(sub, key + ext)
            if os.path.exists(path):
                img = pygame.image.load(path)
                surf = img.convert_alpha() if img.get_alpha() else img.convert()
                break
    if surf is None:
        surf = pygame.Surface((64,64), pygame.SRCALPHA)
        surf.fill((255,0,255,120))
        try:
            f = pygame.font.SysFont('arial', 12)
            surf.blit(f.render(key[:10], True, (0,0,0)), (4,4))
        except Exception: pass
    _IMAGE_CACHE[key] = surf
    return surf

class PropSprite(pygame.sprite.Sprite):
    def __init__(self, key: str, x: int, y: int, collidable: bool=True):
        super().__init__()
        self.key = key
        self.image: 'pygame.Surface' = load_prop_image(key)
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))
        self.collidable = bool(collidable)
    def draw(self, screen: 'pygame.Surface', camera):
        screen.blit(self.image, camera.world_to_screen(self.rect.topleft))

class PropsManager:
    def __init__(self):
        self.all = pygame.sprite.Group()
        self.collidable_props = pygame.sprite.Group()
    def clear(self):
        self.all.empty(); self.collidable_props.empty()
    def add_prop(self, key: str, x: int, y: int, collidable: bool=True):
        sp = PropSprite(key, x, y, collidable)
        self.all.add(sp)
        if sp.collidable: self.collidable_props.add(sp)
    def add_props_from_list(self, items: List[Dict]):
        for it in items or []:
            self.add_prop(it.get('key','unknown'), it.get('x',0), it.get('y',0), it.get('collidable',True))
    def draw(self, screen: 'pygame.Surface', camera, sort_by_y: bool=False):
        sprites = sorted(self.all.sprites(), key=lambda s: s.rect.bottom) if sort_by_y else self.all.sprites()
        for s in sprites: s.draw(screen, camera)
