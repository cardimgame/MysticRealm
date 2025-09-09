from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.config import SAVES_DIR

# Paths fixos dos 3 slots (slot1.json, slot2.json, slot3.json)
SLOTS: List[Path] = [SAVES_DIR / f"slot{i}.json" for i in (1, 2, 3)]


# =========================
# Helpers internos
# =========================
def _ensure_dir() -> None:
    """Garante que a pasta de saves exista."""
    SAVES_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_slot_index(slot_index: int) -> int:
    """
    Normaliza slot_index para índice 0..2.
    Aceita:
      - 1,2,3 (mais comum para UI)
      - 0,1,2 (estilo Python)
    """
    i = int(slot_index)
    if i in (1, 2, 3):
        return i - 1
    if i in (0, 1, 2):
        return i
    raise ValueError("slot_index deve ser 1..3 ou 0..2")


def get_slot_path(slot_index: int) -> Path:
    """Retorna o Path do arquivo JSON do slot informado."""
    return SLOTS[_normalize_slot_index(slot_index)]


# =========================
# API principal (compatível)
# =========================
def has_save_any() -> bool:
    """Retorna True se existir pelo menos um save em qualquer slot."""
    return any(p.exists() for p in SLOTS)


def list_saves() -> List[Path]:
    """
    Mantém compatibilidade: retorna apenas os Paths existentes.
    (Use list_saves_info() para metadados detalhados.)
    """
    return [p for p in SLOTS if p.exists()]


def load_game(path: Path | str) -> Optional[Dict[str, Any]]:
    """
    Carrega um save a partir de um caminho específico.
    Retorna dict ou None se não existir/corroper.
    Tenta fallback no .bak se o arquivo principal falhar.
    """
    p = Path(path)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # tenta backup
        backup = p.with_suffix(p.suffix + ".bak")
        try:
            if backup.exists():
                with backup.open("r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return None


def save_game(slot_index: int, data: Dict[str, Any]) -> bool:
    """
    Salva o conteúdo JSON no slot indicado.
    - Aceita slot 1..3 ou 0..2
    - Gravação atômica com .tmp + os.replace
    - Gera backup .bak do arquivo anterior (se existir)
    """
    tmp = None
    try:
        _ensure_dir()
        path = get_slot_path(slot_index)
        tmp = path.with_suffix(path.suffix + ".tmp")

        # Adiciona metadados mínimos (não quebra dados existentes)
        payload: Dict[str, Any]
        if isinstance(data, dict):
            payload = dict(data)  # cópia rasa
            payload.setdefault("_meta", {})
            # Descobre slot em 1..3 para metadado
            try:
                normalized = _normalize_slot_index(slot_index)
                slot_number = normalized + 1
            except Exception:
                # fallback (se vier valor estranho)
                slot_number = int(slot_index)
            payload["_meta"].update({
                "slot": slot_number,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "schema": "v1",
            })
        else:
            # Se não for dict, ainda assim salvar (mantendo compat)
            payload = {"data": data}

        # Escreve em arquivo temporário
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp.write_text(text, encoding="utf-8")

        # Cria backup do atual (se existir)
        if path.exists():
            backup = path.with_suffix(path.suffix + ".bak")
            try:
                os.replace(path, backup)  # move atômico no Windows
            except Exception:
                # Se falhar, seguimos; não é crítico pro save novo
                pass

        # Move tmp -> final (atômico)
        os.replace(tmp, path)
        return True
    except Exception:
        # limpeza do tmp se sobrar
        try:
            if tmp and Path(tmp).exists():
                Path(tmp).unlink()
        except Exception:
            pass
        return False


# =========================
# Utilitários adicionais
# =========================
def load_slot(slot_index: int) -> Optional[Dict[str, Any]]:
    """Atalho para carregar diretamente por índice de slot."""
    return load_game(get_slot_path(slot_index))


def delete_save(slot_index: int) -> bool:
    """Deleta o save do slot indicado (e seu .bak, se existir)."""
    try:
        p = get_slot_path(slot_index)
        if p.exists():
            p.unlink()
        b = p.with_suffix(p.suffix + ".bak")
        if b.exists():
            b.unlink()
        return True
    except Exception:
        return False


def wipe_all_saves() -> bool:
    """Remove todos os saves e backups dos 3 slots."""
    ok = True
    for i in (1, 2, 3):
        ok = delete_save(i) and ok
    return ok


def list_saves_info() -> List[Dict[str, Any]]:
    """
    Retorna metadados úteis de cada slot (1..3):
    - exists, path, size_bytes, modified, modified_ts
    - summary: campos comuns se presentes (player_name, level, location, playtime_seconds)
    - corrupted: True se falhou leitura do JSON
    """
    info: List[Dict[str, Any]] = []
    for slot_number, p in enumerate(SLOTS, start=1):
        exists = p.exists()
        row: Dict[str, Any] = {"slot": slot_number, "path": p, "exists": exists}
        if exists:
            try:
                st = p.stat()
                row["size_bytes"] = st.st_size
                row["modified_ts"] = st.st_mtime
                row["modified"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
                # leitura leve para summary
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                row["summary"] = {
                    "player_name": (data.get("player", {}) or {}).get("name") or data.get("player_name"),
                    "level": (data.get("player", {}) or {}).get("level") or data.get("level"),
                    "location": data.get("location") or data.get("zone"),
                    "playtime_seconds": data.get("playtime_seconds") or data.get("play_time"),
                }
            except Exception:
                row["corrupted"] = True
        info.append(row)
    return info
