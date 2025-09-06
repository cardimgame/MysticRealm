
from pathlib import Path

FPS: int = 60
SCREEN_SIZE = (1280, 720)

TILE_W: int = 64
TILE_H: int = 32

PLAYER_SIZE: int = 128
PLAYER_SPEED_TILES: float = 3.0
PLAYER_SPEED: float = 220.0

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / 'assets'
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
SAVES_DIR = BASE_DIR / 'saves'
SAVES_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH = BASE_DIR / 'settings.json'

DEFAULT_ASSET_SUBFOLDERS = [
    ASSETS_DIR / 'ground',
    ASSETS_DIR / 'ui',
    ASSETS_DIR / 'player',
    ASSETS_DIR / 'actors',
]
for d in DEFAULT_ASSET_SUBFOLDERS: d.mkdir(parents=True, exist_ok=True)
