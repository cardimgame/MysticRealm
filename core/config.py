"""
core/config.py
Config centralizado, sem imports internos do projeto (apenas stdlib).

- Detecta PROJECT_ROOT de forma robusta a partir deste arquivo.
- Expõe aliases compatíveis (SAVE_DIR, SAVES_DIR, ASSETS_DIR, PROJECT_DIR, ROOT_DIR).
- Garante a criação das pastas críticas (assets, data, saves, logs).
"""

from pathlib import Path

# ==== Raiz do projeto (MysticRealm/) ====
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
PROJECT_DIR: Path  = PROJECT_ROOT            # alias de compatibilidade
ROOT_DIR: Path     = PROJECT_ROOT            # alias opcional

# ==== Caminhos ====
ASSETS_PATH: Path  = PROJECT_ROOT / "assets"
ASSETS_DIR: Path   = ASSETS_PATH             # alias de compatibilidade
DATA_DIR: Path     = PROJECT_ROOT / "data"
SAVE_PATH: Path    = PROJECT_ROOT / "saves"
SAVE_DIR: Path     = SAVE_PATH               # alias de compatibilidade
SAVES_DIR: Path    = SAVE_PATH               # alias (usado por modules antigos)
LOGS_DIR: Path     = PROJECT_ROOT / "logs"
SETTINGS_PATH: Path = PROJECT_ROOT / "settings.json"

# Cria pastas críticas automaticamente (idempotente)
for _p in (ASSETS_PATH, DATA_DIR, SAVE_PATH, LOGS_DIR):
    _p.mkdir(parents=True, exist_ok=True)

# ==== Tela e performance ====
# Use (1920, 1080) para alvo final. Mantive (1920, 1000) como você havia usado.
SCREEN_SIZE: tuple[int, int] = (1920, 1000)
FPS: int = 60
TARGET_FPS: int = FPS  # alias de compatibilidade

# ==== Grade isométrica ====
TILE_W: int = 128
TILE_H: int = 64

# ==== Player ====
PLAYER_SIZE: int = 96
PLAYER_SPEED_TILES: float = 3.8  # tiles por segundo

# ==== Defaults ====
DEFAULT_VOLUME: int = 100
DEFAULT_MUTE: bool = False
DEFAULT_DIFFICULTY: str = "normal"
DEFAULT_LANGUAGE: str = "en-US"
DEFAULT_SCALE_MODE: str = "fit"      # 'fit' ou 'cover'
DEFAULT_FX_QUALITY: str = "half"     # 'half' ou 'quarter'
DEFAULT_SHOW_MISSING: bool = False

# ==== Pós-FX (placeholders/toggles) ====
POSTFX_BLOOM: bool = True
POSTFX_DOF: bool   = True

# ==== Placeholders de compatibilidade (no-ops) ====
def dummy(*args, **kwargs):
    """Função placeholder para manter compatibilidade com imports antigos."""
    pass

def load_image(*args, **kwargs):
    return None

def save_game(*args, **kwargs):
    return None

def load_game(*args, **kwargs):
    return None

# ==== Exportações explícitas ====
__all__ = [
    # Raiz/caminhos
    "PROJECT_ROOT", "PROJECT_DIR", "ROOT_DIR",
    "SETTINGS_PATH", "ASSETS_PATH", "ASSETS_DIR", "DATA_DIR",
    "SAVE_PATH", "SAVE_DIR", "SAVES_DIR", "LOGS_DIR",
    # Tela/performance
    "SCREEN_SIZE", "FPS", "TARGET_FPS",
    # ISO & Player
    "TILE_W", "TILE_H", "PLAYER_SIZE", "PLAYER_SPEED_TILES",
    # Defaults
    "DEFAULT_VOLUME", "DEFAULT_MUTE", "DEFAULT_DIFFICULTY", "DEFAULT_LANGUAGE",
    "DEFAULT_SCALE_MODE", "DEFAULT_FX_QUALITY", "DEFAULT_SHOW_MISSING",
    # FX
    "POSTFX_BLOOM", "POSTFX_DOF",
    # Placeholders
    "dummy", "load_image", "save_game", "load_game",
]
