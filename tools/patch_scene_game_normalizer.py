#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica um patch AST em gameplay/scene_game.py para NORMALIZAR o retorno de
`generate_layers(...)`, aceitando 3/4/5 itens sem quebrar a cena.

• Faz backup automático: gameplay/scene_game.py.bak
• Localiza a PRIMEIRA atribuição cujo valor é uma chamada a `generate_layers(...)`.
• Substitui essa atribuição por um bloco robusto de normalização.

Uso:
    python tools/patch_scene_game_normalizer.py [--project-root .]

Requisitos: Python 3.9+ (usa ast.unparse)
"""
from __future__ import annotations
import argparse
import ast
import shutil
from pathlib import Path

NORMALIZER_TEMPLATE = """
__mr_result__ = {CALL}
if not isinstance(__mr_result__, (list, tuple)):
    raise TypeError(f'generate_layers retornou {type(__mr_result__)}, esperado tuple/list')
if len(__mr_result__) == 3:
    layers, pois, start_rc = __mr_result__
    props_rc, meta = [], {{}}
elif len(__mr_result__) == 4:
    layers, pois, start_rc, props_rc = __mr_result__
    meta = {{}}
elif len(__mr_result__) >= 5:
    layers, pois, start_rc, props_rc, meta = __mr_result__[:5]
else:
    raise ValueError(f'generate_layers retornou {{len(__mr_result__)}} itens: {{__mr_result__}}')
""".strip()

class Finder(ast.NodeVisitor):
    def __init__(self):
        self.target_assign: ast.Assign | None = None
        self.call_src: str | None = None
        self.src_text: str = ''

    def set_src(self, text: str):
        self.src_text = text

    def visit_Assign(self, node: ast.Assign):
        # procura Assign cujo value é Call para nome/atributo com id 'generate_layers'
        val = node.value
        if isinstance(val, ast.Call):
            func_name = None
            if isinstance(val.func, ast.Name):
                func_name = val.func.id
            elif isinstance(val.func, ast.Attribute):
                func_name = val.func.attr
            if func_name == 'generate_layers' and self.target_assign is None:
                self.target_assign = node
                try:
                    self.call_src = ast.get_source_segment(self.src_text, val)
                except Exception:
                    # fallback: reconstrução simples (pode perder kwargs formatados)
                    args = []
                    for a in val.args:
                        args.append(ast.unparse(a))
                    for kw in val.keywords:
                        if kw.arg:
                            args.append(f"{kw.arg}={ast.unparse(kw.value)}")
                        else:
                            args.append(ast.unparse(kw.value))
                    self.call_src = f"generate_layers({', '.join(args)})"
        self.generic_visit(node)


def apply_patch(scene_path: Path) -> bool:
    src = scene_path.read_text(encoding='utf-8')
    tree = ast.parse(src)
    finder = Finder()
    finder.set_src(src)
    finder.visit(tree)
    if not finder.target_assign or not finder.call_src:
        print('[PATCH] Não encontrei uma atribuição com chamada a generate_layers(...).')
        return False

    # Cria bloco de normalização substituindo a Assign original
    norm_src = NORMALIZER_TEMPLATE.replace('{CALL}', finder.call_src)
    norm_nodes = ast.parse(norm_src).body

    class Replacer(ast.NodeTransformer):
        def visit_Assign(self, node: ast.Assign):
            if node is finder.target_assign:
                return norm_nodes
            return node

    new_tree = Replacer().visit(tree)
    ast.fix_missing_locations(new_tree)
    try:
        new_src = ast.unparse(new_tree)
    except Exception as ex:
        print('[PATCH] Falha ao gerar código (ast.unparse).', ex)
        return False

    # Backup e escrita
    backup = scene_path.with_suffix(scene_path.suffix + '.bak')
    shutil.copy(scene_path, backup)
    scene_path.write_text(new_src, encoding='utf-8')
    print('[PATCH] OK. Backup em:', backup)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.', help='Raiz do projeto (onde existe gameplay/scene_game.py)')
    args = ap.parse_args()
    root = Path(args.project_root).resolve()
    scene_path = root / 'gameplay' / 'scene_game.py'
    if not scene_path.exists():
        print('[PATCH] Arquivo não encontrado:', scene_path)
        return 2
    ok = apply_patch(scene_path)
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
