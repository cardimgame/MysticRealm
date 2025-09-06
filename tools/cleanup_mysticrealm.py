#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza e migração seguras do projeto Mystic Realm.

Recursos:
- DRY-RUN por padrão (não altera nem apaga nada).
- Backup .zip automático dos arquivos que serão alterados/removidos (desabilite com --no-backup).
- Checagem de referências (--check-refs) a módulos-alvo antes de excluir/migrar.
- Auto-fix opcional de imports/símbolos (--fix-imports) para migrar systems.savegame → systems.save_load.
- Pode falhar intencionalmente se houver referências remanescentes (--fail-on-ref), ideal para CI.

Uso:
  python tools/cleanup_mysticrealm.py --check-refs
  python tools/cleanup_mysticrealm.py --apply --check-refs --fix-imports --yes
  python tools/cleanup_mysticrealm.py --apply --include-legacy-ui --check-refs --fix-imports --yes
"""

from __future__ import annotations
import argparse
import ast
import io
import os
import re
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# --------------------------- Alvos e mapeamentos ------------------------------

# Arquivos que serão removidos (seguro)
CORE_TARGETS = [
    "systems/savegame.py",   # antigo 1-slot
    "ui/save_select.py",     # UI antiga de saves
]

# Menus legados (remover se passar --include-legacy-ui)
LEGACY_UI_TARGETS = [
    "ui/campaign_menu.py",
    "ui/character_creation.py",
    "ui/menu.py",
]

# Mapeamento de módulos para auto-fix de import
# - Valor None => sem substituto (apenas avisar/impedir; não removemos import automaticamente)
MODULE_MAP: Dict[str, Optional[str]] = {
    "systems.savegame": "systems.save_load",
    "ui.save_select": None,  # sem substituto direto
}

# Renomeação de símbolos ao migrar de systems.savegame -> systems.save_load
SYMBOL_MAP: Dict[str, Dict[str, str]] = {
    "systems.savegame": {
        # iguais mantidos explícitos:
        "save_game": "save_game",
        "load_game": "load_game",
        # renomeações:
        "delete_game": "delete_save",
        "has_save": "has_save_any",
    }
}

# Heurística de chamadas por alias (ex.: savegame.delete_game(...))
ALIAS_ATTR_RENAMES: Dict[str, List[Tuple[str, str]]] = {
    # alias → [(old_attr, new_attr), ...]
    # O alias será inferido quando houver import tipo "from systems import savegame"
    # ou "import systems.savegame as savegame"
    "savegame": [("delete_game", "delete_save"), ("has_save", "has_save_any")],
}

PRUNABLE_DIRS = ["ui", "systems"]


# ------------------------------- Utilitários ---------------------------------

def under(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def relpath(base: Path, p: Path) -> str:
    try:
        return str(p.resolve().relative_to(base.resolve()))
    except Exception:
        return str(p)


def list_py_files(base: Path) -> List[Path]:
    return [p for p in base.rglob("*.py") if p.is_file()]


def zip_backup(base: Path, files: List[Path]) -> Optional[Path]:
    if not files:
        return None
    ts = time.strftime("%Y%m%d_%H%M%S")
    zip_name = f"cleanup_backup_{ts}.zip"
    zip_path = base / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            arcname = relpath(base, f)
            z.write(f, arcname=arcname)
    return zip_path


def prune_empty_dirs(base: Path, rel_dirs: Iterable[str]) -> List[Path]:
    removed: List[Path] = []
    for rel in rel_dirs:
        d = (base / rel).resolve()
        if not (under(base, d) and d.exists() and d.is_dir()):
            continue
        # remove subpastas vazias
        for sub in sorted(d.rglob("*"), reverse=True):
            if sub.is_dir():
                try:
                    next(iter(sub.iterdir()))
                except StopIteration:
                    try:
                        sub.rmdir()
                        removed.append(sub)
                    except Exception:
                        pass
        # tenta a raiz listada
        try:
            next(iter(d.iterdir()))
        except StopIteration:
            try:
                d.rmdir()
                removed.append(d)
            except Exception:
                pass
    return removed


# -------------------------- Scanner de referências ----------------------------

@dataclass
class RefHit:
    file: Path
    line: int
    kind: str  # "import" | "from" | "text"
    detail: str

def scan_import_refs(base: Path, targets_modules: Iterable[str]) -> Dict[str, List[RefHit]]:
    """
    Varre todos os .py e retorna referências de import a cada módulo-alvo.
    Suporta:
      - import systems.savegame
      - import systems.savegame as sg
      - from systems import savegame
      - from systems.savegame import save_game
    """
    hits: Dict[str, List[RefHit]] = {m: [] for m in targets_modules}
    files = list_py_files(base)
    for f in files:
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(src, filename=str(f))
        except SyntaxError:
            continue

        class V(ast.NodeVisitor):
            def visit_Import(self, node: ast.Import):
                for alias in node.names:
                    name = alias.name  # ex.: "systems.savegame"
                    for mod in targets_modules:
                        if name == mod or name.startswith(mod + "."):
                            hits[mod].append(RefHit(f, node.lineno, "import", f"import {name}"))
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ast.ImportFrom):
                module = node.module or ""
                for mod in targets_modules:
                    # "from systems import savegame" (module='systems') com alias 'savegame'
                    if module == mod or module.startswith(mod + "."):
                        hits[mod].append(RefHit(f, node.lineno, "from", f"from {module} import ..."))
                    # caso especial: from systems import savegame
                    if module == "systems":
                        for alias in node.names:
                            if alias.name == "savegame" and mod == "systems.savegame":
                                hits[mod].append(RefHit(f, node.lineno, "from", "from systems import savegame"))
                self.generic_visit(node)

        V().visit(tree)

    return hits


def scan_text_refs_for_symbols(base: Path,
                               symbol_names: Iterable[str]) -> List[RefHit]:
    """
    Heurística simples: procura ocorrências textuais (não AST) de símbolos
    problemáticos (ex.: 'has_save(') para alertar.
    """
    pats = [re.compile(rf'\b{re.escape(name)}\s*\(') for name in symbol_names]
    hits: List[RefHit] = []
    for f in list_py_files(base):
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(src.splitlines(), start=1):
            for pat in pats:
                if pat.search(line):
                    hits.append(RefHit(f, i, "text", line.strip()))
    return hits


# ---------------------------- Rewriter de imports -----------------------------

class ImportRewriter(ast.NodeTransformer):
    """
    - Reescreve módulos conforme MODULE_MAP.
    - Renomeia símbolos conforme SYMBOL_MAP.
    - Preserva alias quando possível.
    """
    def __init__(self):
        super().__init__()
        self.touched = False
        self.detected_aliases: Dict[str, List[str]] = {}  # file-local; aqui não usamos

    def _map_module(self, name: str) -> Optional[str]:
        # name: 'systems.savegame' ou 'systems'
        if name in MODULE_MAP:
            return MODULE_MAP[name]
        # se for submódulo de alvo (ex.: systems.savegame.xyz) → substitui prefixo
        for old in MODULE_MAP:
            if name.startswith(old + ".") and MODULE_MAP[old]:
                new = MODULE_MAP[old] + name[len(old):]
                return new
        return name  # sem mudança

    def visit_Import(self, node: ast.Import):
        changed = False
        for alias in node.names:
            mapped = self._map_module(alias.name)
            if mapped is None:
                # sem substituto → deixamos como está (será tratado pela checagem)
                continue
            if mapped != alias.name:
                alias.name = mapped
                changed = True
        if changed:
            self.touched = True
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        orig_module = module
        mapped_module = self._map_module(module)

        # Caso especial: from systems import savegame
        if module == "systems":
            for alias in node.names:
                if alias.name == "savegame":
                    # transforma em: from systems import save_load as savegame
                    new_mod = MODULE_MAP.get("systems.savegame", None)
                    if new_mod and new_mod.startswith("systems."):
                        alias.name = new_mod.split(".", 1)[1]  # "save_load"
                        # preserva "as savegame" para compatibilidade
                        alias.asname = alias.asname or "savegame"
                        self.touched = True
            return node

        # from systems.savegame import X
        if mapped_module is None:
            # sem substituto → não reescreve; checagem bloqueará/exigirá intervenção
            return node

        # renomeia símbolos se houver mapeamento
        sym_map = SYMBOL_MAP.get("systems.savegame", {})
        if mapped_module != orig_module:
            node.module = mapped_module
            self.touched = True

        if orig_module == "systems.savegame":
            for a in node.names:
                if a.name in sym_map:
                    a.name = sym_map[a.name]
                    self.touched = True
        return node


def rewrite_file_imports(f: Path) -> Tuple[bool, str]:
    """
    Retorna (tocado, novo_conteudo) para f.
    """
    src = f.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(f))
    rewriter = ImportRewriter()
    new_tree = rewriter.visit(tree)
    if not rewriter.touched:
        return False, src
    ast.fix_missing_locations(new_tree)
    try:
        new_src = ast.unparse(new_tree)  # Python 3.9+
    except Exception:
        # fallback: mantém original (poderíamos implementar text-based se necessário)
        return False, src
    return True, new_src


def heuristic_alias_attr_fixes(src: str, aliases: Dict[str, List[Tuple[str, str]]]) -> str:
    """
    Troca simples de chamadas por alias: savegame.delete_game( → savegame.delete_save(
    """
    out = src
    for alias, pairs in aliases.items():
        for old_attr, new_attr in pairs:
            # evita substituir nomes maiores: usa \b e (
            pat = re.compile(rf'(\b{re.escape(alias)}\s*\.\s*){re.escape(old_attr)}\s*\(')
            out = pat.sub(rf'\1{new_attr}(', out)
    return out


def rewrite_imports_in_project(base: Path) -> List[Path]:
    """
    Reescreve imports/símbolos nos .py conforme mappings.
    Retorna lista de arquivos alterados.
    """
    changed: List[Path] = []
    for f in list_py_files(base):
        try:
            touched, new_src = rewrite_file_imports(f)
            if not touched:
                continue
            # Heurística adicional para chamadas por alias
            new_src2 = heuristic_alias_attr_fixes(new_src, ALIAS_ATTR_RENAMES)
            if new_src2 != new_src:
                touched = True
                new_src = new_src2
            if touched:
                f.write_text(new_src, encoding="utf-8")
                changed.append(f)
        except Exception:
            # não interrompe o fluxo por erro em um arquivo; apenas ignora
            continue
    return changed


# ------------------------------ Exclusão segura -------------------------------

def find_existing(base: Path, rel_paths: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for rel in rel_paths:
        p = (base / rel).resolve()
        if under(base, p) and p.exists() and p.is_file():
            out.append(p)
    return out


def delete_files(files: List[Path]) -> List[Path]:
    deleted: List[Path] = []
    for f in files:
        try:
            f.unlink()
            deleted.append(f)
        except FileNotFoundError:
            pass
    return deleted


# ----------------------------------- Main ------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Limpeza e migração seguras do Mystic Realm.")
    parser.add_argument("--apply", action="store_true", help="Aplica a limpeza/migração (por padrão é dry-run).")
    parser.add_argument("--yes", "-y", action="store_true", help="Confirma automaticamente (não interativo). Use com --apply.")
    parser.add_argument("--no-backup", action="store_true", help="Não criar backup .zip antes de alterar/remover.")
    parser.add_argument("--include-legacy-ui", action="store_true", help="Também remove menus antigos (ui/campaign_menu.py, ui/character_creation.py, ui/menu.py).")
    parser.add_argument("--check-refs", action="store_true", help="Checar referências a módulos-alvo antes de excluir.")
    parser.add_argument("--fix-imports", action="store_true", help="Tentar reescrever imports/símbolos automaticamente (savegame→save_load).")
    parser.add_argument("--fail-on-ref", action="store_true", help="Se encontrar referências, falha (exit code 3) e não exclui nada.")
    parser.add_argument("--keep-empty-dirs", action="store_true", help="Não tenta remover diretórios vazios após a limpeza.")
    parser.add_argument("--project-root", type=str, default=".", help="Caminho da raiz do projeto (default: .)")
    args = parser.parse_args(argv)

    base = Path(args.project_root).resolve()
    if not base.exists():
        print(f"[ERRO] Raiz do projeto não encontrada: {base}", file=sys.stderr)
        return 2

    targets = list(CORE_TARGETS)
    if args.include_legacy_ui:
        targets.extend(LEGACY_UI_TARGETS)

    existing = find_existing(base, targets)

    print("=== Mystic Realm — Limpeza/Migração Segura ===")
    print(f"Raiz: {base}")
    print("\nArquivos candidatos à remoção:")
    if existing:
        for p in existing:
            print(f"  • {relpath(base, p)}")
    else:
        print("  (nenhum arquivo alvo encontrado)")

    # ------------------ Checagem de referências ------------------
    ref_hits: Dict[str, List[RefHit]] = {}
    text_symbol_hits: List[RefHit] = []
    modules_to_check = [m for m in MODULE_MAP.keys() if m is not None]

    if args.check_refs:
        print("\nChecando referências de import nos .py ...")
        ref_hits = scan_import_refs(base, modules_to_check)
        any_refs = False
        for mod, hits in ref_hits.items():
            if hits:
                any_refs = True
                print(f"\nReferências a {mod}:")
                for h in hits:
                    print(f"  - {relpath(base, h.file)}:{h.line}  ({h.kind})  {h.detail}")
        # Heurística textual para símbolos sensíveis (apenas alerta)
        sym_names = set()
        for m, mp in SYMBOL_MAP.items():
            sym_names.update(mp.keys())
        text_symbol_hits = scan_text_refs_for_symbols(base, sym_names)
        if text_symbol_hits:
            print("\n(Alerta) Ocorrências textuais de símbolos sensíveis:")
            for h in text_symbol_hits:
                print(f"  - {relpath(base, h.file)}:{h.line}  {h.detail}")

        if args.fail_on_ref and any(hits for hits in ref_hits.values()):
            print("\n[ERRO] Existem referências a módulos que seriam removidos. Execute com --fix-imports, ou remova manualmente.", file=sys.stderr)
            return 3

    # ------------------ DRY-RUN: sem aplicar ------------------
    if not args.apply:
        print("\nModo: DRY-RUN (nada foi alterado/excluído).")
        print("Dicas:")
        print("  • Use --fix-imports junto de --apply para migrar imports automaticamente.")
        print("  • Use --include-legacy-ui para remover os menus antigos.")
        return 0

    # ------------------ Backup antes de alterar/excluir ------------------
    backup_files: List[Path] = []
    # incluir para backup: arquivos-alvo + todos .py (se for reescrever) tocados
    backup_files.extend(existing)
    if args.fix_imports:
        # backup de TODOS .py antes do rewriter (conservador)
        backup_files = sorted(set(backup_files + list_py_files(base)), key=lambda p: relpath(base, p))
    backup_path = None
    if not args.no_backup and backup_files:
        try:
            backup_path = zip_backup(base, backup_files)
            if backup_path:
                print(f"\nBackup criado: {backup_path.name}")
        except Exception as ex:
            print(f"[AVISO] Falha ao criar backup (.zip): {ex}", file=sys.stderr)

    # ------------------ Auto-fix de imports (opcional) ------------------
    changed_files: List[Path] = []
    if args.fix_imports:
        print("\nReescrevendo imports/símbolos conforme mapeamentos ...")
        changed_files = rewrite_imports_in_project(base)
        if changed_files:
            print("Arquivos alterados:")
            for p in changed_files:
                print(f"  ✓ {relpath(base, p)}")
        else:
            print("Nenhum import precisou ser alterado.")

    # ------------------ Exclusão dos arquivos-alvo ------------------
    if existing:
        # Confirmação
        if not args.yes:
            resp = input("\nConfirma a exclusão dos arquivos listados? [y/N] ").strip().lower()
            if resp not in ("y", "yes", "s", "sim"):
                print("Operação cancelada.")
                return 0

        deleted = delete_files(existing)
        if deleted:
            print("\nArquivos excluídos:")
            for p in deleted:
                print(f"  ✓ {relpath(base, p)}")
        else:
            print("\nNenhum arquivo foi excluído (já não existiam?).")
    else:
        print("\nNenhum arquivo a excluir.")

    # ------------------ Remover diretórios vazios ------------------
    if not args.keep_empty_dirs:
        pruned = prune_empty_dirs(base, PRUNABLE_DIRS)
        if pruned:
            print("\nDiretórios vazios removidos:")
            for d in pruned:
                print(f"  - {relpath(base, d)}")

    print("\nConcluído.")
    if backup_path:
        print(f"Backup salvo em: {backup_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())