
import pygame
from core.settings import load_settings

_inited = False

def ensure_audio():
    global _inited
    if _inited:
        return
    try:
        pygame.mixer.init()
    except Exception:
        # ambiente sem áudio
        return
    _inited = True
    apply_settings()

def apply_settings():
    st = load_settings()
    vol = 0.0 if st.get('mute') else (st.get('volume', 100) / 100.0)
    try:
        pygame.mixer.music.set_volume(vol)
    except Exception:
        pass
