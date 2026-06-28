"""Sprint 15 — dashboard OBD2 via adaptador ELM327.

REQUER HARDWARE: adaptador ELM327 (BT/USB) + lib `obd`. Sem isso,
`get_data()` devolve `available=False` e valores a None — o frontend
mostra um ecrã "sem ligação".
"""

from __future__ import annotations

_EMPTY = {"available": False, "rpm": None, "speed": None, "coolant": None, "fuel": None}


class OBDService:
    def __init__(self) -> None:
        self._conn = None

    def _connect(self):
        import obd  # type: ignore
        if self._conn is None or not self._conn.is_connected():
            self._conn = obd.OBD()  # autodeteta porta
        return self._conn

    def get_data(self) -> dict:
        try:
            import obd  # type: ignore
        except Exception:
            return dict(_EMPTY)
        try:
            conn = self._connect()

            def q(cmd):
                r = conn.query(cmd)
                return None if r.is_null() else float(r.value.magnitude)

            return {
                "available": conn.is_connected(),
                "rpm": q(obd.commands.RPM),
                "speed": q(obd.commands.SPEED),
                "coolant": q(obd.commands.COOLANT_TEMP),
                "fuel": q(obd.commands.FUEL_LEVEL),
            }
        except Exception as e:
            return {**_EMPTY, "error": str(e)}
