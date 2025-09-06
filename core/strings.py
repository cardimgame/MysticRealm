
# core/strings.py — i18n (en-US, pt-BR) centralized UI strings (Zip 3)
from typing import Any

STRINGS: dict[str, dict[str, Any]] = {
  'en-US': {
    # MAIN & CAMPAIGN
    'main.continue': 'Continue',
    'main.options': ['Campaign', 'Settings', 'Exit'],
    'campaign.options': ['New Game', 'Load Game', 'Delete Game', 'Back'],

    # SAVES
    'saves.title.load': 'Load Game',
    'saves.title.delete': 'Delete Game',
    'saves.title.save': 'Save Game',
    'saves.hint': 'ENTER to select • ESC back',
    'saves.slot': 'Slot',
    'saves.available': 'Available',
    'saves.empty': 'Empty',
    'saves.deleted': 'Deleted.',

    # SETTINGS
    'settings.title': 'Settings',
    'settings.back': 'Back',
    'settings.show_missing': 'Show Missing Overlay',
    'settings.resolution': 'Resolution',
    'settings.fps': 'FPS',
    'settings.audio': 'Audio',
    'settings.mute': 'Mute',
    'settings.difficulty': 'Difficulty',
    'settings.controls': 'Controls',
    'settings.language': 'Language',
    'settings.lang.values': ['English (US)', 'Português (Brasil)'],

    # CHARACTER CREATION (Phase 1 Complete)
    'char.titles': ['Choose Gender', 'Choose Race', 'Choose Class', 'Choose Constellation', 'Choose 2 Skills', 'Enter Name', 'Summary'],
    'char.hint.nav': '←/→ to change • ENTER confirm • ESC back',
    'char.hint.name': 'ENTER confirm • ESC back',
    'char.hint.summary': 'ENTER to start • ESC to edit',
    'char.hint.skills': '←/→ navigate • ENTER select/deselect • Need 2 skills • ESC back',

    # CONSTELLATIONS (Birthsigns)
    'signs.list': ['The Blade','The Veil','The Aether','The Beast'],
    'signs.desc.The Blade': '+10% physical damage, +1 STR',
    'signs.desc.The Veil': '+10% stealth, +1 DEX',
    'signs.desc.The Aether': '+10% Magicka, +1 INT',
    'signs.desc.The Beast': '+10% Stamina, +1 END',

    # SKILLS (names)
    'skills.list': ['One-Handed','Two-Handed','Archery','Stealth','Conjuration','Elemental Magic'],

    # HUD / UI
    'hud.gold': 'Gold',
    'ui.inventory': 'INVENTORY',
    'ui.paused': 'PAUSED (ESC to resume)',

    # PAUSE TABS
    'pause.tabs': ['Continue', 'Inventory', 'Settings', 'Save', 'Exit to Menu'],

    # DEBUG
    'debug.missing': 'ATTENTION: missing assets (using placeholders):',

    # RACES (by id from systems.stats)
    'race.Norther.name': 'Norther',
    'race.Norther.desc': 'Humans from frozen lands; robust and cold-resistant.',
    'race.Valen.name': 'Valen',
    'race.Valen.desc': 'Elves of ancient woods; keen eyes and light steps.',
    'race.Durn.name': 'Durn',
    'race.Durn.desc': 'Dwarves of the mountains; masters of forge and tenacity.',
    'race.Serathi.name': 'Serathi',
    'race.Serathi.desc': 'Nomadic felines; quick instincts and stealth.',
    'race.Aetherborn.name': 'Aetherborn',
    'race.Aetherborn.desc': 'Born of aether; natural affinity with magic.',

    # CLASSES (keys from systems.stats)
    'class.Guerreiro.name': 'Warrior',
    'class.Guerreiro.desc': 'Melee combat, heavy armor.',
    'class.Arqueiro.name': 'Archer',
    'class.Arqueiro.desc': 'Ranged attacks, mobility.',
    'class.Arcanista.name': 'Arcanist',
    'class.Arcanista.desc': 'Scholarly mages, mystic power.',
    'class.Viajante.name': 'Wayfarer',
    'class.Viajante.desc': 'Versatile, survival and trade.',
    'class.Sombra.name': 'Shade',
    'class.Sombra.desc': 'Stealth and assassination.',
    'class.Guardiã(o).name': 'Guardian',
    'class.Guardiã(o).desc': 'Protection, faith and discipline.',

    # Compass POIs
    'poi.village': 'Village',
    'poi.lake': 'Lake',
    'poi.cave': 'Cave',
    'poi.peak': 'Peak',
  },

  'pt-BR': {
    # MAIN & CAMPAIGN
    'main.continue': 'Continuar',
    'main.options': ['Campanha', 'Configurações', 'Sair'],
    'campaign.options': ['Novo Jogo', 'Carregar Jogo', 'Excluir Jogo', 'Voltar'],

    # SAVES
    'saves.title.load': 'Carregar Jogo',
    'saves.title.delete': 'Excluir Jogo',
    'saves.title.save': 'Salvar Jogo',
    'saves.hint': 'ENTER seleciona • ESC volta',
    'saves.slot': 'Slot',
    'saves.available': 'Disponível',
    'saves.empty': 'Vazio',
    'saves.deleted': 'Excluído.',

    # SETTINGS
    'settings.title': 'Configurações',
    'settings.back': 'Voltar',
    'settings.show_missing': 'Mostrar Aviso de Assets Ausentes',
    'settings.resolution': 'Resolução',
    'settings.fps': 'FPS',
    'settings.audio': 'Áudio',
    'settings.mute': 'Mudo',
    'settings.difficulty': 'Dificuldade',
    'settings.controls': 'Controles',
    'settings.language': 'Idioma',
    'settings.lang.values': ['English (US)', 'Português (Brasil)'],

    # CHARACTER CREATION
    'char.titles': ['Escolher Gênero', 'Escolher Raça', 'Escolher Classe', 'Escolher Constelação', 'Escolher 2 Perícias', 'Digitar Nome', 'Resumo'],
    'char.hint.nav': '←/→ altera • ENTER confirma • ESC volta',
    'char.hint.name': 'ENTER confirma • ESC volta',
    'char.hint.summary': 'ENTER inicia • ESC edita',
    'char.hint.skills': '←/→ navega • ENTER seleciona/deseleciona • Precisa de 2 • ESC volta',

    # CONSTELLATIONS
    'signs.list': ['A Lâmina','O Véu','O Éter','A Fera'],
    'signs.desc.The Blade': '+10% dano físico, +1 FOR',
    'signs.desc.The Veil': '+10% furtividade, +1 DES',
    'signs.desc.The Aether': '+10% Magicka, +1 INT',
    'signs.desc.The Beast': '+10% Stamina, +1 VIG',

    # SKILLS
    'skills.list': ['Uma Mão','Duas Mãos','Arco','Furtividade','Conjuração','Magia Elemental'],

    # HUD / UI
    'hud.gold': 'Ouro',
    'ui.inventory': 'INVENTÁRIO',
    'ui.paused': 'PAUSADO (ESC para continuar)',

    # PAUSE TABS
    'pause.tabs': ['Continuar', 'Inventário', 'Configurações', 'Salvar', 'Sair para o Menu'],

    # DEBUG
    'debug.missing': 'ATENÇÃO: assets ausentes (usando placeholders):',

    # RACES
    'race.Norther.name': 'Norther',
    'race.Norther.desc': 'Humanos das terras geladas; robustos e resistentes ao frio.',
    'race.Valen.name': 'Valen',
    'race.Valen.desc': 'Elfos de bosques antigos; olhos aguçados e passos leves.',
    'race.Durn.name': 'Durn',
    'race.Durn.desc': 'Anões das montanhas; mestres da forja e da tenacidade.',
    'race.Serathi.name': 'Serathi',
    'race.Serathi.desc': 'Felinos nômades; instintos rápidos e furtivos.',
    'race.Aetherborn.name': 'Aetherborn',
    'race.Aetherborn.desc': 'Nascidos do éter; afinidade natural com magia.',

    # CLASSES
    'class.Guerreiro.name': 'Guerreiro',
    'class.Guerreiro.desc': 'Combate corpo a corpo, armaduras pesadas.',
    'class.Arqueiro.name': 'Arqueiro',
    'class.Arqueiro.desc': 'Ataques à distância, mobilidade.',
    'class.Arcanista.name': 'Arcanista',
    'class.Arcanista.desc': 'Magos eruditos, poder místico.',
    'class.Viajante.name': 'Viajante',
    'class.Viajante.desc': 'Versátil, sobrevivência e comércio.',
    'class.Sombra.name': 'Sombra',
    'class.Sombra.desc': 'Furtividade e assassinato.',
    'class.Guardiã(o).name': 'Guardiã(o)',
    'class.Guardiã(o).desc': 'Proteção, fé e disciplina.',

    # Compass POIs
    'poi.village': 'Vila',
    'poi.lake': 'Lago',
    'poi.cave': 'Caverna',
    'poi.peak': 'Pico',
  }
}

def t(key: str, lang: str = 'en-US'):
    return STRINGS.get(lang, {}).get(key, STRINGS.get('en-US', {}).get(key, key))
