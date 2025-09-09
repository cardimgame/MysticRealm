import re
import ast
from pathlib import Path
import subprocess

def fix_missing_module(path: Path, module_name: str) -> bool:
    """
    Tenta corrigir ModuleNotFoundError sugerindo instalação via pip.
    Retorna True se o módulo foi instalado com sucesso.
    """
    try:
        print(f"[AutoFix] Tentando instalar módulo ausente: {module_name}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", module_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[AutoFix] ✅ Módulo '{module_name}' instalado com sucesso.")
            return True
        else:
            print(f"[AutoFix] ❌ Falha ao instalar '{module_name}': {result.stderr}")
            return False
    except Exception as err:
        print(f"[AutoFix] ❌ Erro ao tentar instalar '{module_name}': {err}")
        return False

def fix_optional_typing(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return False

    changed = False
    patterns = [
        r"Optional\s*\(\s*dict\s*\)",
        r"Optional\s*<\s*dict\s*>",
        r"Optional\s+dict",
    ]
    for pat in patterns:
        if re.search(pat, content):
            content = re.sub(pat, "Optional[dict]", content)
            changed = True

    if "Optional[dict]" in content and "from typing import Optional" not in content:
        content = "from typing import Optional\n" + content
        changed = True

    if changed:
        try:
            path.write_text(content, encoding="utf-8")
            print(f"[AutoFix] Corrigido Optional em: {path}")
            return True
        except Exception:
            return False

    return False

def fix_argument_mismatch(path: Path, func_name: str, expected: int, received: int) -> bool:
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:
        return False

    changed = False
    lines = src.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == func_name:
            arg_count = len(node.args)
            if arg_count == received:
                line_no = node.lineno - 1
                line = lines[line_no]
                new_args = ", ".join(["None"] * expected)
                fixed_line = re.sub(rf"{func_name}\s*\((.*?)\)", f"{func_name}({new_args})", line)
                lines[line_no] = fixed_line
                changed = True

    if changed:
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            print(f"[AutoFix] Corrigido chamada de '{func_name}' em: {path}")
            return True
        except Exception:
            return False

    return False

def fix_none_attribute(path: Path, attr_name: str) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return False

    changed = False
    new_lines = []
    for i, line in enumerate(lines):
        if f".{attr_name}" in line and "None" not in line:
            match = re.search(r"(\w+)\." + re.escape(attr_name), line)
            if match:
                obj_name = match.group(1)
                indent = re.match(r"\s*", line).group(0)
                new_lines.append(f"{indent}if {obj_name} is not None:")
                new_lines.append(indent + "    " + line.strip())
                changed = True
                continue
        new_lines.append(line)

    if changed:
        try:
            path.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"[AutoFix] Verificação de None adicionada em: {path}")
            return True
        except Exception:
            return False

    return False
