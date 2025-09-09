import pygame

class OverlapZone:
    """Apply a big positive bias to sprites inside the zone so they draw in front (roofs/fronts)."""
    def __init__(self, x, y, w, h, bias_front=100_000):
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))
        self.bias_front = int(bias_front)

    def apply(self, sprite, group):
        inside = self.rect.colliderect(sprite.rect)
        target = self.bias_front if inside else 0
        if getattr(sprite, 'layer_bias', 0) != target:
            sprite.layer_bias = target
            group.mark_dirty(sprite)
