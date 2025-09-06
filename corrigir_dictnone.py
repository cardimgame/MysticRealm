import os
import re

# Caminho raiz do projeto
ROOT = "C:/Users/ygcardim/OneDrive - DPDHL/Python_Projects/Projects_Games/MysticRealm"

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    # Corrigir Optional[dict] -> Optional[dict]
    if "Optional[dict]" in content:
        content = content.replace("Optional[dict]", "Optional[dict]")
        changed = True

    # Se usou Optional e não tem import, adiciona
    if "Optional[dict]" in content and "from typing import Optional" not in content:
        content = "from typing import Optional\n" + content
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Corrigido: {path}")

# Percorrer todos os arquivos .py
for root, dirs, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".py"):
            process_file(os.path.join(root, file))
