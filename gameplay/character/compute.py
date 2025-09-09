# gameplay/character/compute.py
from __future__ import annotations
from typing import Dict
from gameplay.character import schema, builder as _b

ATTRS = ["STR","DEX","INT","CON"]

def _zero():
    return {k:0 for k in ATTRS}

def finalize(b: _b.BuildState) -> Dict:
    total = _zero()

    if b.race_key:
        for k,v in schema.race_info(b.race_key).attrs.items():
            total[k] = total.get(k,0) + int(v)
    if b.class_key:
        for k,v in schema.class_info(b.class_key).attrs.items():
            total[k] = total.get(k,0) + int(v)
    if b.const_key:
        for k,v in schema.const_info(b.const_key).bonus.items():
            total[k] = total.get(k,0) + int(v)
    for sk in (b.chosen_skills or []):
        for k,v in schema.skill_info(sk).bonus.items():
            total[k] = total.get(k,0) + int(v)

    # Bases por raça
    bases = schema.race_bases(b.race_key or '')

    # Derivados (base da raça + escalonamento simples)
    HP = bases.get('HP',50) + total.get('CON',0) * 8
    MP = bases.get('MP',30) + total.get('INT',0) * 8
    STA = bases.get('STA',50) + (total.get('CON',0)//2) * 6

    gender = _b.GENDERS[b.gender_idx]
    race_label = schema.race_label(b.race_key) if b.race_key else ''
    class_label = schema.class_label(b.class_key) if b.class_key else ''
    const_label = schema.const_label(b.const_key) if b.const_key else ''
    skills_labels = [schema.skill_label(s) for s in (b.chosen_skills or [])]

    profile = {
        'name': b.name.strip() or ('Aventureiro' if schema.current_lang().startswith('pt') else 'Adventurer'),
        'gender': gender,
        'race': race_label,
        'clazz': class_label,
        'sign': const_label,
        'skills': skills_labels,
        'stats': {
            'STR': total.get('STR',0), 'DEX': total.get('DEX',0), 'INT': total.get('INT',0), 'CON': total.get('CON',0),
            'HP': HP, 'MP': MP, 'STA': STA,
        }
    }
    return profile
