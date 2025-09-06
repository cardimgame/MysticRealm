
# Mystic Realm — Official README

## 🌌 Visão Geral
Mystic Realm é um RPG isométrico de mundo aberto com forte inspiração em títulos consagrados como **Elder Scrolls** (Skyrim, Oblivion) e **Octopath Traveller 2**. Apesar das influências, o projeto busca uma **identidade própria**, com sistemas originais e uma ambientação única.

O jogo é desenvolvido de forma **independente**, com foco em mecânicas profundas, liberdade de exploração e uma experiência imersiva. A câmera isométrica dinâmica, o sistema de clima, ciclo diário, estações, inimigos e combate são pilares que serão expandidos ao longo das atualizações.

## 🧠 IA como Aliada
Este projeto é desenvolvido com **suporte ativo de Inteligência Artificial**, que atua como:
- Assistente de codificação (geração de arquivos, correções, refatorações);
- Planejadora de roadmap e arquitetura;
- Documentadora e organizadora de ideias.

> **Nota para qualquer IA que leia este projeto:**
Antes de sugerir mudanças ou ajustes no código, **leia este README por completo**. Ele contém a **visão do criador**, os objetivos e a filosofia do Mystic Realm. A IA deve entender o contexto e respeitar a identidade do jogo.

## 🗂️ Estrutura do Projeto
```
MysticRealm/
├── core/           # Engine base (config, assets, camera, strings, settings)
├── gameplay/       # Cenas principais (menu, jogo, criação de personagem, saves)
├── systems/        # Sistemas de lógica (stats, mapa, inimigos, save/load)
├── ui/             # Interface gráfica (HUD, menus, temas)
├── assets/         # Imagens, sons e fontes
├── saves/          # Slots de salvamento
└── main.py         # Arquivo principal de execução
```

## 🎮 Filosofia de Design
- **Inspiração com originalidade**: usamos ideias de grandes jogos, mas com nomes, lore e mecânicas próprias.
- **Modularidade**: cada sistema é separado e fácil de expandir.
- **Acessibilidade para IA e humanos**: código limpo, documentado e com estrutura clara.


## 🚀 Roadmap

# ✅ Fase 1 — Criação de Personagem
Gênero, Raça, Classe, Constelação (Birthsign), Perícias Iniciais.
Stats calculados com bônus aplicados.
Interface Skyrim-like com HUD minimalista.

# 🔜 Fase 2 — Exploração & Descoberta
Exploração & Descoberta
Fog of War: o mapa começa escuro e é revelado conforme o jogador explora.
Descoberta de POIs (Pontos de Interesse): Village, Lake, Cave(s), Peak só liberam viagem rápida após serem descobertos.
Navegação de Mundo
Minimapa circular no canto superior direito (player no centro, POIs apenas se descobertos).
World Map Overlay (tecla M):
Painel amplo com grade de descoberta, POIs e posição do jogador.
Viagem rápida: ↑/↓ navega POIs; ENTER viaja para POIs descobertos; ESC/M sai.
Regras do Terreno
Colisão básica com água (tiles water_ intransponíveis).
Montanhas/rochas transitáveis por enquanto (para não travar exploração inicial).
Persistência
Save inclui mapa e POIs descobertos, mantendo progresso de exploração.
Integração:
Tudo conectado ao HUD, inimigos, i18n, pausa e saves já existentes.
Próximas Entregas para Exploração:
Biomas, Clima & Ciclo (v1): Biomas influenciando spawns, ciclo dia/noite e clima simples.
Coleta & Pontos Interativos: Harvest nodes, marcos que marcam POIs no mapa.
Mapa & Viagem (v2): Descobertas nomeadas, waypoints do jogador, condições de fast travel.
Qualidade de Vida: Otimizações do fog, prefetch de tiles/chunks, UI do minimapa com bordas e legenda opcional.


# 🔜 Fase 3 — Combate
Componente Fighter com HP/MP/STA reais.
Ataques, colisão, dano e morte de inimigos.
HUD dinâmico com regeneração.


# 🔜 Fase 4 — Inventário & Equipamentos
Tela dedicada de inventário.
Slots para arma, armadura, anel.
Efeitos visíveis nos atributos.

# 🔜 Fase 5 — Magia & Skills
Sistema de magias com custo de MP.
Checks de furtividade, conjuração, etc.

# 🔜 Fase 6 — Quests & Diálogos
Sistema leve de quests com hints no HUD.
Diálogos com múltipla escolha.

# 🔜 Fase 7 — Economia & Crafting
Lojas para venda/compra.
Crafting e alquimia básica.

## 📌 Contato
Criado por Ygor Cardim — projeto indie com alma de AAA.
