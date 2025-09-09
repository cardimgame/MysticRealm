# gameplay/character/builder.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from gameplay.character import schema

GENDERS = ["Masculino", "Feminino"]

@dataclass
class BuildState:
    gender_idx: int = 0
    race_key: Optional[str] = None
    class_key: Optional[str] = None
    const_key: Optional[str] = None
    chosen_skills: List[str] = field(default_factory=list)
    name: str = ""

class Builder:
    def __init__(self):
        self.s = BuildState()

    def set_gender(self, idx: int):
        self.s.gender_idx = idx % len(GENDERS)

    def set_race(self, key: str):
        if key in schema.race_keys():
            self.s.race_key = key

    def set_class(self, key: str):
        if key in schema.class_keys():
            self.s.class_key = key

    def set_const(self, key: str):
        if key in schema.const_keys():
            self.s.const_key = key

    def toggle_skill(self, key: str, max_skills: int = 2):
        if key not in schema.skill_keys():
            return
        if key in self.s.chosen_skills:
            self.s.chosen_skills.remove(key)
        else:
            if len(self.s.chosen_skills) < max_skills:
                self.s.chosen_skills.append(key)

    def set_name(self, name: str):
        name = (name or '').strip()
        if len(name) <= 16:
            self.s.name = name

    def valid_gender(self) -> bool: return True
    def valid_race(self) -> bool: return self.s.race_key is not None
    def valid_class(self) -> bool: return self.s.class_key is not None
    def valid_const(self) -> bool: return self.s.const_key is not None
    def valid_skills(self, required: int = 2) -> bool: return len(self.s.chosen_skills) == required
    def valid_name(self) -> bool: return len(self.s.name.strip()) >= 1

    def snapshot(self) -> BuildState:
        return self.s
