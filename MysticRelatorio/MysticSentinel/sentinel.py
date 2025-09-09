import traceback
import time
import os
import sys
import re
import json
from pathlib import Path
from MysticRelatorio.MysticSentinel.auto_fix import (
    fix_optional_typing,
    fix_argument_mismatch,
    fix_none_attribute,
    fix_missing_module
)
from MysticRelatorio.MysticSentinel.report import generate_report

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

CONFIG_PATH = Path(__file__).parent / "config.json"
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except Exception:
    CONFIG = {}

def color(text, code): return f"\033[{code}m{text}\033[0m"

def run_with_guard(main_func):
    try:
        main_func()
    except Exception as e:
        tb = traceback.format_exc()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = LOG_DIR / f"error_{timestamp}.txt"

        # Extrai caminho do arquivo onde ocorreu o erro
        lines = tb.splitlines()
        file_path = None
        for line in lines:
            if "File" in line and ", line" in line:
                parts = line.split('"')
                if len(parts) > 1:
                    file_path = Path(parts[1])
                    break

        fixed = False
        if CONFIG.get("auto_fix_enabled", True) and file_path and file_path.exists():
            # Correção de Optional
            if CONFIG.get("fixers", {}).get("optional_typing", True):
                fixed |= fix_optional_typing(file_path)

            # Correção de argumentos faltando
            if isinstance(e, TypeError) and "missing" in str(e):
                if CONFIG.get("fixers", {}).get("argument_mismatch", True):
                    match = re.search(r"(\w+)\(\) missing (\d+) required .*?argument", str(e))
                    if match:
                        func_name = match.group(1)
                        missing_args = int(match.group(2))
                        fixed |= fix_argument_mismatch(file_path, func_name, expected=missing_args + 1, received=missing_args)

            # Correção de atributo em NoneType
            if isinstance(e, AttributeError) and "'NoneType' object has no attribute" in str(e):
                if CONFIG.get("fixers", {}).get("none_attribute", True):
                    match = re.search(r"has no attribute '(\w+)'", str(e))
                    if match:
                        attr_name = match.group(1)
                        fixed |= fix_none_attribute(file_path, attr_name)
            # Correção de módulo ausente
            if isinstance(e, ModuleNotFoundError):
                if CONFIG.get("fixers", {}).get("missing_module", True):
                    match = re.search(r"No module named '(\w+)'", str(e))
                    if match:
                        module_name = match.group(1)
                        fixed |= fix_missing_module(file_path, module_name)

        # Gera relatório
        generate_report(
            error_type=type(e).__name__,
            message=str(e),
            traceback_str=tb,
            file_path=file_path if file_path else Path("desconhecido"),
            fixed=fixed
        )

        print("\n" + color("[MysticSentinel] ⚠️ Erro capturado", "94"))  # Azul
        print(color(f"Tipo: {type(e).__name__}", "91"))  # Vermelho
        print(color(f"Mensagem: {str(e)}", "91"))
        if file_path:
            print(color(f"Arquivo afetado: {file_path}", "90"))  # Cinza
        print(color(f"[AutoFix] {'✅ Correção automática aplicada' if fixed else '❌ Correção não aplicada'}", "92" if fixed else "93"))
        print(color("[MysticSentinel] O jogo foi encerrado com segurança.", "94"))
