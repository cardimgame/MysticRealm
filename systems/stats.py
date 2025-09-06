
from dataclasses import dataclass

RACES = {
    'Norther': {'desc': 'Humanos das terras geladas; robustos, resistentes ao frio.', 'bonus': {'STR': 1, 'VIT': 2}},
    'Valen':   {'desc': 'Elfos de bosques antigos; olhos aguçados e passos leves.',    'bonus': {'DEX': 2, 'WIS': 1}},
    'Durn':    {'desc': 'Anões das montanhas; mestres da forja e da tenacidade.',      'bonus': {'STR': 2, 'END': 1}},
    'Serathi': {'desc': 'Felinos nômades; instintos rápidos e furtivos.',               'bonus': {'DEX': 2, 'INT': 1}},
    'Aetherborn': {'desc':'Nascidos do éter; afinidade natural com magia.',              'bonus': {'INT': 2, 'WIS': 1}},
}

CLASSES = {
    'Guerreiro':  {'desc': 'Combate corpo a corpo, armaduras pesadas.', 'base': {'STR': 4, 'DEX': 1, 'INT': 0, 'VIT': 3, 'END': 3, 'WIS': 0}},
    'Arqueiro':   {'desc': 'Ataques à distância, mobilidade.',           'base': {'STR': 1, 'DEX': 4, 'INT': 0, 'VIT': 2, 'END': 2, 'WIS': 0}},
    'Arcanista':  {'desc': 'Magos eruditos, poder místico.',             'base': {'STR': 0, 'DEX': 0, 'INT': 5, 'VIT': 1, 'END': 1, 'WIS': 3}},
    'Viajante':   {'desc': 'Versátil, sobrevivência e comércio.',        'base': {'STR': 1, 'DEX': 2, 'INT': 1, 'VIT': 2, 'END': 2, 'WIS': 1}},
    'Sombra':     {'desc': 'Furtividade e assassinato.',                 'base': {'STR': 1, 'DEX': 5, 'INT': 1, 'VIT': 1, 'END': 2, 'WIS': 0}},
    'Guardiã(o)': {'desc': 'Proteção, fé e disciplina.',                 'base': {'STR': 3, 'DEX': 0, 'INT': 1, 'VIT': 3, 'END': 3, 'WIS': 2}},
}

@dataclass
class Stats:
    STR: int; DEX: int; INT: int; VIT: int; END: int; WIS: int
    HP: int; MP: int; STA: int

def build_stats(race: str, clazz: str) -> 'Stats':
    base = CLASSES.get(clazz, CLASSES['Guerreiro'])['base'].copy()
    bonus = RACES.get(race, RACES['Norther'])['bonus']
    for k, v in bonus.items():
        base[k] = base.get(k, 0) + v
    STR, DEX, INT = base['STR'], base['DEX'], base['INT']
    VIT, END, WIS = base['VIT'], base['END'], base['WIS']
    hp = 30 + VIT * 8
    mp = 10 + INT * 8 + WIS * 4
    sta = 20 + END * 6
    return Stats(STR, DEX, INT, VIT, END, WIS, hp, mp, sta)
