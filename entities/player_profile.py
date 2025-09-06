# entities/player_profile.py
from dataclasses import dataclass

GENDERS = ["Masculino", "Feminino", "Não-binário"]
RACES   = ["Humano", "Elfo", "Anão", "Orc"]
CLASSES = ["Guerreiro", "Arqueiro", "Mago", "Ladino"]

@dataclass
class PlayerProfile:
    gender: str = GENDERS[0]
    race:   str = RACES[0]
    clazz:  str = CLASSES[0]
    # atributos derivados
    speed:  float = 240.0  # px/s (base)

def apply_derived_attributes(profile: PlayerProfile) -> PlayerProfile:
    base_speed = 240.0
    race_mod = {
        "Humano":   0,
        "Elfo":     +20,
        "Anão":     -20,
        "Orc":      -10,
    }
    class_mod = {
        "Guerreiro":  0,
        "Arqueiro":  +10,
        "Mago":       0,
        "Ladino":    +20,
    }
    profile.speed = base_speed + race_mod.get(profile.race, 0) + class_mod.get(profile.clazz, 0)
    return profile