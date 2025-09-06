# auto_analysis_custom.py
from __future__ import annotations
import os, pathlib, ast, re, json, time, traceback
from collections import defaultdict

ROOT = pathlib.Path(".").resolve()
REPORT_FILE = ROOT / "CUSTOM_IA_ANALYSIS.json"

# Pastas e arquivos que queremos analisar
TARGET_PY_FOLDERS = ["core", "entitie", "gameplay", "systems", "ui"]
TARGET_ASSET_FOLDERS = ["assets"]
TARGET_ROOT_FILES = ["main.py"]

# ----------------------------
# Utilitários
# ----------------------------
def rel(p: pathlib.Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def walk_files(folder: pathlib.Path, exts=None):
    """Gera arquivos dentro de folder com extensão opcional"""
    for root, dirs, files in os.walk(folder):
        for f in files:
            p = pathlib.Path(root) / f
            if exts is None or p.suffix.lower() in exts:
                yield p

def read_text_safely(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def parse_python(src: str):
    try:
        return ast.parse(src)
    except Exception:
        return None

# ----------------------------
# Análise de arquivos Python
# ----------------------------
def analyze_py_file(path: pathlib.Path):
    src = read_text_safely(path)
    info = {
        "path": rel(path),
        "loc": src.count("\n") + 1,
        "classes": [],
        "functions": [],
        "imports": [],
        "uses_pygame": ("import pygame" in src) or ("from pygame" in src),
        "source_code": src
    }
    tree = parse_python(src)
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    info["imports"].append(n.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                info["imports"].append(node.module)
            elif isinstance(node, ast.ClassDef):
                cls = {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "methods": []
                }
                for sub in node.body:
                    if isinstance(sub, ast.FunctionDef):
                        cls["methods"].append({
                            "name": sub.name,
                            "args": [a.arg for a in sub.args.args],
                            "decorators": [ast.get_source_segment(src, d) for d in sub.decorator_list],
                            "start_line": sub.lineno,
                            "end_line": getattr(sub, "end_lineno", sub.lineno),
                            "draw_suspect": bool(re.search(
                                r"\b(self\.)?(vel|pos|state|on_ground|health|inventory)\s*=",
                                ast.get_source_segment(src, sub) or ""
                            ))
                        })
                info["classes"].append(cls)
            elif isinstance(node, ast.FunctionDef):
                info["functions"].append({
                    "name": node.name,
                    "args": [a.arg for a in node.args.args],
                    "decorators": [ast.get_source_segment(src, d) for d in node.decorator_list],
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "draw_suspect": bool(re.search(
                        r"\b(self\.)?(vel|pos|state|on_ground|health|inventory)\s*=",
                        ast.get_source_segment(src, node) or ""
                    )),
                    "is_update": node.name == "update",
                    "is_draw": node.name == "draw",
                    "is_handle_events": node.name == "handle_events"
                })
    return info

# ----------------------------
# Gera relatório completo
# ----------------------------
def generate_report():
    payload = {
        "timestamp": time.time(),
        "files": []
    }

    # Análise de pastas Python
    for folder in TARGET_PY_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for p in walk_files(folder_path, exts={".py"}):
                try:
                    info = analyze_py_file(p)
                except Exception:
                    info = {"path": rel(p), "error": traceback.format_exc()}
                payload["files"].append(info)

    # Arquivos Python na raiz
    for file_name in TARGET_ROOT_FILES:
        p = ROOT / file_name
        if p.exists():
            try:
                info = analyze_py_file(p)
            except Exception:
                info = {"path": rel(p), "error": traceback.format_exc()}
            payload["files"].append(info)

    # Pastas de assets (.png apenas nomes)
    for folder in TARGET_ASSET_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for p in walk_files(folder_path, exts={".png"}):
                payload["files"].append({
                    "path": rel(p),
                    "loc": 0,
                    "classes": [],
                    "functions": [],
                    "imports": [],
                    "uses_pygame": False,
                    "source_code": None  # Não lê código
                })

    # Salva JSON
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Relatório gerado: {REPORT_FILE}")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    generate_report()
