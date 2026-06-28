"""Sprint 12 — fontes de áudio e estado de chamada (HFP).

- Fontes (bluetooth/aux/usb): a seleção é guardada e, no Pi, comutaria o
  loopback/sink do PulseAudio. A comutação real é marcada com TODO porque
  depende do setup de áudio do carro.
- Chamadas (HFP): expostas como interface; o estado real precisa de
  BlueZ/oFono + telemóvel ligado — por agora devolve "sem chamada".
"""

from __future__ import annotations

SOURCES = ("bluetooth", "aux", "usb")


class AudioService:
    def __init__(self) -> None:
        self._source = "bluetooth"

    def get_source(self) -> dict:
        return {"source": self._source, "available_sources": list(SOURCES)}

    def set_source(self, source: str) -> dict:
        if source not in SOURCES:
            return {"status": "error", "error": "fonte inválida"}
        self._source = source
        # TODO(hardware): comutar o sink/loopback do PulseAudio conforme a
        # fonte (ex.: `pactl load-module module-loopback` para o AUX).
        return {"status": "ok", "source": source}

    def call_state(self) -> dict:
        # TODO(hardware): ler estado HFP via BlueZ/oFono (org.ofono.VoiceCall).
        return {"active": False, "number": None}
