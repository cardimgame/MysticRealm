# systems/items.py — itens e loot por classe
from typing import Dict, List

ITEMS: Dict[str, dict] = {
    # armas
    'sword_basic':   {'type':'weapon','class':'Guerreiro','atk':5},
    'axe_basic':     {'type':'weapon','class':'Guardião','atk':6},
    'bow_basic':     {'type':'weapon','class':'Arqueiro','atk':5},
    'dagger_basic':  {'type':'weapon','class':'Sombra','atk':4},
    'staff_basic':   {'type':'weapon','class':'Arcanista','atk':3,'mag':4},
    # armaduras
    'armor_light':   {'type':'armor','class':'Viajante','def':3},
    'armor_heavy':   {'type':'armor','class':'Guardião','def':6},
    'robe_basic':    {'type':'armor','class':'Arcanista','def':1,'mag':2},
    # consumíveis
    'potion_hp':     {'type':'consumable','hp':20},
    'potion_sta':    {'type':'consumable','sta':15},
    'potion_mp':     {'type':'consumable','mp':15},
}

LOOT_BY_CLASS: Dict[str, List[str]] = {
    'Guerreiro': ['sword_basic','armor_light','potion_hp'],
    'Arcanista': ['staff_basic','robe_basic','potion_mp'],
    'Viajante':  ['armor_light','dagger_basic','potion_sta'],
    'Arqueiro':  ['bow_basic','armor_light','potion_hp'],
    'Sombra':    ['dagger_basic','armor_light','potion_sta'],
    'Trovador':  ['armor_light','potion_hp','potion_mp'],
    'Guardião':  ['axe_basic','armor_heavy','potion_hp'],
}
