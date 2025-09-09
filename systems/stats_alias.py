# systems/stats_alias.py — canonicalization for class keys
CLASS_ALIASES = {
 'Guerreiro': 'Warrior',
 'Arqueiro': 'Archer',
 'Arcanista': 'Arcanist',
 'Viajante': 'Wayfarer',
 'Sombra': 'Shade',
 'Guardiã(o)': 'Guardian',
 'Guardiã': 'Guardian',
 'Guardião': 'Guardian',
 'Guardiao': 'Guardian',
 # EN passthrough
 'Warrior': 'Warrior',
 'Archer': 'Archer',
 'Arcanist': 'Arcanist',
 'Wayfarer': 'Wayfarer',
 'Shade': 'Shade',
 'Guardian': 'Guardian',
}

def canon_class(name: str) -> str:
 return CLASS_ALIASES.get(name, name)
