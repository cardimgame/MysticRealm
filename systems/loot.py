
import random

BIOME_LOOT = {
    'grass': ['ervas', 'peles', 'carne_crua', 'seta'],
    'forest': ['madeira', 'fruta_silvestre', 'erva_rara', 'fungo'],
    'snow': ['gelo', 'peles_grossas', 'mineral_raro'],
    'water': ['peixe', 'alga', 'pérola'],
    'dirt': ['argila', 'minério_ferro', 'pedra'],
}

PRICES = {
    'ervas': 2, 'peles': 5, 'carne_crua': 3, 'seta': 1,
    'madeira': 2, 'fruta_silvestre': 1, 'erva_rara': 12, 'fungo': 3,
    'gelo': 1, 'peles_grossas': 7, 'mineral_raro': 20,
    'peixe': 4, 'alga': 2, 'pérola': 30,
    'argila': 2, 'minério_ferro': 8, 'pedra': 1,
}

def roll_loot(biome: str, rng: random.Random | None = None) -> list[str]:
    rnd = rng or random.Random()
    pool = BIOME_LOOT.get(biome, [])
    if not pool:
        return []
    n = rnd.randint(1, 3)
    return [rnd.choice(pool) for _ in range(n)]

