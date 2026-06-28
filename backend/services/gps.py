"""Sprint 16 — posição GPS via gpsd.

REQUER HARDWARE: recetor GPS + daemon `gpsd` + lib `gpsd-py3` (`import gpsd`).
Sem isso devolve `available=False`. A navegação com mapas offline precisa
ainda de tiles (mbtiles) que são um asset à parte — ver FEATURE-PLAN.md.
"""

from __future__ import annotations

_EMPTY = {"available": False, "fix": False, "lat": None, "lon": None, "speed": None}


class GPSService:
    def get_position(self) -> dict:
        try:
            import gpsd  # type: ignore
        except Exception:
            return dict(_EMPTY)
        try:
            gpsd.connect()
            p = gpsd.get_current()
            if p.mode < 2:  # sem fix 2D/3D
                return {**_EMPTY, "available": True}
            return {
                "available": True,
                "fix": True,
                "lat": p.lat,
                "lon": p.lon,
                "speed": getattr(p, "hspeed", None),
            }
        except Exception as e:
            return {**_EMPTY, "error": str(e)}
