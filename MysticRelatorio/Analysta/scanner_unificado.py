import os
import ast
import re
import json
from datetime import datetime

# Caminho raiz do projeto
root_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(root_dir, "relatorio_unificado.json")

# Pastas e arquivos permitidos
allowed_folders = {"assets", "core", "entities", "gameplay", "saves", "systems", "tools", "ui"}
allowed_root_files = {"main.py"}
archived_files = {
    os.path.normpath(os.path.join(root_dir, "settings.json")),
    os.path.normpath(os.path.join(root_dir, "core", "config.py")),
    os.path.normpath(os.path.join(root_dir, "systems", "items.py")),
    os.path.normpath(os.path.join(root_dir, "tools", "cleanup_project.py")),
    os.path.normpath(os.path.join(root_dir, "tools", "migrate_grass_assets.py")),
    os.path.normpath(os.path.join(root_dir, "ui", "options_menu.py")),
    os.path.normpath(os.path.join(root_dir, "ui", "pause_menu.py")),
}

# Palavras-chave para classificação funcional
keywords = {
    "Player": ["player", "profile"],
    "NPCs": ["npc", "enemy", "mob"],
    "Quests": ["quest", "mission", "objective"],
    "Loot/Inventory": ["loot", "inventory", "item", "equip"],
    "Combat": ["combat", "attack", "skill", "damage"],
    "Maps/Tiles": ["map", "tile", "level", "world"],
    "Camera": ["camera"],
    "UI": ["ui", "menu", "hud", "widget"]
}

# Listar arquivos ativos
def list_active_files(root):
    files_list = []
    for dirpath, _, files in os.walk(root):
        folder_name = os.path.basename(dirpath)
        for file in files:
            full_path = os.path.normpath(os.path.join(dirpath, file))
            if full_path in archived_files:
                continue
            if folder_name in allowed_folders or (dirpath == root and file in allowed_root_files):
                if file.endswith(".py"):
                    files_list.append(full_path)
    return files_list

# Verificar sintaxe
def check_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        return "OK", tree, source
    except Exception as e:
        return f"Erro: {e}", None, ""

# Extrair definições
def extract_defs(tree):
    funcs, classes = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs.add(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
    return sorted(funcs), sorted(classes)

# Extrair imports
def extract_imports(tree):
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

# Detectar docstrings
def has_docstrings(source):
    return '"""' in source or "'''" in source

# Detectar testes
def has_tests(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            return True
    return False

# Classificar complexidade
def classify_complexity(funcs, classes):
    total = len(funcs) + len(classes)
    if total >= 8:
        return "Alta"
    elif total >= 4:
        return "Média"
    else:
        return "Baixa"

# Detectar módulo funcional
def detect_module(file_name):
    file_lower = file_name.lower()
    for tag, kw_list in keywords.items():
        if any(kw in file_lower for kw in kw_list):
            return tag
    return "Não classificado"

# Detectar tipo de arquivo
def detect_type(file_name):
    name = file_name.lower()
    if "controller" in name:
        return "Controlador"
    elif "manager" in name or "handler" in name:
        return "Gerenciador"
    elif "service" in name or "api" in name:
        return "Serviço"
    elif "model" in name or "schema" in name:
        return "Modelo"
    elif "menu" in name or "ui" in name:
        return "Interface"
    else:
        return "Script"

# Processar arquivos
active_files = list_active_files(root_dir)
imports_map = {file: set() for file in active_files}
report = []

for file_path in active_files:
    rel_path = os.path.relpath(file_path, root_dir)
    syntax_status, tree, source = check_syntax(file_path)
    funcs, classes, broken_imports = [], [], []
    imports = set()

    if tree:
        funcs, classes = extract_defs(tree)
        imports = extract_imports(tree)
        for mod in imports:
            mod_path = os.path.normpath(os.path.join(root_dir, *mod.split(".")) + ".py")
            if not os.path.exists(mod_path):
                broken_imports.append(mod)
            elif mod_path in imports_map:
                imports_map[mod_path].add(file_path)

    report.append({
        "arquivo": os.path.basename(file_path),
        "pasta": os.path.relpath(os.path.dirname(file_path), root_dir),
        "sintaxe": syntax_status,
        "importado_por": [os.path.relpath(i, root_dir) for i in imports_map[file_path]],
        "imports_quebrados": broken_imports,
        "funcoes": funcs,
        "classes": classes,
        "modulo_funcional": detect_module(file_path),
        "tipo_arquivo": detect_type(file_path),
        "complexidade": classify_complexity(funcs, classes),
        "possui_docstrings": has_docstrings(source),
        "possui_testes": has_tests(tree) if tree else False,
        "ultima_modificacao": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
        "sugestao_inteligente": "Manter" if syntax_status == "OK" else "Revisar"
    })

# Salvar JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"✅ Scanner unificado concluído. JSON gerado em: {output_file}")
