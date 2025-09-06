
import pygame

class Camera:
    def __init__(self, screen_width: int, screen_height: int, world_width: int = 4096, world_height: int = 4096):
        self.screen_w = int(screen_width)
        self.screen_h = int(screen_height)
        self.world_w = int(world_width)
        self.world_h = int(world_height)
        self.x = 0.0
        self.y = 0.0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.screen_w, self.screen_h)

    def world_to_screen(self, pos):
        x, y = pos
        return (int(x - self.x), int(y - self.y))

    def move_to(self, x: float, y: float):
        max_x = max(0, self.world_w - self.screen_w)
        max_y = max(0, self.world_h - self.screen_h)
        self.x = min(max(0, x), max_x)
        self.y = min(max(0, y), max_y)

    def center_on(self, world_pos: tuple[int, int]):
        self.move_to(world_pos[0] - self.screen_w // 2, world_pos[1] - self.screen_h // 2)

    def follow(self, target_rect: pygame.Rect, smooth: float = 0.12):
        tx, ty = target_rect.center
        goal_x = tx - self.screen_w // 2
        goal_y = ty - self.screen_h // 2
        self.move_to(self.x + (goal_x - self.x) * smooth, self.y + (goal_y - self.y) * smooth)

    def on_resize(self, w: int, h: int):
        self.screen_w, self.screen_h = int(w), int(h)
