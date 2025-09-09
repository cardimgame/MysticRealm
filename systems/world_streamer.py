# systems/world_streamer.py — v2 (min-compat return type)
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any

from core.map_iso2 import IsoTileSet2
from core.iso_chunked import IsoChunkedMap, ChunkSpec
import systems.mapgen_caelari as mapgen

@dataclass
class Region:
    id: str
    size: Tuple[int,int]
    seed: int
    neighbors: Dict[str, str]
    origin: Tuple[int,int] = (0,0)
    side: str = 'W'

@dataclass
class LoadedRegion:
    region: Region
    cmap: IsoChunkedMap
    meta: Dict[str, Any]

class WorldStreamer:
    def __init__(self, registry: Dict[str, Region], current_id: str,
                 tileset: Optional[IsoTileSet2]=None,
                 chunk_spec: ChunkSpec=ChunkSpec(rows=24, cols=24, lru_max=12)):
        self.registry = registry
        self.current_id = current_id
        self.active: Optional[LoadedRegion] = None
        self.next_loaded: Optional[LoadedRegion] = None
        self.tileset = tileset or IsoTileSet2()
        self.chunk_spec = chunk_spec

    def _load_region(self, rid: str) -> LoadedRegion:
        R = self.registry[rid]
        layers = mapgen.generate(side=R.side, rows=R.size[0], cols=R.size[1], seed=R.seed)
        cmap = IsoChunkedMap(layers, self.tileset, origin=R.origin, spec=self.chunk_spec)
        rows, cols = R.size
        gate_r0, gate_r1 = (rows//2 - 2, rows//2 + 2)
        meta = {
            'gate_east': {'rc_range': ((gate_r0, gate_r1), (cols - 10, cols - 2))}
        }
        if 'W' in R.neighbors:
            meta['gate_west'] = {'rc_range': ((gate_r0, gate_r1), (2, 8))}
        return LoadedRegion(R, cmap, meta)

    def ensure_loaded(self):
        if not self.active:
            print('[WS] ensure_loaded ->', self.current_id)
            self.active = self._load_region(self.current_id)

    def update(self, player_rc: Tuple[int,int]):
        if not self.active:
            return None
        r, c = player_rc
        rows, cols = self.active.region.size
        # EAST gate
        gateE = self.active.meta.get('gate_east')
        if gateE:
            (gr0, gr1), (gc0, gc1) = gateE['rc_range']
            if c >= gc0 - 8 and self.next_loaded is None:
                nxt = self.active.region.neighbors.get('E')
                if nxt and nxt in self.registry:
                    print('[WS] preloading ->', nxt)
                    self.next_loaded = self._load_region(nxt)
            if gc0 <= c <= gc1 and gr0 <= r <= gr1 and self.next_loaded:
                print('[WS] handoff E ->', self.next_loaded.region.id)
                self.active = self.next_loaded
                self.current_id = self.active.region.id
                self.next_loaded = None
                new_r = min(max(r, 1), self.active.region.size[0]-2)
                new_c = 1
                return (new_r, new_c)  # MIN-COMPAT: return only (r,c)
        # WEST gate
        gateW = self.active.meta.get('gate_west')
        if gateW:
            (gr0, gr1), (gc0, gc1) = gateW['rc_range']
            if c <= gc1 + 8 and self.next_loaded is None:
                nxt = self.active.region.neighbors.get('W')
                if nxt and nxt in self.registry:
                    print('[WS] preloading ->', nxt)
                    self.next_loaded = self._load_region(nxt)
            if gc0 <= c <= gc1 and gr0 <= r <= gr1 and self.next_loaded:
                print('[WS] handoff W ->', self.next_loaded.region.id)
                self.active = self.next_loaded
                self.current_id = self.active.region.id
                self.next_loaded = None
                new_r = min(max(r, 1), self.active.region.size[0]-2)
                new_c = self.active.region.size[1]-2
                return (new_r, new_c)  # MIN-COMPAT
        return None
