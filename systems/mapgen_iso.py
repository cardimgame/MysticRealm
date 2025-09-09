# systems/mapgen_iso.py — compatibility wrapper to new Caelari generator
from __future__ import annotations
from typing import Tuple, Dict, Any
from systems.mapgen_caelari import generate as _generate

def generate_layers(rows: int = 256, cols: int = 256, seed: int = 22051, want_meta: bool = True, side: str = 'W'):
    """
    Backward-compatible signature used by old code:
      returns: (layers, pois, start_rc, props_rc[, meta])
    Internally uses systems.mapgen_caelari.generate (new).
    """
    layers = _generate(side=side, rows=rows, cols=cols, seed=seed)
    # Minimal/neutral POIs + start/meta (can be enriched later)
    pois: Dict[str, Any] = {}
    start_rc: Tuple[int,int] = (rows//2, int(cols*0.30))
    props_rc = []
    gate_r0, gate_r1 = (rows//2 - 2, rows//2 + 2)
    gate_east = {'rc_range': ((gate_r0, gate_r1), (cols - 10, cols - 2))}
    meta = {'gate_east': gate_east}
    if want_meta:
        return layers, pois, start_rc, props_rc, meta
    return layers, pois, start_rc, props_rc
