import pygame

class DepthGroup(pygame.sprite.LayeredUpdates):
    """Layered group where each sprite layer = rect.bottom + depth_offset + layer_bias.
    Use change_layer only on sprites whose Y changed or entered/exited overlap zones.
    """
    def __init__(self):
        super().__init__()
        self._dirty = set()

    def add(self, *sprites, layer=None):
        for sp in sprites:
            if not hasattr(sp, 'layer_bias'):
                sp.layer_bias = 0
            if not hasattr(sp, 'depth_offset'):
                sp.depth_offset = 0
            sp._layer = (sp.rect.bottom + sp.depth_offset + sp.layer_bias) if layer is None else layer
            super().add(sp, layer=sp._layer)

    def mark_dirty(self, sp):
        self._dirty.add(sp)

    def sync_layers(self):
        if not self._dirty:
            return
        for sp in list(self._dirty):
            new_layer = sp.rect.bottom + sp.depth_offset + sp.layer_bias
            if self.get_layer_of_sprite(sp) != new_layer:
                self.change_layer(sp, new_layer)
            self._dirty.discard(sp)

    def draw_sorted(self, screen, camera, clip_rect=None):
        self.sync_layers()
        for layer in sorted(self.layers()):
            for sp in self.get_sprites_from_layer(layer):
                if clip_rect and not sp.rect.colliderect(clip_rect):
                    continue
                screen.blit(sp.image, camera.world_to_screen(sp.rect.topleft) if hasattr(camera,'world_to_screen') else camera.aplicar(sp))
