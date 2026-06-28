"""Sprint 18 — assistente de voz.

A wake word e o STT (Whisper/Vosk) precisam de microfone e modelos, por
isso ficam como dependência opcional/lazy. O que é *puro e testável* é o
`parse_intent`: mapeia uma frase já transcrita para uma ação que os
serviços existentes sabem executar.
"""

from __future__ import annotations

import re

_NEXT = ("próxima", "proxima", "next", "seguinte", "avança", "avanca", "salta")
_PREV = ("anterior", "previous", "volta atrás", "volta atras", "retrocede")
_PAUSE = ("pausa", "pause", "para", "stop")
_PLAY = ("toca", "play", "retoma", "continua")


def parse_intent(text: str) -> dict:
    """Frase (já transcrita) → intenção. Função pura, testada."""
    t = (text or "").lower().strip()
    if not t:
        return {"action": "none"}

    m = re.search(r"volume\s+(\d{1,3})", t)
    if m:
        return {"action": "volume", "level": max(0, min(100, int(m.group(1))))}
    if "volume" in t and any(w in t for w in ("aumenta", "sobe", "mais")):
        return {"action": "volume_up"}
    if "volume" in t and any(w in t for w in ("baixa", "diminui", "menos")):
        return {"action": "volume_down"}

    # Ordem importa: "para" (stop) vs "próxima" — testamos play/pause depois
    # do volume e antes do resto.
    if any(w in t for w in _NEXT):
        return {"action": "next"}
    if any(w in t for w in _PREV):
        return {"action": "prev"}
    if any(w in t for w in _PAUSE):
        return {"action": "pause"}
    if any(w in t for w in _PLAY):
        return {"action": "play"}
    return {"action": "unknown", "text": t}


class VoiceService:
    def handle(self, text: str) -> dict:
        return parse_intent(text)

    def available(self) -> bool:
        """True se há stack de STT instalado (wake word + reconhecimento)."""
        try:
            import vosk  # type: ignore  # noqa: F401
            return True
        except Exception:
            return False
